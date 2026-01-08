import moviepy.editor as mp
import whisper
import os
import openai
import json
import requests
import time
from getpass import getpass
from dotenv import load_dotenv

# 加载环境变量中的API密钥
load_dotenv()

# 提取视频中的音频
def extract_audio_from_video(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

# 使用Whisper转换音频为文本
def audio_to_text(audio_path, language="zh"):
    print("正在加载Whisper模型...")
    model = whisper.load_model("base")  # 可选模型大小: tiny, base, small, medium, large
    
    print(f"开始转录音频: {audio_path}")
    result = model.transcribe(audio_path, language=language)
    
    return result["text"]

# 使用OpenAI API润色文本
def refine_text_with_openai(text, api_key=None):
    try:
        print("正在使用OpenAI API润色文本...")
        
        # 如果没有提供API密钥，尝试从环境变量获取
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未提供API密钥且环境变量中没有OPENAI_API_KEY")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建润色文本的请求数据
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "你是一个文本润色专家，擅长将转录的语音文本整理成有条理、语法正确、标点完善的文本。请修复可能的语音识别错误，并使文本更加流畅自然。保持原始内容的完整性和含义。"},
                {"role": "user", "content": f"请将以下转录文本润色，添加适当的标点符号，纠正可能的错误，使其更易阅读和理解：\n\n{text}"}
            ]
        }
        
        # 发送请求给OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60  # 设置超时时间为60秒
        )
        
        # 检查响应状态码
        if response.status_code != 200:
            error_message = f"API调用失败，状态码: {response.status_code}"
            if response.text:
                error_message += f", 错误信息: {response.text}"
            raise Exception(error_message)
        
        # 解析响应
        response_data = response.json()
        refined_text = response_data["choices"][0]["message"]["content"]
        
        # 再次调用API进行总结
        print("正在使用OpenAI API总结文本...")
        summary_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "你是一个擅长总结的AI助手。请简明扼要地总结文本的主要内容和观点。"},
                {"role": "user", "content": f"请总结以下文本的主要内容：\n\n{refined_text}"}
            ]
        }
        
        # 发送总结请求
        summary_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=summary_data,
            timeout=60
        )
        
        # 检查总结响应状态码
        if summary_response.status_code != 200:
            error_message = f"总结API调用失败，状态码: {summary_response.status_code}"
            if summary_response.text:
                error_message += f", 错误信息: {summary_response.text}"
            raise Exception(error_message)
        
        # 解析总结响应
        summary_response_data = summary_response.json()
        summary = summary_response_data["choices"][0]["message"]["content"]
        
        return refined_text, summary
    
    except Exception as e:
        print(f"OpenAI API调用失败: {str(e)}")
        return None, None

# 使用DeepSeek API润色文本
def refine_text_with_deepseek(text, api_key=None):
    try:
        print("正在使用DeepSeek API润色文本...")
        
        # 如果没有提供API密钥，尝试从环境变量获取
        if not api_key:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("未提供API密钥且环境变量中没有DEEPSEEK_API_KEY")
        
        api_url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 构建润色文本的请求数据
        data = {
            "model": "deepseek-chat", 
            "messages": [
                {"role": "system", "content": "你是一个文本润色专家，擅长将转录的语音文本整理成有条理、语法正确、标点完善的文本。请修复可能的语音识别错误，并使文本更加流畅自然。保持原始内容的完整性和含义。"},
                {"role": "user", "content": f"请将以下转录文本润色，添加适当的标点符号，纠正可能的错误，使其更易阅读和理解：\n\n{text}"}
            ]
        }
        
        # 发送请求给DeepSeek API
        response = requests.post(
            api_url, 
            headers=headers, 
            json=data, 
            timeout=60  # 设置超时时间为60秒
        )
        
        # 检查响应状态码
        if response.status_code != 200:
            error_message = f"API调用失败，状态码: {response.status_code}"
            if response.text:
                error_message += f", 错误信息: {response.text}"
            raise Exception(error_message)
        
        # 解析响应
        response_data = response.json()
        refined_text = response_data["choices"][0]["message"]["content"]
        
        # 再次调用API进行总结
        print("正在使用DeepSeek API总结文本...")
        data_summary = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个擅长总结的AI助手。请简明扼要地总结文本的主要内容和观点。"},
                {"role": "user", "content": f"请总结以下文本的主要内容：\n\n{refined_text}"}
            ]
        }
        
        # 发送总结请求
        response_summary = requests.post(
            api_url, 
            headers=headers, 
            json=data_summary, 
            timeout=60
        )
        
        # 检查总结响应状态码
        if response_summary.status_code != 200:
            error_message = f"总结API调用失败，状态码: {response_summary.status_code}"
            if response_summary.text:
                error_message += f", 错误信息: {response_summary.text}"
            raise Exception(error_message)
        
        # 解析总结响应
        response_summary_data = response_summary.json()
        summary = response_summary_data["choices"][0]["message"]["content"]
        
        return refined_text, summary
    
    except Exception as e:
        print(f"DeepSeek API调用失败: {str(e)}")
        return None, None

