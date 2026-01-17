"""测试small模型是否可用"""
import os
import sys
import time

# 添加backend目录到路径
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from core.whisper_engine import WhisperEngine

def test_small_model():
    """测试small模型加载和转录"""
    
    print("=== 测试Small模型 ===\n")
    
    # 检查模型文件是否存在
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    small_model_path = os.path.join(models_dir, 'small.pt')
    
    print(f"1. 检查模型文件...")
    print(f"   模型目录: {models_dir}")
    
    if os.path.exists(small_model_path):
        size_mb = os.path.getsize(small_model_path) / (1024 * 1024)
        print(f"   ✓ small.pt 存在 ({size_mb:.2f} MB)")
        
        if size_mb < 100:
            print(f"   ⚠ 文件过小，可能损坏 (预期约466MB)")
            return False
    else:
        print(f"   ❌ small.pt 不存在")
        print(f"\n请先下载模型:")
        print(f"   cd backend")
        print(f"   python download_model_reliable.py")
        return False
    
    # 测试加载模型
    print(f"\n2. 加载模型...")
    engine = WhisperEngine(model_size='small')
    
    try:
        start_time = time.time()
        engine.load_model()
        load_time = time.time() - start_time
        
        print(f"   ✓ 模型加载成功 (耗时: {load_time:.2f}秒)")
    except Exception as e:
        print(f"   ❌ 模型加载失败: {e}")
        return False
    
    # 查找测试音频文件
    print(f"\n3. 查找测试音频...")
    
    test_audios = []
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads')
    
    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                if file.endswith(('.wav', '.mp3', '.m4a')):
                    test_audios.append(os.path.join(root, file))
    
    if not test_audios:
        print(f"   ⚠ 未找到测试音频文件")
        print(f"   跳过转录测试")
        return True
    
    # 使用第一个找到的音频文件
    test_audio = test_audios[0]
    audio_size_mb = os.path.getsize(test_audio) / (1024 * 1024)
    print(f"   ✓ 找到测试音频: {os.path.basename(test_audio)} ({audio_size_mb:.2f}MB)")
    
    # 如果文件太大，只转录前30秒
    if audio_size_mb > 5:
        print(f"   ⚠ 文件较大，建议使用小片段测试")
    
    # 测试转录
    print(f"\n4. 测试转录...")
    
    try:
        start_time = time.time()
        result = engine.transcribe(test_audio, 'zh')
        transcribe_time = time.time() - start_time
        
        text = result.get('text', '')
        segments = result.get('segments', [])
        
        print(f"   ✓ 转录成功 (耗时: {transcribe_time:.2f}秒)")
        print(f"   文本长度: {len(text)} 字符")
        print(f"   分段数量: {len(segments)}")
        
        # 显示前200字符
        if text:
            print(f"\n   转录结果预览:")
            print(f"   {text[:200]}")
            
            # 检查重复内容
            if len(text) > 100:
                sample = text[:20]
                count = text.count(sample[:10])
                if count > 10:
                    print(f"\n   ⚠ 检测到重复内容 ('{sample[:10]}' 出现 {count} 次)")
                    print(f"   可能存在幻觉问题")
                else:
                    print(f"\n   ✓ 未检测到明显重复内容")
        else:
            print(f"   ⚠ 转录结果为空")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 转录失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_model_quality():
    """比较base和small模型的质量（如果都可用）"""
    
    print(f"\n\n=== 模型对比分析 ===")
    
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    
    print(f"\n可用模型:")
    for model_name in ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']:
        model_path = os.path.join(models_dir, f'{model_name}.pt')
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"  ✓ {model_name:12s} ({size_mb:6.2f} MB)")
    
    print(f"\n建议:")
    print(f"  • tiny/base:  适合快速测试，中文识别率较低 (⭐⭐)")
    print(f"  • small:      中文识别率中等，速度较快 (⭐⭐⭐)")
    print(f"  • medium:     中文识别率高，生产环境推荐 (⭐⭐⭐⭐)")
    print(f"  • large:      最高识别率，但速度慢 (⭐⭐⭐⭐⭐)")

if __name__ == "__main__":
    success = test_small_model()
    compare_model_quality()
    
    if success:
        print(f"\n✓ Small模型测试通过!")
    else:
        print(f"\n✗ Small模型测试失败")
        sys.exit(1)
