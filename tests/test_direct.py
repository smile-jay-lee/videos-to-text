"""直接测试修复后的代码"""
import os
import sys

# 添加后端目录到路径
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from utils.validators import get_secure_filename
from core.whisper_engine import WhisperEngine

print("=== 测试1: 文件名保留中文 ===")
test_filenames = [
    "录音机-11点52分.wav",
    "测试音频-下午3点.mp3",
    "Meeting Notes 2024.wav",
    "视频转文字_final.mp4"
]

for filename in test_filenames:
    result = get_secure_filename(filename)
    status = "✓" if "录音机" in result or "测试音频" in result or "视频转文字" in result else "⚠"
    print(f"{status} '{filename}' -> '{result}'")

print("\n=== 测试2: Whisper防幻觉参数 ===")
engine = WhisperEngine()

# 检查配置
print("检查transcribe方法中的选项...")
import inspect
source = inspect.getsource(engine.transcribe)
if 'condition_on_previous_text' in source:
    if "condition_on_previous_text': False" in source or 'condition_on_previous_text": False' in source:
        print("✓ condition_on_previous_text: False (已设置)")
    else:
        print("⚠ condition_on_previous_text 存在但值可能不正确")
else:
    print("❌ condition_on_previous_text 未找到")

if 'compression_ratio_threshold' in source:
    print("✓ compression_ratio_threshold: 已设置")
else:
    print("⚠ compression_ratio_threshold 未设置")

if 'logprob_threshold' in source:
    print("✓ logprob_threshold: 已设置")
else:
    print("⚠ logprob_threshold 未设置")

if 'no_speech_threshold' in source:
    print("✓ no_speech_threshold: 已设置")
else:
    print("⚠ no_speech_threshold 未设置")

print("\n=== 测试3: 实际转录30秒音频 ===")
test_audio = r"D:\project\videos to text\frontend\static\uploads\621dbf1d-af55-4114-a7e1-99f3cfe5facf\test_segment_30s.wav"

if os.path.exists(test_audio):
    print(f"加载模型...")
    model = engine.load_model('base')
    print(f"✓ 模型加载成功")
    
    print(f"转录音频...")
    result = engine.transcribe(test_audio, 'zh')
    text = result.get('text', '')
    
    print(f"\n转录结果长度: {len(text)} 字符")
    print(f"前100字符: {text[:100]}")
    
    # 检查重复
    if len(text) > 50:
        sample = text[:20]
        count = text.count(sample[:10])
        if count > 10:
            print(f"⚠ 可能存在重复内容 ('{sample[:10]}' 出现 {count} 次)")
        else:
            print(f"✓ 无明显重复内容")
else:
    print(f"❌ 测试文件不存在: {test_audio}")

print("\n=== 所有测试完成 ===")
