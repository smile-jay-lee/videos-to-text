"""测试修复后的音频切割功能"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from pydub import AudioSegment
from pydub.generators import Sine
from core.audio_extractor import AudioExtractor

print("=== 测试音频切割修复 ===\n")

# 1. 创建测试音频（5秒，440Hz正弦波）
print("1. 创建测试音频（5秒，440Hz）...")
test_audio = Sine(440).to_audio_segment(duration=5000)  # 5秒
test_audio = test_audio.set_channels(2)  # 双声道
test_audio = test_audio.set_frame_rate(44100)  # 标准采样率

# 保存测试音频
test_dir = os.path.dirname(__file__)
test_file = os.path.join(test_dir, "test_split_input.mp3")
test_audio.export(test_file, format="mp3", bitrate="192k")
print(f"   ✓ 测试音频已创建: {test_file}")
print(f"   - 时长: {len(test_audio)/1000:.2f}秒")
print(f"   - 音量: {test_audio.max_dBFS:.2f}dBFS")

# 2. 测试切割
print("\n2. 测试切割功能（每2秒一段）...")
extractor = AudioExtractor()

try:
    chunks = extractor.split_audio(test_file, chunk_duration_ms=2000)  # 每2秒一段
    print(f"   ✓ 成功切割为 {len(chunks)} 段")
    
    # 3. 验证每个片段
    print("\n3. 验证切割片段:")
    all_valid = True
    
    for i, chunk_path in enumerate(chunks):
        if not os.path.exists(chunk_path):
            print(f"   ❌ 片段{i}不存在: {chunk_path}")
            all_valid = False
            continue
        
        # 读取片段
        chunk_audio = AudioSegment.from_file(chunk_path)
        file_size_kb = os.path.getsize(chunk_path) / 1024
        
        print(f"\n   片段 {i}:")
        print(f"   - 文件大小: {file_size_kb:.2f}KB")
        print(f"   - 时长: {len(chunk_audio)/1000:.2f}秒")
        print(f"   - 声道: {chunk_audio.channels}")
        print(f"   - 采样率: {chunk_audio.frame_rate}Hz")
        print(f"   - 音量峰值: {chunk_audio.max_dBFS:.2f}dBFS")
        
        # 检查问题
        if file_size_kb < 5:
            print(f"   ⚠ 警告: 文件过小")
            all_valid = False
        if chunk_audio.max_dBFS < -50:
            print(f"   ❌ 错误: 音频为静音或音量过低!")
            all_valid = False
        if len(chunk_audio) < 100:  # 少于0.1秒
            print(f"   ⚠ 警告: 时长过短")
            all_valid = False
        if chunk_audio.max_dBFS >= -20:
            print(f"   ✓ 音频有效")
    
    # 4. 清理测试文件
    print("\n4. 清理测试文件...")
    os.remove(test_file)
    for chunk_path in chunks:
        if os.path.exists(chunk_path):
            os.remove(chunk_path)
    print("   ✓ 已清理")
    
    # 结果
    print(f"\n{'='*50}")
    if all_valid:
        print("✓✓✓ 所有测试通过！音频切割功能正常")
    else:
        print("❌❌❌ 测试失败！存在问题")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
