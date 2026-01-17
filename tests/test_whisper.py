"""
测试Whisper引擎功能
使用base模型测试音频转录
"""
import sys
import os
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from core.whisper_engine import WhisperEngine
from core.audio_extractor import AudioExtractor
import time

def test_audio_transcription():
    """测试音频转录功能"""
    
    print("=" * 60)
    print("Whisper 引擎功能测试")
    print("=" * 60)
    
    # 1. 准备测试音频
    history_dir = Path(__file__).parent.parent / 'history'
    test_audio = history_dir / 'extracted_audio.wav'
    
    if not test_audio.exists():
        test_audio = history_dir / '社会学_audio.mp3'
    
    if not test_audio.exists():
        print("❌ 未找到测试音频文件")
        return
    
    print(f"\n✓ 测试音频: {test_audio.name}")
    file_size = test_audio.stat().st_size / 1024 / 1024
    print(f"✓ 文件大小: {file_size:.2f} MB")
    
    # 2. 初始化Whisper引擎（使用base模型）
    print("\n" + "=" * 60)
    print("步骤1: 加载Whisper模型")
    print("=" * 60)
    
    start_time = time.time()
    engine = WhisperEngine(model_size='base')
    engine.load_model()
    load_time = time.time() - start_time
    
    print(f"✓ 模型加载完成，耗时: {load_time:.2f}秒")
    
    # 3. 转录音频（只转录前30秒测试）
    print("\n" + "=" * 60)
    print("步骤2: 转录音频（前30秒）")
    print("=" * 60)
    
    # 如果音频太大，先切割一小段
    test_segment = None
    if file_size > 10:
        from pydub import AudioSegment
        print("音频较大，提取前30秒进行测试...")
        
        audio = AudioSegment.from_file(str(test_audio))
        segment = audio[:30000]  # 前30秒
        
        test_segment = Path(__file__).parent / 'test_segment.wav'
        segment.export(str(test_segment), format="wav")
        print(f"✓ 已提取测试片段: {test_segment}")
        audio_to_transcribe = test_segment
    else:
        audio_to_transcribe = test_audio
    
    start_time = time.time()
    result = engine.transcribe(str(audio_to_transcribe), language='zh')
    transcribe_time = time.time() - start_time
    
    print(f"\n✓ 转录完成，耗时: {transcribe_time:.2f}秒")
    
    # 4. 显示结果
    print("\n" + "=" * 60)
    print("转录结果")
    print("=" * 60)
    
    text = result.get('text', '')
    print(f"\n{text}\n")
    
    print("=" * 60)
    print(f"文本长度: {len(text)} 字符")
    print(f"包含片段: {len(result.get('segments', []))} 个")
    
    # 5. 保存结果
    output_file = Path(__file__).parent / 'test_output.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"测试音频: {test_audio.name}\n")
        f.write(f"模型: base\n")
        f.write(f"语言: 中文\n")
        f.write(f"加载时间: {load_time:.2f}秒\n")
        f.write(f"转录时间: {transcribe_time:.2f}秒\n")
        f.write(f"\n{'=' * 60}\n")
        f.write(f"转录文本:\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(text)
        
        # 详细片段信息
        f.write(f"\n\n{'=' * 60}\n")
        f.write(f"详细片段信息:\n")
        f.write(f"{'=' * 60}\n\n")
        for i, seg in enumerate(result.get('segments', []), 1):
            f.write(f"[片段 {i}] {seg['start']:.2f}s - {seg['end']:.2f}s\n")
            f.write(f"{seg['text']}\n\n")
    
    print(f"\n✓ 结果已保存到: {output_file}")
    
    # 清理临时文件
    if test_segment and test_segment.exists():
        test_segment.unlink()
        print(f"✓ 已清理临时文件")
    
    print("\n" + "=" * 60)
    print("✓ 测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_audio_transcription()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