# 保存API密钥到环境变量文件
def save_api_key(service, api_key):
    with open('.env', 'a') as f:
        f.write(f"\n{service}_API_KEY={api_key}")
    print(f"{service} API密钥已保存到.env文件中，下次运行时将自动加载。")

# 主程序
def main():

    #用户输入文件名字
    video_name = input("请输入视频文件名: ")

    video_path = video_name + ".mp4"  # 你的视频文件路径
    audio_path = video_name + ".wav"  # 提取的音频文件路径
    
    # 如果视频文件不存在，让用户指定路径
    # if not os.path.exists(video_path):
    #     video_path = input("请输入视频文件路径: ")
    
    # 提取音频
    print(f"从视频 {video_path} 中提取音频...")
    extract_audio_from_video(video_path, audio_path)
    
    # 转换音频为文字
    original_text = audio_to_text(audio_path)
    print("\n原始识别结果：")
    print(original_text)
    
    # 保存原始文本到文件
    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(original_text)
    print(f"\n原始转录文本已保存到 transcription.txt")
    
    # 询问用户是否要使用AI润色和总结
    use_ai = input("\n是否使用AI润色和总结文本？(y/n): ").lower() == 'y'
    
    if use_ai:
        # 尝试从环境变量获取API密钥
        openai_api_key = os.getenv("OPENAI_API_KEY")
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        refined_text = None
        summary = None
        
        # 如果环境变量中有OpenAI API密钥，直接使用
        if openai_api_key:
            print("检测到环境变量中的OpenAI API密钥，正在使用...")
            refined_text, summary = refine_text_with_openai(original_text, openai_api_key)
        # 否则询问用户是否尝试使用OpenAI API
        else:
            try_openai = input("是否尝试使用OpenAI API？(y/n): ").lower() == 'y'
            
            if try_openai:
                api_key = getpass("请输入OpenAI API密钥: ")
                # 询问是否保存API密钥
                if input("是否保存此API密钥到本地环境变量文件中？(y/n): ").lower() == 'y':
                    save_api_key("OPENAI", api_key)
                refined_text, summary = refine_text_with_openai(original_text, api_key)
        
        # 如果OpenAI API失败或用户选择不使用，尝试DeepSeek
        if refined_text is None:
            print("\nOpenAI API不可用或未选择，尝试DeepSeek API...")
            
            # 如果环境变量中有DeepSeek API密钥，直接使用
            if deepseek_api_key:
                print("检测到环境变量中的DeepSeek API密钥，正在使用...")
                refined_text, summary = refine_text_with_deepseek(original_text, deepseek_api_key)
            # 否则询问用户输入
            else:
                api_key = getpass("请输入DeepSeek API密钥: ")
                # 询问是否保存API密钥
                if input("是否保存此API密钥到本地环境变量文件中？(y/n): ").lower() == 'y':
                    save_api_key("DEEPSEEK", api_key)
                refined_text, summary = refine_text_with_deepseek(original_text, api_key)
        
        # 如果成功获取润色后的文本和摘要
        if refined_text and summary:
            print("\n润色后的文本：")
            print(refined_text)
            
            print("\n文本摘要：")
            print(summary)
            
            # 将润色后的文本和摘要保存到结果文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("## 润色后的文本\n\n")
                f.write(refined_text)
                f.write("\n\n## 文本摘要\n\n")
                f.write(summary)
            
            print(f"\n润色后的文本和摘要已保存到 result.txt")
        else:
            print("\n无法使用API润色文本，请检查API密钥或网络连接。")

if __name__ == "__main__":
    main()
