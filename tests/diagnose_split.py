"""诊断音频切割问题"""
import os
import sys

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from pydub import AudioSegment
import math

def test_audio_split(audio_path):
    """测试音频切割"""
    print(f"=== 测试音频切割: {os.path.basename(audio_path)} ===\n")
    
    if not os.path.exists(audio_path):
        print(f"❌ 文件不存在: {audio_path}")
        return
    
    try:
        # 读取原始音频
        print("1. 读取原始音频...")
        audio = AudioSegment.from_file(audio_path)
        print(f"   ✓ 时长: {len(audio)/1000:.2f}秒")
        print(f"   ✓ 声道: {audio.channels}")
        print(f"   ✓ 采样率: {audio.frame_rate}Hz")
        print(f"   ✓ 音量峰值: {audio.max_dBFS:.2f}dBFS")
        
        # 检查是否为静音
        if audio.max_dBFS < -50:
            print(f"   ⚠ 警告: 音频音量过低，可能是静音!")
        
        # 切割测试 (前30秒)
        print("\n2. 测试切割前30秒...")
        chunk_duration_ms = 30 * 1000
        num_chunks = math.ceil(len(audio) / chunk_duration_ms)
        
        base_name = os.path.splitext(audio_path)[0]
        output_dir = os.path.dirname(audio_path)
        
        for i in range(min(3, num_chunks)):  # 只测试前3段
            start_ms = i * chunk_duration_ms
            end_ms = min((i+1) * chunk_duration_ms, len(audio))
            
            print(f"\n   切割段 {i}: {start_ms}ms - {end_ms}ms")
            chunk = audio[start_ms:end_ms]
            
            print(f"   - 时长: {len(chunk)/1000:.2f}秒")
            print(f"   - 声道: {chunk.channels}")
            print(f"   - 采样率: {chunk.frame_rate}Hz")
            print(f"   - 音量峰值: {chunk.max_dBFS:.2f}dBFS")
            
            if chunk.max_dBFS < -50:
                print(f"   ❌ 该片段音量过低或为静音!")
            else:
                print(f"   ✓ 该片段有有效音频")
            
            # 导出测试
            chunk_path = os.path.join(output_dir, f"test_chunk_{i}.mp3")
            chunk.export(chunk_path, format="mp3")
            
            # 验证导出的文件
            exported_size = os.path.getsize(chunk_path)
            print(f"   - 导出文件大小: {exported_size/1024:.2f}KB")
            
            if exported_size < 1024:
                print(f"   ⚠ 导出文件过小，可能有问题!")
            
            # 重新读取验证
            try:
                verify_chunk = AudioSegment.from_file(chunk_path)
                print(f"   - 重新读取验证: ✓ 时长{len(verify_chunk)/1000:.2f}秒")
                print(f"   - 验证音量: {verify_chunk.max_dBFS:.2f}dBFS")
            except Exception as e:
                print(f"   ❌ 重新读取失败: {e}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

# 测试文件
test_files = [
    r"D:\project\videos to text\frontend\static\uploads\621dbf1d-af55-4114-a7e1-99f3cfe5facf\test_segment_30s.wav",
]

# 查找其他可能的测试文件
uploads_dir = r"D:\project\videos to text\frontend\static\uploads"
if os.path.exists(uploads_dir):
    for root, dirs, files in os.walk(uploads_dir):
        for file in files:
            if file.endswith(('.wav', '.mp3')) and '录音机' in file:
                test_files.append(os.path.join(root, file))
                break

print(f"找到 {len(test_files)} 个测试文件\n")

for audio_file in test_files:
    if os.path.exists(audio_file):
        test_audio_split(audio_file)
        print("\n" + "="*80 + "\n")
