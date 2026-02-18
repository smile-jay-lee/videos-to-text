"""
业务逻辑层 - Bilibili音频下载服务

提供从Bilibili下载视频音频流的功能
仅依赖 Python 标准库 + requests
"""

import os
import re
import json
import time
import requests
from typing import Dict, Optional, List
from pathlib import Path
from utils.logger import get_logger
from utils.file_handler import ensure_dir, get_safe_filename

logger = get_logger(__name__)


class BiliAudioService:
    """
    Bilibili音频下载服务
    
    功能：
    - 解析B站视频链接（支持 BV号、AV号、短链接）
    - 获取视频元数据（标题、时长、分P信息）
    - 下载DASH格式音频流
    - 自动处理文件名安全性
    
    限制：
    - 仅支持公开、免费视频
    - 不支持付费内容（大会员专享）
    - 不支持需登录观看的视频
    """
    
    # B站API端点
    API_VIEW = 'https://api.bilibili.com/x/web-interface/view'
    API_PLAYURL = 'https://api.bilibili.com/x/player/playurl'
    
    # 请求头配置（防爬必需）
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/',
        'Origin': 'https://www.bilibili.com',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # 默认输出目录
    DEFAULT_OUTPUT_DIR = 'temp_audio'
    
    # 请求超时时间（秒）
    TIMEOUT = 30
    
    # 下载重试次数
    MAX_RETRIES = 3
    
    def __init__(self, output_dir: str = None):
        """
        初始化Bilibili音频下载服务
        
        Args:
            output_dir: 输出目录路径，默认为 temp_audio/
        """
        self.output_dir = Path(output_dir or self.DEFAULT_OUTPUT_DIR)
        ensure_dir(str(self.output_dir))
        
        # 创建会话（复用连接）
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
        logger.info(f"Bilibili音频下载服务已初始化，输出目录: {self.output_dir}")
    
    def download_audio(
        self,
        url_or_bvid: str,
        page_num: Optional[int] = None
    ) -> Optional[str]:
        """
        下载B站视频音频（主入口方法）
        
        Args:
            url_or_bvid: B站视频URL或BV号
            page_num: 指定下载第几P（从1开始），None表示下载第一P
            
        Returns:
            音频文件的绝对路径，失败返回None
            
        Example:
            >>> service = BiliAudioService()
            >>> audio_path = service.download_audio('BV1xx411c7XD')
            >>> # 或者指定分P
            >>> audio_path = service.download_audio('BV1xx411c7XD', page_num=2)
        """
        try:
            logger.info(f"开始处理: {url_or_bvid}")
            
            # 1. 解析视频ID
            video_id = self._parse_video_url(url_or_bvid)
            if not video_id:
                logger.error(f"无法解析视频ID: {url_or_bvid}")
                return None
            
            logger.info(f"解析到视频ID: {video_id}")
            
            # 2. 获取视频信息
            video_info = self._get_video_info(video_id)
            if not video_info:
                logger.error("无法获取视频信息")
                return None
            
            logger.info(f"视频标题: {video_info['title']}")
            logger.info(f"UP主: {video_info['owner']}")
            logger.info(f"总分P数: {len(video_info['pages'])}")
            
            # 3. 确定要下载的分P
            page_index = (page_num - 1) if page_num else 0
            if page_index < 0 or page_index >= len(video_info['pages']):
                logger.error(f"分P编号超出范围: {page_num} (总共{len(video_info['pages'])}P)")
                return None
            
            page = video_info['pages'][page_index]
            logger.info(f"准备下载第 {page['page']} P: {page['title']}")
            
            # 4. 获取音频流URL
            audio_info = self._get_audio_url(video_info['aid'], page['cid'])
            if not audio_info:
                logger.error("无法获取音频流地址")
                return None
            
            logger.info(f"音质ID: {audio_info['quality']}")
            
            # 5. 生成文件名和路径
            filename = self._generate_filename(
                video_info['title'],
                page['title'] if len(video_info['pages']) > 1 else None,
                page['page']
            )
            
            # 根据编码器确定扩展名
            ext = 'm4a' if 'audio' in audio_info['codec'] else 'mp4'
            filepath = self.output_dir / f"{filename}.{ext}"
            
            # 6. 下载文件
            success = self._download_file(
                audio_info['url'],
                filepath,
                audio_info.get('backup_urls', [])
            )
            
            if success:
                abs_path = str(filepath.absolute())
                logger.info(f"下载成功: {abs_path}")
                return abs_path
            else:
                logger.error("下载失败")
                return None
                
        except Exception as e:
            logger.error(f"下载过程发生异常: {str(e)}", exc_info=True)
            return None
    
    def get_video_info(self, url_or_bvid: str) -> Optional[Dict]:
        """
        获取视频元数据（不下载）
        
        Args:
            url_or_bvid: B站视频URL或BV号
            
        Returns:
            视频信息字典，包含 title, owner, pages 等字段
            
        Example:
            >>> service = BiliAudioService()
            >>> info = service.get_video_info('BV1xx411c7XD')
            >>> print(info['title'])
        """
        try:
            video_id = self._parse_video_url(url_or_bvid)
            if not video_id:
                return None
            
            return self._get_video_info(video_id)
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None
    
    # ============ 私有方法 ============
    
    def _parse_video_url(self, url_or_bvid: str) -> Optional[Dict[str, str]]:
        """
        解析视频URL或BV号，提取ID
        
        支持格式:
        - BV1xx411c7XD
        - av123456
        - https://www.bilibili.com/video/BV1xx411c7XD
        - https://b23.tv/xxxxx (短链接)
        
        Args:
            url_or_bvid: 视频URL或ID
            
        Returns:
            {'type': 'bvid'|'aid', 'id': 'xxx'}
        """
        # 处理短链接：先从文本中提取真正的 URL（兼容分享文本格式）
        if 'b23.tv' in url_or_bvid:
            b23_match = re.search(r'https?://b23\.tv/\S+', url_or_bvid)
            short_url = b23_match.group(0).rstrip('】')  if b23_match else url_or_bvid.strip()
            try:
                resp = self.session.head(short_url, allow_redirects=True, timeout=10)
                url_or_bvid = resp.url
                logger.info(f"短链接解析为: {url_or_bvid}")
            except Exception as e:
                logger.error(f"解析短链接失败: {e}")
                return None
        
        # 提取 BV 号
        bv_match = re.search(r'BV[a-zA-Z0-9]+', url_or_bvid, re.IGNORECASE)
        if bv_match:
            return {'type': 'bvid', 'id': bv_match.group(0)}
        
        # 提取 AV 号
        av_match = re.search(r'av(\d+)', url_or_bvid, re.IGNORECASE)
        if av_match:
            return {'type': 'aid', 'id': av_match.group(1)}
        
        # 直接是 BV 号
        if re.match(r'^BV[a-zA-Z0-9]{10}$', url_or_bvid, re.IGNORECASE):
            return {'type': 'bvid', 'id': url_or_bvid}
        
        return None
    
    def _get_video_info(self, video_id: Dict[str, str]) -> Optional[Dict]:
        """
        调用B站API获取视频详细信息
        
        Args:
            video_id: 由 _parse_video_url 返回的ID字典
            
        Returns:
            视频信息字典
        """
        params = {video_id['type']: video_id['id']}
        
        try:
            resp = self.session.get(
                self.API_VIEW,
                params=params,
                timeout=self.TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data['code'] != 0:
                logger.error(f"API返回错误: {data.get('message', '未知错误')} (code: {data['code']})")
                return None
            
            video_data = data['data']
            
            # 构建分P信息
            pages = []
            for page in video_data.get('pages', []):
                pages.append({
                    'title': page.get('part', video_data['title']),
                    'cid': page['cid'],
                    'duration': page['duration'],
                    'page': page['page']
                })
            
            # 如果没有pages字段，说明是单P视频
            if not pages:
                pages.append({
                    'title': video_data['title'],
                    'cid': video_data['cid'],
                    'duration': video_data.get('duration', 0),
                    'page': 1
                })
            
            return {
                'title': video_data['title'],
                'aid': video_data['aid'],
                'bvid': video_data['bvid'],
                'cid': video_data['cid'],
                'owner': video_data['owner']['name'],
                'duration': video_data.get('duration', 0),
                'pages': pages
            }
            
        except requests.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"解析响应数据失败: {e}")
            return None
    
    def _get_audio_url(self, aid: int, cid: int) -> Optional[Dict]:
        """
        获取音频流地址
        
        Args:
            aid: 视频AV号
            cid: 视频CID（分P唯一标识）
            
        Returns:
            音频信息字典，包含 url, backup_urls, codec, quality 字段
        """
        params = {
            'avid': aid,
            'cid': cid,
            'qn': 64,        # 未登录质量
            'fnver': 0,      # 固定值
            'fnval': 16,     # 16=DASH格式（分离音视频流）
            'fourk': 1,      # 支持4K
        }
        
        try:
            resp = self.session.get(
                self.API_PLAYURL,
                params=params,
                timeout=self.TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data['code'] != 0:
                logger.error(f"获取播放地址失败: {data.get('message')} (code: {data['code']})")
                return None
            
            play_data = data['data']
            
            # 优先获取 DASH 格式的纯音频流
            if 'dash' in play_data and 'audio' in play_data['dash']:
                audio_list = play_data['dash']['audio']
                if audio_list:
                    # 选择音质最好的（ID最大）
                    best_audio = max(audio_list, key=lambda x: x.get('id', 0))
                    return {
                        'url': best_audio['baseUrl'],
                        'backup_urls': best_audio.get('backupUrl', []),
                        'codec': 'audio/mp4',
                        'quality': best_audio.get('id', 0)
                    }
            
            # 如果没有 DASH 音频，尝试 durl（完整视频流）
            if 'durl' in play_data and play_data['durl']:
                logger.warning("该视频不支持单独音频流，将下载完整视频文件（含音频）")
                first_url = play_data['durl'][0]
                return {
                    'url': first_url['url'],
                    'backup_urls': first_url.get('backup_url', []),
                    'codec': 'video/mp4',
                    'quality': play_data.get('quality', 0)
                }
            
            logger.error("未找到可用的音频/视频流")
            return None
            
        except Exception as e:
            logger.error(f"获取音频流地址异常: {e}")
            return None
    
    def _download_file(
        self,
        url: str,
        filepath: Path,
        backup_urls: List[str] = None
    ) -> bool:
        """
        下载文件（支持重试和备用URL）
        
        Args:
            url: 主URL
            filepath: 保存路径
            backup_urls: 备用URL列表
            
        Returns:
            是否下载成功
        """
        urls_to_try = [url] + (backup_urls or [])
        
        for idx, current_url in enumerate(urls_to_try):
            for retry in range(self.MAX_RETRIES):
                try:
                    logger.info(f"尝试下载 (URL {idx + 1}/{len(urls_to_try)}, 重试 {retry + 1}/{self.MAX_RETRIES})")
                    
                    # 添加Range头以支持断点续传
                    download_headers = self.HEADERS.copy()
                    download_headers['Range'] = 'bytes=0-'
                    
                    # 流式下载
                    resp = self.session.get(
                        current_url,
                        headers=download_headers,
                        stream=True,
                        timeout=self.TIMEOUT
                    )
                    resp.raise_for_status()
                    
                    total_size = int(resp.headers.get('content-length', 0))
                    downloaded_size = 0
                    
                    with open(filepath, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=1024 * 1024):  # 1MB
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                # 记录进度（每10MB）
                                if downloaded_size % (10 * 1024 * 1024) < 1024 * 1024:
                                    if total_size > 0:
                                        progress = (downloaded_size / total_size) * 100
                                        logger.info(f"下载进度: {progress:.1f}%")
                    
                    logger.info(f"下载完成: {filepath.name} ({downloaded_size} bytes)")
                    return True
                    
                except requests.RequestException as e:
                    logger.warning(f"下载失败 (URL {idx + 1}, 重试 {retry + 1}): {e}")
                    
                    # 如果不是最后一次重试，等待后重试
                    if retry < self.MAX_RETRIES - 1:
                        time.sleep(2 ** retry)  # 指数退避
                        continue
                    
                    # 如果是最后一次重试且还有备用URL，尝试下一个URL
                    if idx < len(urls_to_try) - 1:
                        logger.info("尝试备用URL...")
                        break
                
                except Exception as e:
                    logger.error(f"下载过程发生异常: {e}")
                    return False
        
        logger.error("所有URL和重试均失败")
        
        # 清理可能的不完整文件
        if filepath.exists():
            try:
                filepath.unlink()
                logger.info("已删除不完整的文件")
            except:
                pass
        
        return False
    
    def _generate_filename(
        self,
        title: str,
        part_title: Optional[str] = None,
        page_num: int = 1
    ) -> str:
        """
        生成安全的文件名
        
        Args:
            title: 视频标题
            part_title: 分P标题
            page_num: 分P编号
            
        Returns:
            安全的文件名（不含扩展名）
        """
        # 清理主标题
        safe_title = get_safe_filename(title)
        
        # 如果有分P信息，添加到文件名
        if part_title and part_title != title:
            safe_part = get_safe_filename(part_title)
            filename = f"{safe_title}_P{page_num}_{safe_part}"
        else:
            filename = safe_title
        
        # 限制文件名长度（Windows限制260字符，保留扩展名空间）
        max_length = 200
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename.strip()
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()
