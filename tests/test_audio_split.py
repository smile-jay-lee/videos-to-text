"""
测试音频分割功能
检查文件名处理和分割逻辑
"""
import sys
import os
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from core.audio_extractor import AudioExtractor
from pydub import AudioSegment

def test_filename_handling():
    """测试文件名处理"""
    print("=" * 60)
    print("测试文件名处理")
    print("=" * 60)
    
    test_cases = [
        "录音机-11点52分.wav",
        "C:/Users/dell/Documents/录音机-11点52分.wav",
        "test-1152.wav",
        "audio_file.mp3"
    ]
    
    for test_path in test_cases:
        base_name = os.path.splitext(test_path)[0]
        print(f"\n原始路径: {test_path}")
        print(f"提取基础名: {base_name}")
        print(f"分块文件名: {base_name}_chunk_0.mp3")

def test_audio_split():
    """测试实际音频分割"""
    print("\n" + "=" * 60)
    print("测试实际音频分割")
    print("=" * 60)
    
    # 查找测试音频
    history_dir = Path(__file__).parent.parent / 'history'
    test_audio = history_dir / 'extracted_audio.wav'
    
    if not test_audio.exists():
        print("❌ 测试音频不存在")
        return
    
    print(f"\n✓ 测试音频: {test_audio}")
    
    # 获取音频信息
    audio = AudioSegment.from_file(str(test_audio))
    duration_sec = len(audio) / 1000
    print(f"✓ 音频时长: {duration_sec:.2f}秒 ({duration_sec/60:.2f}分钟)")
    
    # 模拟分割（不实际创建文件）
    chunk_duration_ms = 10 * 60 * 1000  # 10分钟
    num_chunks = -(-len(audio) // chunk_duration_ms)  # 向上取整
    
    print(f"✓ 将分割为: {num_chunks} 段")
    
    base_name = os.path.splitext(str(test_audio))[0]
    print(f"✓ 基础文件名: {base_name}")
    
    for i in range(num_chunks):
        start_ms = i * chunk_duration_ms
        end_ms = min((i+1) * chunk_duration_ms, len(audio))
        chunk_path = f"{base_name}_chunk_{i}.mp3"
        
        duration = (end_ms - start_ms) / 1000
        print(f"  片段 {i}: {chunk_path}")
        print(f"    时间范围: {start_ms/1000:.1f}s - {end_ms/1000:.1f}s (时长: {duration:.1f}s)")

def check_problematic_file():
    """检查问题文件路径"""
    print("\n" + "=" * 60)
    print("检查问题场景")
    print("=" * 60)
    
    # 模拟微信文件路径
    problematic_path = r"C:\Users\dell\Documents\xwechat_files\wxid_arb7y58rr0d522_1688\msg\file\2026-01\录音机-11点52分.wav"
    
    print(f"\n原始路径: {problematic_path}")
    print(f"文件名: {os.path.basename(problematic_path)}")
    
    base_name = os.path.splitext(problematic_path)[0]
    print(f"提取基础名: {base_name}")
    
    # 检查是否包含中文
    if any('\u4e00' <= char <= '\u9fff' for char in base_name):
        print("✓ 包含中文字符")
    
    # 模拟分块文件名
    for i in range(3):
        chunk_path = f"{base_name}_chunk_{i}.mp3"
        chunk_basename = os.path.basename(chunk_path)
        print(f"\n片段 {i}:")
        print(f"  完整路径: {chunk_path}")
        print(f"  文件名: {chunk_basename}")

if __name__ == '__main__':
    try:
        test_filename_handling()
        test_audio_split()
        check_problematic_file()
        
        print("\n" + "=" * 60)
        print("✓ 测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
