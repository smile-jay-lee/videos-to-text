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
from services import get_cached_transcription_service, TextService
from services.transcription_service import TranscriptionService
from services.gemini_service import get_gemini_service
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
        model = request.form.get('model', current_app.config.get('WHISPER_MODEL', 'medium'))
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
        
        # 获取进程级常驻转录服务（按模型复用）
        transcription_service = get_cached_transcription_service(model_size=model)
        
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
                # 使用 Gemini 优化转录文案
                gemini_service = get_gemini_service()
                gemini_result = gemini_service.polish_transcription(transcription_text)
                
                if gemini_result.get('success'):
                    polished_text = gemini_result['polished_text']
                    polished_path = os.path.join(output_dir, f'{filename}_polished.txt')
                    with open(polished_path, 'w', encoding='utf-8') as f:
                        f.write(polished_text)
                    response_data['polished_text'] = polished_text
                    response_data['output_files'].append(f'{filename}_polished.txt')
                    logger.info(f"Gemini 优化完成: {len(transcription_text)} -> {len(polished_text)} chars")
                else:
                    logger.warning(f"Gemini 优化失败: {gemini_result.get('error', 'Unknown error')}")
                    response_data['ai_warning'] = f"Gemini 优化失败: {gemini_result.get('error', 'Unknown error')}"
                    
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


# ─────────────────────────────────────────────────────────────────────────────
# Bilibili 相关接口
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route('/bili/info')
def get_bili_info():
    """获取 B 站视频元数据（仅解析，不下载）"""
    url = request.args.get('url', '').strip()
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400

    try:
        from services.bili_service import BiliAudioService
        service = BiliAudioService()
        info = service.get_video_info(url)

        if info is None:
            return jsonify({'error': '无法解析链接，请检查 BV 号或链接是否正确，以及视频是否公开'}), 400

        return jsonify({'success': True, **info})

    except Exception as e:
        logger.error(f"获取B站视频信息失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/transcribe-url', methods=['POST'])
def transcribe_url():
    """通过 B 站链接下载音频并转录"""
    import shutil

    try:
        data = request.get_json(silent=True) or {}
        url      = data.get('url', '').strip()
        model    = data.get('model', current_app.config.get('WHISPER_MODEL', 'medium'))
        use_ai   = bool(data.get('use_ai', False))
        page_num = data.get('page_num', None)   # None → 第 1 P

        if not url:
            return jsonify({'error': '缺少 url 参数'}), 400

        task_id  = str(uuid.uuid4())
        temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], task_id)
        ensure_dir(temp_dir)

        audio_path = None
        try:
            # 1. 下载音频到临时目录
            from services.bili_service import BiliAudioService
            bili = BiliAudioService(output_dir=temp_dir)
            audio_path = bili.download_audio(url, page_num=page_num)

            if not audio_path:
                return jsonify({'error': '音频下载失败，视频可能不存在、已删除或需要登录'}), 400

            display_name = os.path.splitext(os.path.basename(audio_path))[0]

            # 2. 转录
            transcription_service = TranscriptionService(model_size=model)
            result = transcription_service.transcribe_file(audio_path, language='zh')
            transcription_text = result.get('text', '')

            # 3. 持久化结果
            output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], task_id)
            ensure_dir(output_dir)

            txt_path = os.path.join(output_dir, f'{display_name}_transcription.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(transcription_text)

            metadata = {
                'task_id':     task_id,
                'filename':    display_name,
                'source_type': 'bili_url',
                'source_url':  url,
                'model':       model,
                'duration':    result.get('duration'),
                'created_at':  datetime.now().isoformat(),
                'file_size':   os.path.getsize(txt_path),
                'text_length': len(transcription_text),
                'use_ai':      use_ai,
            }
            save_task_metadata(task_id, metadata)

            response_data = {
                'success':       True,
                'task_id':       task_id,
                'filename':      display_name,
                'transcription': transcription_text,
                'model':         model,
                'duration':      result.get('duration'),
                'output_files':  [os.path.basename(txt_path)],
            }

            # 4. AI 润色（可选）
            if use_ai and transcription_text:
                try:
                    gemini_service = get_gemini_service()
                    gemini_result = gemini_service.polish_transcription(transcription_text)
                    if gemini_result.get('success'):
                        polished_text = gemini_result['polished_text']
                        polished_path = os.path.join(output_dir, f'{display_name}_polished.txt')
                        with open(polished_path, 'w', encoding='utf-8') as f:
                            f.write(polished_text)
                        response_data['polished_text'] = polished_text
                        response_data['output_files'].append(os.path.basename(polished_path))
                except Exception as ai_err:
                    logger.warning(f"AI处理失败: {ai_err}")
                    response_data['ai_warning'] = f'AI处理失败: {ai_err}'

            logger.info(f"URL转录完成: {task_id}")
            return jsonify(response_data)

        finally:
            # 5. 清理临时音频和上传目录（无论成功与否）
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    logger.info(f"已清理临时音频: {audio_path}")
                except Exception:
                    pass
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"URL转录失败: {str(e)}", exc_info=True)
        return jsonify({'error': f'处理失败: {str(e)}'}), 500
