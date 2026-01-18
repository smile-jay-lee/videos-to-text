"""
测试 Gemini API 集成
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.gemini_service import GeminiService


def test_gemini_basic():
    """测试基础功能"""
    print("=" * 60)
    print("测试 Gemini API 基础功能")
    print("=" * 60)
    
    # 模拟语音识别错误的文本
    test_text = """
    大家好，欢迎来到今天的技术讲座。
    今天我们要讲的是关于人工只能的一些基础知识。
    人工只能，也就是 AI，是一种让机器具有只能的技术。
    通过机器学习和深度学习，我们可以让计算机识别图像、理解语言、做出决策。
    请问大家有什么问题吗？请问。请问。
    """
    
    try:
        # 初始化服务
        print("\n1. 初始化 Gemini 服务...")
        gemini = GeminiService()
        print("✓ 初始化成功")
        
        # 测试文案优化
        print("\n2. 测试文案优化...")
        print(f"\n原始文本 ({len(test_text)} 字符):")
        print("-" * 60)
        print(test_text)
        print("-" * 60)
        
        result = gemini.polish_transcription(test_text)
        
        if result['success']:
            print("\n✓ 优化成功")
            print(f"\n优化后文本 ({result['polished_length']} 字符):")
            print("-" * 60)
            print(result['polished_text'])
            print("-" * 60)
            print(f"\n字符变化: {result['original_length']} -> {result['polished_length']}")
        else:
            print(f"\n✗ 优化失败: {result.get('error', 'Unknown error')}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_with_context():
    """测试带上下文的优化"""
    print("\n" + "=" * 60)
    print("测试带上下文的文案优化")
    print("=" * 60)
    
    test_text = """
    各位同学大家好，我是张老师。
    今天我们要学习 Python 编程的基础知识。
    首先我们来看看如何定义一个函数。
    函数是代码的重用单元，可以提高我们的开发效率。
    """
    
    context = {
        "topic": "Python编程教学",
        "speaker": "张老师",
        "audience": "计算机专业学生"
    }
    
    try:
        gemini = GeminiService()
        
        print(f"\n上下文信息:")
        for k, v in context.items():
            print(f"  {k}: {v}")
        
        print(f"\n原始文本:")
        print("-" * 60)
        print(test_text)
        print("-" * 60)
        
        result = gemini.polish_with_context(test_text, context)
        
        if result['success']:
            print(f"\n优化后文本:")
            print("-" * 60)
            print(result['polished_text'])
            print("-" * 60)
            print("\n✓ 带上下文优化测试通过")
            return True
        else:
            print(f"\n✗ 优化失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        return False


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试边界情况")
    print("=" * 60)
    
    try:
        gemini = GeminiService()
        
        # 测试空文本
        print("\n1. 测试空文本...")
        result = gemini.polish_transcription("")
        assert not result['success'], "空文本应该返回失败"
        print("✓ 空文本处理正确")
        
        # 测试极短文本
        print("\n2. 测试极短文本...")
        result = gemini.polish_transcription("你好")
        print(f"  输入: '你好'")
        print(f"  输出: '{result['polished_text']}'")
        print(f"  状态: {'成功' if result['success'] else '失败'}")
        
        # 测试长文本
        print("\n3. 测试长文本...")
        long_text = "这是一个测试。" * 100
        result = gemini.polish_transcription(long_text)
        print(f"  输入长度: {len(long_text)} 字符")
        print(f"  输出长度: {result.get('polished_length', 0)} 字符")
        print(f"  状态: {'成功' if result['success'] else '失败'}")
        
        print("\n✓ 边界情况测试完成")
        return True
        
    except Exception as e:
        print(f"\n✗ 边界测试失败: {str(e)}")
        return False


if __name__ == '__main__':
    print("开始 Gemini API 集成测试\n")
    
    # 运行所有测试
    tests = [
        ("基础功能测试", test_gemini_basic),
        ("上下文优化测试", test_gemini_with_context),
        ("边界情况测试", test_edge_cases)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n测试 '{name}' 异常: {str(e)}")
            results.append((name, False))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(success for _, success in results)
    print("\n" + ("=" * 60))
    if all_passed:
        print("✓ 所有测试通过!")
    else:
        print("✗ 部分测试失败")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)
