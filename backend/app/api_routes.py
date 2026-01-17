"""
Flask路由定义 - API for React Frontend
"""
import os
import uuid
import json
from datetime import datetime
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


def save_task_metadata(task_id, data):
    """保存任务元数据"""
    try:
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        ensure_dir(output_dir)
        
        metadata_path = os.path.join(output_dir, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存元数据失败: {str(e)}")


def load_task_metadata(task_id):
    """加载任务元数据"""
    try:
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        metadata_path = os.path.join(output_dir, 'metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载元数据失败: {str(e)}")
    
    return None


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
        
        # 执行转录（明确指定中文）
        result = transcription_service.transcribe_file(file_path, language='zh')
        
        transcription_text = result.get('text', '')
        
        # 保存转录结果
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        ensure_dir(output_dir)
        
        txt_path = os.path.join(output_dir, f'{filename}_transcription.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcription_text)
        
        # 保存元数据
        metadata = {
            'task_id': task_id,
            'filename': filename,
            'model': model,
            'duration': result.get('duration'),
            'created_at': datetime.now().isoformat(),
            'file_size': os.path.getsize(txt_path),
            'text_length': len(transcription_text),
            'use_ai': use_ai
        }
        save_task_metadata(task_id, metadata)
        
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

@api_bp.route('/history')
def get_history():
    """获取历史记录列表"""
    try:
        output_folder = current_app.config['OUTPUT_FOLDER']
        history = []
        
        # 遍历输出目录
        if os.path.exists(output_folder):
            for task_id in os.listdir(output_folder):
                task_dir = os.path.join(output_folder, task_id)
                
                # 跳过非目录文件
                if not os.path.isdir(task_dir):
                    continue
                
                # 加载元数据
                metadata = load_task_metadata(task_id)
                
                if metadata:
                    history.append(metadata)
                else:
                    # 如果没有元数据，尝试从文件系统推断
                    files = [f for f in os.listdir(task_dir) if f.endswith('.txt')]
                    if files:
                        main_file = files[0]
                        file_path = os.path.join(task_dir, main_file)
                        stat = os.stat(file_path)
                        
                        history.append({
                            'task_id': task_id,
                            'filename': main_file.replace('_transcription.txt', ''),
                            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'file_size': stat.st_size,
                            'model': 'unknown'
                        })
        
        # 按时间倒序排序
        history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        })
        
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        return jsonify({'error': '获取历史记录失败'}), 500


@api_bp.route('/history/<task_id>')
def get_history_detail(task_id):
    """获取历史记录详情"""
    try:
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        
        if not os.path.exists(output_dir):
            return jsonify({'error': '记录不存在'}), 404
        
        # 加载元数据
        metadata = load_task_metadata(task_id)
        
        # 读取转录文本
        transcription = None
        polished_text = None
        summary = None
        
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            
            if filename.endswith('_transcription.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    transcription = f.read()
            elif filename.endswith('_polished.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    polished_text = f.read()
            elif filename.endswith('_summary.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    summary = f.read()
        
        result = {
            'success': True,
            'task_id': task_id,
            'metadata': metadata,
            'transcription': transcription,
            'polished_text': polished_text,
            'summary': summary
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取详情失败: {str(e)}")
        return jsonify({'error': '获取详情失败'}), 500


@api_bp.route('/history/<task_id>', methods=['DELETE'])
def delete_history(task_id):
    """删除历史记录"""
    try:
        import shutil
        
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
        
        if not os.path.exists(output_dir):
            return jsonify({'error': '记录不存在'}), 404
        
        # 删除目录及所有文件
        shutil.rmtree(output_dir)
        
        logger.info(f"已删除历史记录: {task_id}")
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除失败: {str(e)}")
        return jsonify({'error': '删除失败'}), 500