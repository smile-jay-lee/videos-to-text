import os
import sys
import re
import requests
import time
import json
import random
from urllib.parse import urlparse, parse_qs
import http.cookiejar
import base64

# 用户代理列表，随机选择以减少被检测的可能性
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/91.0.4472.80 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
]

# 用于绕过反爬虫的高级请求会话类
class AdvancedSession:
    def __init__(self):
        self.session = requests.Session()
        self.cookie_jar = http.cookiejar.CookieJar()
        self.session.cookies = self.cookie_jar
        self.rotate_user_agent()
        
        # 设置基本请求头
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Referer': 'https://www.douyin.com/'
        })
    
    def rotate_user_agent(self):
        """随机切换User-Agent"""
        self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
    
    def get(self, url, **kwargs):
        """高级GET请求，加入随机延迟和错误重试"""
        max_retries = kwargs.pop('max_retries', 3)
        retry_delay = kwargs.pop('retry_delay', 1)
        
        # 随机延迟0-2秒，模拟人类行为
        time.sleep(random.uniform(0, 2))
        
        # 尝试请求，如果失败则重试
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, **kwargs)
                
                # 如果检测到反爬虫挑战，尝试处理
                if "_wafchallengeid" in response.text:
                    print(f"检测到反爬虫挑战页面，尝试处理...")
                    self.handle_waf_challenge(response)
                    continue
                
                return response
            except Exception as e:
                print(f"请求失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    self.rotate_user_agent()  # 切换User-Agent再试
                else:
                    raise
    
    def handle_waf_challenge(self, response):
        """尝试处理WAF反爬虫挑战"""
        print("正在尝试解决反爬虫挑战...")
        
        # 这里只是一个示例，真正的解决方案需要根据实际挑战内容编写
        # 目前，我们只是简单地增加一些cookie并重试
        self.session.cookies.set('_wafchallengeid_solved', 'true', domain='.douyin.com')
        self.session.cookies.set('douyin_device_id', f"{random.randint(10000, 99999)}{int(time.time())}")
        self.session.cookies.set('passport_csrf_token', base64.b64encode(os.urandom(16)).decode('utf-8'))
        
        # 增加其他可能的cookie
        self.session.cookies.set('ttwid', f"1%7C{base64.b64encode(os.urandom(40)).decode('utf-8')}%7C{int(time.time())}%7C")
        
        # 切换UA再试
        self.rotate_user_agent()

def extract_douyin_video(share_url):
    """使用高级方法提取抖音视频"""
    print(f"正在处理链接: {share_url}")
    
    try:
        # 清理链接，只保留抖音链接部分
        clean_url = re.search(r'(https://v\.douyin\.com/\S+)/?', share_url)
        if clean_url:
            share_url = clean_url.group(1)
        
        # 创建我们的高级会话
        session = AdvancedSession()
        
        print(f"获取抖音分享链接: {share_url}")
        
        # 第一步：获取重定向后的真实URL
        print("正在获取完整URL...")
        response = session.get(share_url, allow_redirects=True)
        if response.status_code != 200:
            print(f"访问链接失败，状态码: {response.status_code}")
            return None
        
        # 获取最终URL
        final_url = response.url
        print(f"重定向到: {final_url}")
        
        # 保存页面内容用于调试
        with open("douyin_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("页面内容已保存到douyin_response.html")
        
        # 检查页面是否包含反爬虫挑战
        if "_wafchallengeid" in response.text:
            print("页面包含反爬虫挑战，尝试访问API...")
            
            # 尝试直接通过视频ID访问API
            video_id = None
            
            # 从URL中提取视频ID
            path_match = re.search(r'/video/(\d+)', final_url)
            if path_match:
                video_id = path_match.group(1)
                print(f"从URL提取视频ID: {video_id}")
            
            # 从HTML内容中提取视频ID
            if not video_id:
                id_match = re.search(r'"itemId":"?(\d+)"?', response.text)
                if id_match:
                    video_id = id_match.group(1)
                    print(f"从HTML内容提取视频ID: {video_id}")
            
            if not video_id:
                print("无法获取视频ID，尝试使用抖音开放平台解析...")
                
                # 使用抖音开放平台接口
                platform_url = "https://www.douyin.com/aweme/v1/web/aweme/detail/"
                params = {
                    "aweme_id": video_id,
                    "aid": "1128",
                    "version_name": "23.5.0",
                    "device_platform": "android",
                    "os_version": "10",
                }
                
                # 轮换User-Agent
                session.rotate_user_agent()
                api_response = session.get(platform_url, params=params)
                
                if api_response.status_code == 200:
                    try:
                        api_data = api_response.json()
                        print("成功获取API数据")
                        video_url = api_data.get("aweme_detail", {}).get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
                        
                        if video_url:
                            print(f"找到视频URL: {video_url}")
                            return download_video(session, video_url)
                    except Exception as e:
                        print(f"解析API数据出错: {str(e)}")
            
            # 如果前面的方法都失败了，尝试通过直接搜索接口
            print("尝试使用搜索接口...")
            search_url = "https://www.douyin.com/aweme/v1/web/general/search/single/"
            search_params = {"keyword": final_url}
            search_response = session.get(search_url, params=search_params)
            
            if search_response.status_code == 200:
                try:
                    search_data = search_response.json()
                    print("搜索接口返回数据")
                    # 这里需要解析特定的搜索接口数据结构
                except Exception as e:
                    print(f"解析搜索结果出错: {str(e)}")
        
        # 尝试从页面内容中提取视频直链
        video_url_match = re.search(r'"playAddr":"([^"]+)"', response.text) or \
                          re.search(r'playAddr: ?"([^"]+)"', response.text) or \
                          re.search(r'"url":"([^"]+\.mp4[^"]*)"', response.text)
        
        if video_url_match:
            video_url = video_url_match.group(1).replace('\\u002F', '/').replace('\\', '')
            print(f"从页面中找到视频URL: {video_url}")
            return download_video(session, video_url)
        
        # 尝试从移动端API获取视频信息
        print("尝试通过移动端API获取视频...")
        
        # 提取视频ID
        video_id_match = re.search(r'/video/(\d+)', final_url) or \
                         re.search(r'"itemId":"?(\d+)"?', response.text)
        
        if not video_id_match:
            print("无法找到视频ID")
            return None
        
        video_id = video_id_match.group(1)
        print(f"提取到视频ID: {video_id}")
        
        # 使用移动端API
        mobile_headers = session.session.headers.copy()
        mobile_headers['User-Agent'] = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        
        # 添加X-Bogus参数(这是抖音验证的一部分)
        # 注意：实际上，这个参数需要动态生成，这里只是示例
        xbogus = f"DFSzswVLQfhANtGnS8s{random.randint(1000, 9999)}"
        
        api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}&a_bogus={xbogus}"
        session.session.headers = mobile_headers
        api_response = session.get(api_url)
        
        if api_response.status_code != 200:
            print(f"获取视频信息失败，状态码: {api_response.status_code}")
            return None
        
        try:
            video_data = api_response.json()
            # 保存API响应以便调试
            with open("douyin_api_response.json", "w", encoding="utf-8") as f:
                json.dump(video_data, f, ensure_ascii=False, indent=2)
            
            if not video_data.get('item_list'):
                print("API返回数据中没有视频信息")
                return None
            
            # 尝试获取无水印视频URL
            video_url = video_data['item_list'][0]['video']['play_addr']['url_list'][0]
            # 替换域名，获取无水印视频
            video_url = video_url.replace('playwm', 'play')
            print(f"从API获取到视频URL: {video_url}")
            
            return download_video(session, video_url)
            
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"解析视频数据失败: {str(e)}")
            print("无法通过API获取视频URL")
            return None
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def download_video(session, video_url):
    """下载视频的功能，封装成一个单独的函数"""
    try:
        print(f"开始下载视频: {video_url}")
        video_response = session.get(video_url, stream=True)
        
        if video_response.status_code != 200:
            print(f"下载视频失败，状态码: {video_response.status_code}")
            return None
        
        # 生成输出文件名
        timestamp = int(time.time())
        output_file = f"douyin_video_{timestamp}.mp4"
        
        # 保存视频
        total_size = int(video_response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_file, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 显示下载进度
                    if total_size > 0:
                        percent = int(100 * downloaded / total_size)
                        sys.stdout.write(f"\r下载进度: {percent}% ({downloaded}/{total_size} 字节)")
                        sys.stdout.flush()
        
        print(f"\n视频已成功下载到: {output_file}")
        return output_file
    except Exception as e:
        print(f"下载视频时出错: {str(e)}")
        return None

def main():
    """主函数，处理命令行参数或用户输入"""
    print("抖音视频下载器 - 高级版 (绕过反爬虫)")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入抖音分享链接: ")
    
    # 确保URL非空
    if not url.strip():
        print("链接为空，请提供有效的抖音链接")
        return
    
    extract_douyin_video(url)

if __name__ == "__main__":
    main()
