import os
import openai
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量读取OpenAI API密钥
openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_with_chatgpt(text, subject=""):
    """使用ChatGPT API对文本进行总结
    
    Args:
        text: 需要总结的文本内容
        subject: 文本主题，帮助AI更好地理解内容
    
    Returns:
        总结后的文本
    """
    print("正在使用ChatGPT对文本进行总结...")
    
    # 如果文本超长，需要分块处理
    if len(text) > 12000:
        print("文本较长，将进行分块总结...")
        # 分块处理文本
        chunks = [text[i:i+12000] for i in range(0, len(text), 12000)]
        
        # 分别总结每个块
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"正在总结第 {i+1}/{len(chunks)} 块文本...")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-16k",  # 使用更大的上下文窗口
                messages=[
                    {"role": "system", "content": f"你是一个专业的{subject if subject else '内容'}总结助手，请对以下内容进行概括总结。"},
                    {"role": "user", "content": f"请对以下{'讲座' if subject else '文本'}内容的第{i+1}部分进行总结，提取关键观点：\n\n{chunk}"}
                ],
                max_tokens=1000
            )
            chunk_summaries.append(response.choices[0].message.content)
            # 添加短暂延迟以避免API速率限制
            time.sleep(1)
        
        # 最后对所有块的总结进行整合
        final_summary_prompt = "\n\n".join(chunk_summaries)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject if subject else '内容'}总结助手，请对以下内容进行整合总结。"},
                {"role": "user", "content": f"下面是一个{'关于'+subject if subject else ''}内容的分段总结，请将这些整合成一个连贯的总结，包括主要观点、理论框架和关键例子：\n\n{final_summary_prompt}"}
            ],
            max_tokens=1500
        )
        summary = response.choices[0].message.content
    else:
        # 文本长度适中，直接总结
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"你是一个专业的{subject if subject else '内容'}总结助手，请对以下内容进行概括总结。"},
                {"role": "user", "content": f"请对以下{'关于'+subject+'的' if subject else ''}内容进行详细总结，包括主要观点、理论框架和关键例子：\n\n{text}"}
            ],
            max_tokens=1500
        )
        summary = response.choices[0].message.content
    
    print("总结完成")
    return summary

def main():
    """对文本文件进行AI总结的主函数"""
    print("=== 文本AI总结工具 ===")
    
    # 获取要总结的文本文件路径
    file_path = input("请输入要总结的文本文件路径: ").strip()
    
    # 验证文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在。")
        return
    
    # 获取可选的主题信息，帮助AI更好地理解内容
    subject = input("请输入文本主题(可选，例如'社会学'、'心理学'等): ").strip()
    
    # 生成输出文件名
    base_name = os.path.splitext(file_path)[0]
    output_file = f"{base_name}_summary.txt"
    
    try:
        # 读取文本文件
        print(f"正在读取文件 '{file_path}'...")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # 检查文本是否为空
        if not text.strip():
            print("错误: 文本文件是空的。")
            return
        
        # 显示文本长度信息
        print(f"文本长度: 约 {len(text) // 1000}K 字符")
        
        # 调用API进行总结
        summary = summarize_with_chatgpt(text, subject)
        
        # 将总结保存到文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n总结已保存至 '{output_file}'")
        print(f"处理完成！")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
