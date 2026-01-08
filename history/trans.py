import os
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import math
import time
import whisper
from dotenv import load_dotenv

# 加载环境变量配置
load_dotenv()

def extract_audio(video_path, output_audio_path):
    """步骤1: 从视频中提取音频"""
    print("正在从视频中提取音频...")
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)
    video.close()
    print(f"音频已提取并保存到 {output_audio_path}")

def split_audio(audio_path, chunk_length_ms=10*60*1000):
    """将音频分割成较小的片段（每段10分钟），以满足API限制"""
    print(f"正在将音频分割为{chunk_length_ms/60000}分钟的片段...")
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    
    # 计算需要多少个分段
    num_chunks = math.ceil(len(audio) / chunk_length_ms)
    
    for i in range(num_chunks):
        start_ms = i * chunk_length_ms
        end_ms = min((i+1) * chunk_length_ms, len(audio))
        chunk = audio[start_ms:end_ms]
        chunk_path = f"temp_chunk_{i}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
        print(f"已创建音频片段 {i+1}/{num_chunks}")
    
    return chunks

def transcribe_audio_chunk(chunk_path, whisper_model=None):
    """使用本地Whisper模型转录单个音频片段"""
    print(f"正在转录音频片段 {chunk_path}...")
    
    # 如果没有传入模型实例，则加载模型
    if whisper_model is None:
        print("正在加载Whisper模型...")
        whisper_model = whisper.load_model("base")  # 可选模型：tiny, base, small, medium, large
    
    # 使用whisper模型进行转录
    result = whisper_model.transcribe(chunk_path, language="zh")
    
    return result["text"]

def audio_to_text(audio_path):
    """步骤2: 将音频转换为文本，处理大型文件时分段处理"""
    print("正在将音频转换为文本...")
    
    # 检查音频文件大小
    file_size = os.path.getsize(audio_path) / (1024 * 1024)  # 转换为MB
    
    if file_size > 20:  # 如果文件大于20MB，进行分段处理
        print(f"音频文件大小为 {file_size:.2f}MB，超过Whisper单次处理能力，将进行分段处理")
        chunks = split_audio(audio_path)
        
        # 加载一次whisper模型，所有片段共用
        print("正在加载Whisper模型...")
        whisper_model = whisper.load_model("base")  # 可选模型：tiny, base, small, medium, large
        
        # 转录每个片段
        transcriptions = []
        for chunk in chunks:
            transcription = transcribe_audio_chunk(chunk, whisper_model)
            transcriptions.append(transcription)
            
        # 合并所有转录结果
        full_text = " ".join(transcriptions)
        
        # 清理临时文件
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
    else:
        # 小文件直接转录
        full_text = transcribe_audio_chunk(audio_path)
    
    print("音频成功转换为文本")
    return full_text

def main():
    """处理视频到文本的主函数"""
    # 获取输入视频路径
    video_path = input("请输入视频文件路径(默认为社会学.mp4): ").strip() or "社会学.mp4"
    # 生成音频文件名
    audio_path = f"{os.path.splitext(video_path)[0]}_audio.mp3"
    # 生成转写文件名
    transcription_file = f"{os.path.splitext(video_path)[0]}_transcription.txt"
    
    try:
        # 步骤1: 提取音频
        if not os.path.exists(audio_path):
            extract_audio(video_path, audio_path)
        else:
            print(f"音频文件 {audio_path} 已存在，跳过提取步骤")
        
        # 步骤2: 将音频转换为文本
        if os.path.exists(transcription_file):
            print(f"已找到转写文本文件 {transcription_file}，跳过转写步骤")
            with open(transcription_file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = audio_to_text(audio_path)
            # 将文本保存到文件
            with open(transcription_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"转写文本已保存至 {transcription_file}")
        
        print(f"\n处理完成！转写文本已保存到 {transcription_file}")
        print(f"如需对文本进行AI总结，请运行 sub.py 并指定该文本文件")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()