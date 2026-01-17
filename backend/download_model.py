"""
手动下载 Whisper 模型
解决网络连接问题导致的自动下载失败
"""
import os
import urllib.request
import hashlib
from tqdm import tqdm

# Whisper 模型下载地址和SHA256
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

def download_file(url, dest_path, expected_sha256=None):
    """下载文件并显示进度"""
    print(f"下载中: {url}")
    print(f"保存到: {dest_path}")
    
    # 获取文件大小
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req) as response:
        file_size = int(response.headers.get('Content-Length', 0))
    
    # 下载文件
    chunk_size = 8192
    downloaded = 0
    
    with urllib.request.urlopen(url) as response, \
         open(dest_path, 'wb') as out_file, \
         tqdm(total=file_size, unit='B', unit_scale=True, desc='下载进度') as pbar:
        
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            
            out_file.write(chunk)
            downloaded += len(chunk)
            pbar.update(len(chunk))
    
    print(f"\n下载完成！")
    
    # 验证SHA256
    if expected_sha256:
        print("正在验证文件...")
        sha256 = hashlib.sha256()
        with open(dest_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        if sha256.hexdigest() == expected_sha256:
            print("✅ 文件校验成功！")
        else:
            print("❌ 文件校验失败，请重新下载")
            os.remove(dest_path)
            return False
    
    return True

def main():
    # 使用项目根目录下的 models 文件夹，而不是 C 盘
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, 'models')
    os.makedirs(cache_dir, exist_ok=True)
    
    print("=" * 60)
    print("Whisper 模型手动下载工具")
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
    
    # 检查文件是否已存在
    if os.path.exists(dest_path):
        overwrite = input(f"\n文件已存在: {dest_path}\n是否覆盖? (yes/no): ").strip().lower()
        if overwrite != 'yes':
            print("已取消")
            return
    
    print(f"\n开始下载 {model_name} 模型...")
    print(f"文件大小: {model_info['url'].split('/')[-1]}")
    
    try:
        success = download_file(
            model_info['url'],
            dest_path,
            model_info['sha256']
        )
        
        if success:
            print(f"\n✅ {model_name} 模型下载成功！")
            print(f"位置: {dest_path}")
            print("\n现在可以在应用中使用这个模型了。")
        
    except KeyboardInterrupt:
        print("\n\n下载已取消")
        if os.path.exists(dest_path):
            os.remove(dest_path)
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        if os.path.exists(dest_path):
            os.remove(dest_path)

if __name__ == '__main__':
    main()
