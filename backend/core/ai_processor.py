"""
核心功能模块 - AI文本处理器
负责文本润色和总结功能
"""
import os
import requests
import time
from typing import Dict, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class AIProcessor:
    """AI文本处理器（润色、总结）"""
    
    SUPPORTED_PROVIDERS = ['openai', 'deepseek']
    
    def __init__(self, provider: str = "openai", api_key: str = None):
        """
        初始化AI处理器
        
        Args:
            provider: AI服务提供商 (openai/deepseek)
            api_key: API密钥，如果为None则从环境变量读取
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"不支持的提供商: {provider}")
        
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        
        if not self.api_key:
            raise ValueError(f"未找到 {provider} 的API密钥")
        
        self.api_url = self._get_api_url()
        logger.info(f"AI处理器已初始化，提供商: {provider}")
    
    def _get_api_key(self) -> Optional[str]:
        """从环境变量获取API密钥"""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "deepseek":
            return os.getenv("DEEPSEEK_API_KEY")
        return None
    
    def _get_api_url(self) -> str:
        """获取API地址"""
        if self.provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.provider == "deepseek":
            return "https://api.deepseek.com/v1/chat/completions"
        return ""
    
    def _get_model_name(self) -> str:
        """获取模型名称"""
        if self.provider == "openai":
            return "gpt-3.5-turbo"
        elif self.provider == "deepseek":
            return "deepseek-chat"
        return ""
    
    def _call_api(self, messages: list, max_tokens: int = 1500) -> str:
        """
        调用AI API
        
        Args:
            messages: 消息列表
            max_tokens: 最大token数
            
        Returns:
            API返回的文本
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self._get_model_name(),
                "messages": messages,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"API调用失败，状态码: {response.status_code}"
                if response.text:
                    error_msg += f", 错误: {response.text}"
                raise Exception(error_msg)
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"API调用失败: {str(e)}")
            raise
    
    def refine_text(self, text: str) -> str:
        """
        润色文本
        
        Args:
            text: 原始文本
            
        Returns:
            润色后的文本
        """
        try:
            logger.info(f"开始润色文本，长度: {len(text)} 字符")
            
            # 如果文本超长，分块处理
            if len(text) > 12000:
                return self._refine_long_text(text)
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个文本润色专家，擅长将转录的语音文本整理成有条理、语法正确、标点完善的文本。请修复可能的语音识别错误，并使文本更加流畅自然。保持原始内容的完整性和含义。"
                },
                {
                    "role": "user",
                    "content": f"请将以下转录文本润色，添加适当的标点符号，纠正可能的错误，使其更易阅读和理解：\n\n{text}"
                }
            ]
            
            refined = self._call_api(messages, max_tokens=2000)
            logger.info("文本润色完成")
            return refined
            
        except Exception as e:
            logger.error(f"文本润色失败: {str(e)}")
            raise
    
    def summarize(self, text: str, max_length: int = 500) -> str:
        """
        生成文本摘要
        
        Args:
            text: 原始文本
            max_length: 摘要最大长度
            
        Returns:
            摘要文本
        """
        try:
            logger.info(f"开始生成摘要，原文长度: {len(text)} 字符")
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个擅长总结的AI助手。请简明扼要地总结文本的主要内容和观点。"
                },
                {
                    "role": "user",
                    "content": f"请总结以下文本的主要内容（不超过{max_length}字）：\n\n{text}"
                }
            ]
            
            summary = self._call_api(messages, max_tokens=1000)
            logger.info("摘要生成完成")
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            raise
    
    def _refine_long_text(self, text: str) -> str:
        """处理长文本的润色"""
        logger.info("文本较长，将进行分块处理")
        
        # 分块
        chunk_size = 10000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        refined_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"正在润色第 {i+1}/{len(chunks)} 块")
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个文本润色专家。"
                },
                {
                    "role": "user",
                    "content": f"请润色以下文本的第{i+1}部分：\n\n{chunk}"
                }
            ]
            
            refined = self._call_api(messages, max_tokens=1500)
            refined_chunks.append(refined)
            
            # 避免API速率限制
            if i < len(chunks) - 1:
                time.sleep(1)
        
        return "\n\n".join(refined_chunks)
    
    def process_text(self, text: str, refine: bool = True, summarize: bool = True) -> Dict:
        """
        完整处理文本（润色+总结）
        
        Args:
            text: 原始文本
            refine: 是否润色
            summarize: 是否生成摘要
            
        Returns:
            包含原文、润色文本、摘要的字典
        """
        try:
            result = {
                "original": text,
                "refined": None,
                "summary": None
            }
            
            if refine:
                result["refined"] = self.refine_text(text)
            
            if summarize:
                # 对润色后的文本生成摘要（如果有），否则对原文生成
                text_to_summarize = result["refined"] if result["refined"] else text
                result["summary"] = self.summarize(text_to_summarize)
            
            logger.info("文本处理完成")
            return result
            
        except Exception as e:
            logger.error(f"文本处理失败: {str(e)}")
            raise
