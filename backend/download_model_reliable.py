"""
可靠的Whisper模型下载工具
使用requests库支持断点续传和重试机制
"""
import os
import hashlib
import requests
from tqdm import tqdm

# Whisper 模型配置
MODELS = {
    'tiny': {
        'url': 'https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt',
        'sha256': '65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9'
    },
    'base': {
        'url': 'https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt',
        'sha256': 'ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e'
    },
    'small': {
        'url': 'https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt',
        'sha256': '9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794'
    },
    'medium': {
        'url': 'https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt',
        'sha256': '345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1'
    },
    'large-v3': {
        'url': 'https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt',
        'sha256': 'e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb'
    }
}

def verify_file(file_path, expected_sha256):
    """验证文件SHA256"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_sha256

def download_with_resume(url, dest_path, expected_sha256, max_retries=3):
    """支持断点续传的下载"""
    
    # 检查是否已存在完整文件
    if os.path.exists(dest_path):
        print(f"检查现有文件...")
        if verify_file(dest_path, expected_sha256):
            print("✅ 文件已存在且完整，无需下载")
            return True
        else:
            print("文件已损坏，重新下载")
            os.remove(dest_path)
    
    # 创建临时文件
    temp_path = dest_path + '.download'
    resume_pos = 0
    
    # 如果存在未完成的下载，尝试续传
    if os.path.exists(temp_path):
        resume_pos = os.path.getsize(temp_path)
        print(f"检测到未完成的下载，从 {resume_pos / 1024 / 1024:.2f}MB 处继续")
    
    headers = {}
    if resume_pos > 0:
        headers['Range'] = f'bytes={resume_pos}-'
    
    for attempt in range(max_retries):
        try:
            print(f"\n{'续传' if resume_pos > 0 else '开始下载'} (尝试 {attempt + 1}/{max_retries})")
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            
            # 获取文件总大小
            if resume_pos > 0 and response.status_code == 206:
                # 断点续传成功
                total_size = int(response.headers.get('content-length', 0)) + resume_pos
                print(f"续传成功，总大小: {total_size / 1024 / 1024:.2f}MB")
            elif response.status_code == 200:
                # 服务器不支持断点续传或首次下载
                total_size = int(response.headers.get('content-length', 0))
                if resume_pos > 0:
                    print("服务器不支持断点续传，重新下载")
                    os.remove(temp_path)
                    resume_pos = 0
            else:
                raise Exception(f"HTTP错误: {response.status_code}")
            
            # 下载文件
            mode = 'ab' if resume_pos > 0 else 'wb'
            with open(temp_path, mode) as f:
                with tqdm(total=total_size, initial=resume_pos, unit='B', 
                         unit_scale=True, desc='下载进度') as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            print("\n下载完成，验证文件...")
            
            # 验证文件
            if verify_file(temp_path, expected_sha256):
                # 重命名为最终文件名
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                os.rename(temp_path, dest_path)
                print("✅ 文件校验成功！")
                return True
            else:
                print("❌ 文件校验失败")
                os.remove(temp_path)
                resume_pos = 0
                
        except KeyboardInterrupt:
            print("\n\n下载已取消，已保存进度，下次可继续")
            return False
        except Exception as e:
            print(f"下载出错: {str(e)}")
            if attempt < max_retries - 1:
                print("等待3秒后重试...")
                import time
                time.sleep(3)
                # 更新续传位置
                if os.path.exists(temp_path):
                    resume_pos = os.path.getsize(temp_path)
            else:
                print("达到最大重试次数")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, 'models')
    os.makedirs(cache_dir, exist_ok=True)
    
    print("=" * 60)
    print("Whisper 模型可靠下载工具（支持断点续传）")
    print("=" * 60)
    print(f"模型将下载到: {cache_dir}")
    print("=" * 60)
    print("\n可用模型:")
    print("1. tiny    (~39MB)   - 最快")
    print("2. base    (~142MB)  - 一般")
    print("3. small   (~466MB)  - 推荐（中文）⭐")
    print("4. medium  (~1.5GB)  - 很好（中文）⭐⭐")
    print("5. large-v3 (~2.9GB) - 最佳")
    print("0. 退出")
    
    choice = input("\n请选择要下载的模型 (0-5): ").strip()
    
    model_map = {
        '1': 'tiny',
        '2': 'base',
        '3': 'small',
        '4': 'medium',
        '5': 'large-v3'
    }
    
    if choice == '0':
        print("已取消")
        return
    
    if choice not in model_map:
        print("无效的选择")
        return
    
    model_name = model_map[choice]
    model_info = MODELS[model_name]
    dest_path = os.path.join(cache_dir, f'{model_name}.pt')
    
    print(f"\n开始下载 {model_name} 模型...")
    
    success = download_with_resume(
        model_info['url'],
        dest_path,
        model_info['sha256']
    )
    
    if success:
        print(f"\n✅ {model_name} 模型下载成功！")
        print(f"位置: {dest_path}")
        file_size = os.path.getsize(dest_path) / 1024 / 1024
        print(f"大小: {file_size:.2f}MB")
        print("\n现在可以在应用中使用这个模型了。")
    else:
        print(f"\n❌ {model_name} 模型下载失败")

if __name__ == '__main__':
    main()
