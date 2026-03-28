"""
Flask路由定义
"""
import os
import uuid
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from services import get_cached_transcription_service, TextService
from utils.validators import validate_file, get_secure_filename
from utils.file_handler import ensure_dir, cleanup_file
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建蓝图
bp = Blueprint('main', __name__)

# 全局任务存储（生产环境应使用Redis等）
tasks = {}


@bp.route('/')
def index():
    """主页"""
    return render_template('index.html')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """上传页面"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    # POST - 处理文件上传
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未选择文件'}), 400
        
        file = request.files['file']
        
        # 验证文件
        is_valid, error_msg = validate_file(file)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # 保存文件
        task_id = str(uuid.uuid4())
        filename = get_secure_filename(file.filename)
        
        task_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], task_id)
        ensure_dir(task_dir)
        
        file_path = os.path.join(task_dir, filename)
        file.save(file_path)
        
        logger.info(f"文件已上传: {task_id} - {filename}")
        
        # 初始化任务
        tasks[task_id] = {
            'status': 'uploaded',
            'progress': 0,
            'message': '文件已上传',
            'file_path': file_path,
            'filename': filename
        }
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'filename': filename,
            'message': '文件上传成功'
        })
        
    except Exception as e:
        logger.error(f"上传失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/transcribe', methods=['POST'])
def transcribe():
    """开始转写任务"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        language = data.get('language', 'zh')
        model = data.get('model', current_app.config['WHISPER_MODEL'])
        
        if not task_id or task_id not in tasks:
            return jsonify({'success': False, 'error': '无效的任务ID'}), 400
        
        task = tasks[task_id]
        file_path = task['file_path']
        
        # 更新任务状态
        task['status'] = 'processing'
        task['message'] = '开始处理...'
        
        logger.info(f"开始转写任务: {task_id}")
        
        # 获取进程级常驻转写服务（按模型复用）
        service = get_cached_transcription_service(model_size=model)
        
        # 定义进度回调
        def update_progress(tid, progress, message):
            if tid in tasks:
                tasks[tid]['progress'] = progress
                tasks[tid]['message'] = message
                if progress < 0:
                    tasks[tid]['status'] = 'failed'
                elif progress >= 100:
                    tasks[tid]['status'] = 'completed'
        
        # 执行转写（这里应该用异步任务，暂时同步）
        result = service.transcribe_file(
            file_path,
            language=language,
            task_id=task_id,
            progress_callback=update_progress
        )
        
        # 保存结果
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        ensure_dir(output_dir)
        
        txt_path = os.path.join(output_dir, 'transcription.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        task['result'] = result
        task['txt_file'] = txt_path
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '转写完成'
        })
        
    except Exception as e:
        logger.error(f"转写失败: {str(e)}")
        if task_id and task_id in tasks:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['message'] = f'转写失败: {str(e)}'
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/task/<task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    return jsonify({
        'success': True,
        'task_id': task_id,
        'status': task['status'],
        'progress': task.get('progress', 0),
        'message': task.get('message', '')
    })


@bp.route('/api/result/<task_id>')
def get_result(task_id):
    """获取转写结果"""
    if task_id not in tasks:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    
    if task['status'] != 'completed':
        return jsonify({
            'success': False,
            'error': '任务尚未完成'
        }), 400
    
    result = task.get('result', {})
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'text': result.get('text', ''),
        'download_links': {
            'txt': f'/api/download/{task_id}/txt'
        }
    })


@bp.route('/api/download/<task_id>/<file_type>')
def download_file(task_id, file_type):
    """下载文件"""
    if task_id not in tasks:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    
    if file_type == 'txt':
        file_path = task.get('txt_file')
        if file_path and os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f'transcription_{task_id}.txt'
            )
    
    return jsonify({'success': False, 'error': '文件不存在'}), 404


@bp.route('/result/<task_id>')
def result_page(task_id):
    """结果页面"""
    if task_id not in tasks:
        return render_template('error.html', error='任务不存在'), 404
    
    task = tasks[task_id]
    result = task.get('result', {})
    
    return render_template('result.html', task_id=task_id, task=task, result=result)
