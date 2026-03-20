import { useState, useRef, useCallback } from 'react'
import { uploadVideo, transcribeUrl } from '../utils/api'

// 每个步骤自动推进到下一步的延迟（ms）；99999 = 不自动推进，等 API 返回
const STEP_ADVANCE_MS = [2500, 2500, 99999, 99999]

/**
 * 管理转录任务（文件 or URL），并模拟多阶段进度
 *
 * 返回:
 *   phase:    'idle' | 'processing' | 'done' | 'error'
 *   stepIdx:  当前活跃步骤下标（>= steps.length 时全部完成）
 *   steps:    步骤 key 数组，如 ['downloading','extracting','transcribing']
 *   result:   后端返回的数据（phase=done 时有效）
 *   error:    错误信息字符串
 *   submitUrl(url, pageNum, model, useAI)
 *   submitFile(file, model, useAI)
 *   reset()
 */
export function useTranscription() {
  const [phase, setPhase]     = useState('idle')
  const [stepIdx, setStepIdx] = useState(0)
  const [steps, setSteps]     = useState([])
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const timersRef = useRef([])

  const run = useCallback(async (callFn, stepList) => {
    // 清除上次的定时器
    timersRef.current.forEach(clearTimeout)
    timersRef.current = []

    setPhase('processing')
    setSteps(stepList)
    setStepIdx(0)
    setResult(null)
    setError(null)

    // 按延迟递增安排每步推进，跳过最后一步（由 API 响应触发）
    let cumDelay = 0
    for (let i = 0; i < stepList.length - 1; i++) {
      cumDelay += (STEP_ADVANCE_MS[i] ?? 99999)
      if (cumDelay < 60000) {  // 超过 60s 的步骤不预设推进
        const target = i + 1
        const t = setTimeout(() => setStepIdx(target), cumDelay)
        timersRef.current.push(t)
      }
    }

    try {
      const data = await callFn()
      timersRef.current.forEach(clearTimeout)
      timersRef.current = []
      setStepIdx(stepList.length) // 超过最后一个下标 → UI 全部标绿
      setResult(data)
      setPhase('done')
    } catch (err) {
      timersRef.current.forEach(clearTimeout)
      timersRef.current = []
      setError(err.message || '处理失败，请重试')
      setPhase('error')
    }
  }, [])

  const submitUrl = useCallback((url, pageNum, model, useAI) => {
    const base = ['downloading', 'extracting', 'transcribing']
    const stepList = useAI ? [...base, 'ai'] : base
    return run(() => transcribeUrl(url, pageNum, model, useAI), stepList)
  }, [run])

  const submitFile = useCallback((file, model, useAI) => {
    const base = ['uploading', 'extracting', 'transcribing']
    const stepList = useAI ? [...base, 'ai'] : base
    return run(() => uploadVideo(file, model, useAI), stepList)
  }, [run])

  const reset = useCallback(() => {
    timersRef.current.forEach(clearTimeout)
    timersRef.current = []
    setPhase('idle')
    setSteps([])
    setStepIdx(0)
    setResult(null)
    setError(null)
  }, [])

  return { phase, stepIdx, steps, result, error, submitUrl, submitFile, reset }
}
