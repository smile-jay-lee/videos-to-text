"""
清理 Whisper 模型缓存
用于解决模型下载损坏或校验失败的问题
"""
import os
import shutil

def clear_whisper_cache():
    """清理 Whisper 模型缓存"""
    cache_dir = os.path.expanduser('~/.cache/whisper')
    
    if not os.path.exists(cache_dir):
        print(f"缓存目录不存在: {cache_dir}")
        return
    
    print(f"缓存目录: {cache_dir}")
    print("\n当前缓存的模型文件:")
    
    files = os.listdir(cache_dir)
    if not files:
        print("  (无)")
        return
    
    for file in files:
        file_path = os.path.join(cache_dir, file)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"  - {file} ({size_mb:.2f} MB)")
    
    print("\n选择操作:")
    print("1. 删除所有缓存")
    print("2. 删除 large 模型")
    print("3. 取消")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == '1':
        confirm = input("确认删除所有缓存? (yes/no): ").strip().lower()
        if confirm == 'yes':
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            print("✅ 已删除所有缓存")
        else:
            print("已取消")
    elif choice == '2':
        large_files = [f for f in files if 'large' in f.lower()]
        if large_files:
            for file in large_files:
                file_path = os.path.join(cache_dir, file)
                os.remove(file_path)
                print(f"✅ 已删除: {file}")
        else:
            print("未找到 large 模型文件")
    else:
        print("已取消")

if __name__ == '__main__':
    clear_whisper_cache()
