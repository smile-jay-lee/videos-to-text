"""
Flask路由定义 - API for React Frontend
"""
import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_cors import CORS
from werkzeug.utils import secure_filename
from services import TranscriptionService, TextService
from utils.validators import validate_file, get_secure_filename
from utils.file_handler import ensure_dir, cleanup_file
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 启用CORS
CORS(api_bp)

# 全局任务存储（生产环境应使用Redis等）
tasks = {}


@api_bp.route('/transcribe', methods=['POST'])
def transcribe():
    """转录视频/音频文件"""
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '未选择文件'}), 400
        
        file = request.files['file']
        model = request.form.get('model', current_app.config.get('WHISPER_MODEL', 'base'))
        use_ai = request.form.get('use_ai', 'false').lower() == 'true'
        
        # 验证文件
        is_valid, error_msg = validate_file(file)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 保存文件
        task_id = str(uuid.uuid4())
        filename = get_secure_filename(file.filename)
        
        task_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], task_id)
        ensure_dir(task_dir)
        
        file_path = os.path.join(task_dir, filename)
        file.save(file_path)
        
        logger.info(f"开始处理: {task_id} - {filename} (model: {model}, AI: {use_ai})")
        
        # 创建转录服务
        transcription_service = TranscriptionService(model_size=model)
        
        # 执行转录
        result = transcription_service.transcribe_file(file_path)
        
        transcription_text = result.get('text', '')
        
        # 保存转录结果
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        ensure_dir(output_dir)
        
        txt_path = os.path.join(output_dir, f'{filename}_transcription.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcription_text)
        
        response_data = {
            'success': True,
            'task_id': task_id,
            'filename': filename,
            'transcription': transcription_text,
            'model': model,
            'duration': result.get('duration'),
            'output_files': [f'{filename}_transcription.txt']
        }
        
        # AI处理
        if use_ai and transcription_text:
            try:
                text_service = TextService()
                
                # AI润色
                polished_text = text_service.polish_text(transcription_text)
                if polished_text:
                    polished_path = os.path.join(output_dir, f'{filename}_polished.txt')
                    with open(polished_path, 'w', encoding='utf-8') as f:
                        f.write(polished_text)
                    response_data['polished_text'] = polished_text
                    response_data['output_files'].append(f'{filename}_polished.txt')
                
                # AI摘要
                summary = text_service.summarize_text(transcription_text)
                if summary:
                    summary_path = os.path.join(output_dir, f'{filename}_summary.txt')
                    with open(summary_path, 'w', encoding='utf-8') as f:
                        f.write(summary)
                    response_data['summary'] = summary
                    response_data['output_files'].append(f'{filename}_summary.txt')
                    
            except Exception as ai_error:
                logger.warning(f"AI处理失败: {str(ai_error)}")
                response_data['ai_warning'] = f'AI处理失败: {str(ai_error)}'
        
        # 清理上传的文件
        try:
            cleanup_file(file_path)
        except:
            pass
        
        logger.info(f"处理完成: {task_id}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"转录失败: {str(e)}", exc_info=True)
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@api_bp.route('/download/<task_id>/<filename>')
def download_file(task_id, filename):
    """下载输出文件"""
    try:
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"下载失败: {str(e)}")
        return jsonify({'error': '下载失败'}), 500


@api_bp.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'videos-to-text-api'
    })
