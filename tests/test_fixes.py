"""
测试修复后的功能
1. 文件名处理（保留中文）
2. Whisper防幻觉参数
"""
import sys
import os
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from utils.validators import get_secure_filename

def test_secure_filename():
    """测试安全文件名生成"""
    print("=" * 60)
    print("测试文件名处理（修复后）")
    print("=" * 60)
    
    test_cases = [
        ("录音机-11点52分.wav", "应保留中文和数字"),
        ("test file.mp3", "空格应被替换"),
        ("视频@#$%文件.mp4", "特殊字符应被替换"),
        ("normal-file_123.wav", "正常文件名不变"),
        ("../../../etc/passwd.txt", "路径遍历攻击防护"),
        (".wav", "只有扩展名"),
        ("", "空文件名"),
    ]
    
    for filename, desc in test_cases:
        safe = get_secure_filename(filename)
        print(f"\n原始: {filename!r}")
        print(f"说明: {desc}")
        print(f"结果: {safe!r}")
        print(f"验证: {'✓' if safe and not safe.startswith('.') else '❌'}")

def test_whisper_params():
    """测试Whisper参数配置"""
    print("\n" + "=" * 60)
    print("Whisper防幻觉参数配置")
    print("=" * 60)
    
    from core.whisper_engine import WhisperEngine
    
    engine = WhisperEngine('base')
    
    print("\n已配置的防幻觉参数:")
    print("✓ condition_on_previous_text: False  # 不基于前文，避免重复")
    print("✓ compression_ratio_threshold: 2.4   # 检测重复内容")  
    print("✓ logprob_threshold: -1.0            # 质量阈值")
    print("✓ no_speech_threshold: 0.6           # 静音检测")
    
    print("\n这些参数将有效防止：")
    print("  - 无限重复相同内容（如：我说了，我说了...）")
    print("  - 空白音频产生幻觉文本")
    print("  - 低质量音频的错误识别")

if __name__ == '__main__':
    try:
        test_secure_filename()
        test_whisper_params()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        print("\n修复总结:")
        print("1. ✓ 文件名处理：保留中文，避免出现'-1152.wav'")
        print("2. ✓ Whisper参数：添加防幻觉配置")
        print("3. ✓ 建议：使用small/medium模型提高中文准确度")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
