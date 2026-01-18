"""
Gemini AI 服务
用于优化语音识别后的文案
"""
from google import genai
from google.genai import types
from typing import Optional
from app.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Gemini AI 服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 服务
        
        Args:
            api_key: Gemini API key，如果不提供则从配置读取
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # 配置 Gemini Client
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Gemini service initialized")
    
    def polish_transcription(self, text: str, custom_prompt: Optional[str] = None) -> dict:
        """
        优化转录文案，修正语音识别错误
        
        Args:
            text: 原始转录文本
            custom_prompt: 自定义提示词，如果不提供则使用默认提示
            
        Returns:
            dict: 包含 polished_text (优化后的文本) 和 success (是否成功)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for polishing")
            return {
                "success": False,
                "polished_text": text,
                "error": "Empty text"
            }
        
        try:
            # 构建提示词
            if custom_prompt:
                prompt = f"{custom_prompt}\n\n原文：\n{text}"
            else:
                prompt = f"""整理一下文案，可能存在语音识别错误，变成正确文案。

要求：
1. 修正明显的识别错误（如同音字、错别字）
2. 调整标点符号，使文案更通顺
3. 保持原文的语义和风格
4. 不要添加原文没有的内容
5. 不要过度修改，只修正错误

原文：
{text}

请直接输出优化后的文案，不要添加任何解释或说明。"""
            
            logger.info(f"Sending request to Gemini (text length: {len(text)} chars)")
            
            # 调用 Gemini API (使用 gemini-2.5-flash 模型)
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            polished_text = response.text.strip()
            
            logger.info(f"Gemini polishing completed (output length: {len(polished_text)} chars)")
            
            return {
                "success": True,
                "polished_text": polished_text,
                "original_length": len(text),
                "polished_length": len(polished_text)
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "polished_text": text,  # 失败时返回原文
                "error": str(e)
            }
    
    def polish_with_context(self, text: str, context: dict) -> dict:
        """
        带上下文的文案优化
        
        Args:
            text: 原始转录文本
            context: 上下文信息，如 {"topic": "技术讲座", "speaker": "张三"}
            
        Returns:
            dict: 优化结果
        """
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        custom_prompt = f"""根据以下上下文信息，整理文案并修正语音识别错误：

上下文：
{context_str}

整理要求：
1. 结合上下文信息理解内容
2. 修正识别错误
3. 调整标点和语句通顺度
4. 保持原意

原文："""
        
        return self.polish_transcription(text, custom_prompt=custom_prompt)


# 单例实例（延迟初始化）
_gemini_service_instance: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    获取 Gemini 服务单例
    
    Returns:
        GeminiService: Gemini 服务实例
    """
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance
