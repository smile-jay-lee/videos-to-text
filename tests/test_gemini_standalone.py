"""
独立测试 Gemini API（不依赖 Whisper）
"""
import os
import sys

# 直接测试 google.genai
try:
    from google import genai
    from dotenv import load_dotenv
    
    print("=" * 60)
    print("Gemini API 独立测试")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\n✗ 错误：未找到 GEMINI_API_KEY 环境变量")
        sys.exit(1)
    
    print(f"\n✓ API Key 已加载: {api_key[:20]}...")
    
    # 配置并测试
    print("\n1. 配置 Gemini...")
    client = genai.Client(api_key=api_key)
    print("✓ Gemini 客户端初始化成功")
    
    # 测试文本优化
    print("\n2. 测试文案优化...")
    test_text = """
    大家好，今天我们要讲的是关于人工只能的一些基础知识。
    人工只能，也就是 AI，是一种让机器具有只能的技术。
    请问大家有什么问题吗？请问。请问。
    """
    
    print(f"\n原文 ({len(test_text)} 字符):")
    print("-" * 60)
    print(test_text)
    print("-" * 60)
    
    prompt = f"""整理一下文案，可能存在语音识别错误，变成正确文案。

要求：
1. 修正明显的识别错误（如同音字、错别字）
2. 调整标点符号，使文案更通顺
3. 保持原文的语义和风格
4. 不要添加原文没有的内容

原文：
{test_text}

请直接输出优化后的文案，不要添加任何解释或说明。"""
    
    print("\n3. 调用 Gemini API...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    polished = response.text.strip()
    
    print(f"\n✓ 优化完成 ({len(polished)} 字符):")
    print("-" * 60)
    print(polished)
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✓ Gemini API 测试通过！")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n✗ 导入错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
