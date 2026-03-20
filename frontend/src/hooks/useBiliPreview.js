import { useState, useCallback } from 'react'
import { getBiliInfo } from '../utils/api'

/**
 * 管理 B 站视频预解析状态
 * 返回: { url, setUrl, preview, isParsing, parseError, parseUrl, clearPreview }
 */
export function useBiliPreview() {
  const [url, setUrlState] = useState('')
  const [preview, setPreview] = useState(null)
  const [isParsing, setIsParsing] = useState(false)
  const [parseError, setParseError] = useState('')

  // 修改 URL 时自动清除旧的预览和错误
  const setUrl = useCallback((val) => {
    setUrlState(val)
    setPreview(null)
    setParseError('')
  }, [])

  const parseUrl = useCallback(async () => {
    const trimmed = url.trim()
    if (!trimmed || isParsing) return
    setIsParsing(true)
    setParseError('')
    setPreview(null)
    try {
      const data = await getBiliInfo(trimmed)
      setPreview(data)
    } catch (err) {
      setParseError(err.message || '解析失败，请检查链接是否正确')
    } finally {
      setIsParsing(false)
    }
  }, [url, isParsing])

  const clearPreview = useCallback(() => {
    setPreview(null)
    setParseError('')
  }, [])

  return { url, setUrl, preview, isParsing, parseError, parseUrl, clearPreview }
}
