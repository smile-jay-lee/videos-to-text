"""测试API上传和转录功能"""
import os
import sys
import requests
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_upload_and_transcribe():
    """测试上传和转录API"""
    
    # 使用之前测试过的音频片段
    test_audio = r"D:\project\videos to text\frontend\static\uploads\621dbf1d-af55-4114-a7e1-99f3cfe5facf\test_segment_30s.wav"
    
    if not os.path.exists(test_audio):
        print(f"❌ 测试文件不存在: {test_audio}")
        return
    
    # 创建一个带中文名称的副本
    chinese_name_audio = os.path.join(os.path.dirname(test_audio), "测试音频-11点52分.wav")
    
    # 如果副本不存在，创建它
    if not os.path.exists(chinese_name_audio):
        import shutil
        shutil.copy2(test_audio, chinese_name_audio)
        print(f"✓ 创建测试文件: {chinese_name_audio}")
    
    # 上传文件
    url = "http://127.0.0.1:5000/api/upload"
    
    print(f"\n上传文件: {os.path.basename(chinese_name_audio)}")
    
    try:
        with open(chinese_name_audio, 'rb') as f:
            files = {'file': (os.path.basename(chinese_name_audio), f, 'audio/wav')}
            response = requests.post(url, files=files, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 上传成功!")
            print(f"  会话ID: {result.get('session_id')}")
            
            # 检查生成的输出文件
            session_id = result.get('session_id')
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', session_id)
            
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                print(f"\n生成的输出文件:")
                for f in files:
                    print(f"  - {f}")
                    
                    # 检查文件名是否保留了中文
                    if "测试音频" in f or "11点52分" in f:
                        print(f"    ✓ 文件名中文保留正确!")
                    else:
                        print(f"    ⚠ 文件名可能被修改了")
                    
                    # 读取内容检查幻觉
                    file_path = os.path.join(output_dir, f)
                    if f.endswith('.txt'):
                        with open(file_path, 'r', encoding='utf-8') as tf:
                            content = tf.read()
                            print(f"    内容长度: {len(content)} 字符")
                            
                            # 检查重复内容
                            if len(content) > 100:
                                # 检查前50个字符是否在后面重复出现很多次
                                sample = content[:50]
                                count = content.count(sample[:20])
                                if count > 10:
                                    print(f"    ⚠ 检测到重复内容 ('{sample[:20]}' 出现 {count} 次)")
                                else:
                                    print(f"    ✓ 未检测到明显的幻觉重复")
                            
                            print(f"    前100字符预览: {content[:100]}")
            else:
                print(f"❌ 输出目录不存在: {output_dir}")
        else:
            print(f"❌ 上传失败: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    print("=== 测试API上传和转录功能 ===")
    test_upload_and_transcribe()
