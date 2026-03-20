import { useState, useEffect, useRef } from 'react'
import { useBiliPreview }   from '../hooks/useBiliPreview'
import { useTranscription } from '../hooks/useTranscription'

// ── 常量 ─────────────────────────────────────────────────────────────────────

const MODEL_OPTIONS = [
  { value: 'base',   label: 'Base',   note: '快速' },
  { value: 'small',  label: 'Small',  note: '推荐' },
  { value: 'medium', label: 'Medium', note: '精准' },
]

const STEP_LABELS = {
  downloading:  '下载音频',
  uploading:    '上传文件',
  extracting:   '提取音频',
  transcribing: '语音转录',
  ai:           'AI 优化',
}

// ── 工具函数 ──────────────────────────────────────────────────────────────────

function fmtDuration(seconds) {
  const s = Math.floor(seconds)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${m}:${String(sec).padStart(2, '0')}`
}

// ── ProgressSteps 子组件 ──────────────────────────────────────────────────────

function ProgressSteps({ steps, stepIdx, phase }) {
  return (
    <div className="flex items-center flex-wrap gap-y-2">
      {steps.map((step, idx) => {
        const done   = phase === 'done' || idx < stepIdx
        const active = phase === 'processing' && idx === stepIdx
        return (
          <div key={step} className="flex items-center">
            <div className={`flex items-center gap-1.5 text-xs font-medium ${
              done   ? 'text-green-600' :
              active ? 'text-indigo-600' :
                       'text-gray-400'
            }`}>
              <span className={`inline-block w-1.5 h-1.5 rounded-full ${
                done   ? 'bg-green-500' :
                active ? 'bg-indigo-500 animate-pulse' :
                         'bg-gray-300'
              }`} />
              {STEP_LABELS[step] ?? step}
            </div>
            {idx < steps.length - 1 && (
              <span className={`mx-3 text-xs ${done ? 'text-green-400' : 'text-gray-300'}`}>→</span>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── 主组件 ────────────────────────────────────────────────────────────────────

function UploadPage({ onSuccess }) {
  const [mode, setMode]         = useState('url')
  const [model, setModel]       = useState('small')
  const [useAI, setUseAI]       = useState(false)
  const [file, setFile]         = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [pageNum, setPageNum]   = useState(null)  // null = 第 1 P

  const fileInputRef = useRef(null)
  const bili = useBiliPreview()
  const tx   = useTranscription()

  // 预览视频更换时重置分P选择
  useEffect(() => {
    if (bili.preview) setPageNum(null)
  }, [bili.preview])

  // 转录成功后跳转结果页
  useEffect(() => {
    if (tx.phase === 'done' && tx.result) {
      onSuccess(tx.result)
    }
  }, [tx.phase, tx.result, onSuccess])

  const isProcessing = tx.phase === 'processing'

  // ── 事件处理 ────────────────────────────────────────────────────────────────

  const handleSwitchMode = (m) => {
    if (isProcessing) return
    setMode(m)
    tx.reset()
    bili.clearPreview()
    setFile(null)
  }

  const handleUrlSubmit = () => {
    if (!bili.preview || isProcessing) return
    tx.submitUrl(bili.url, pageNum, model, useAI)
  }

  const handleFileSubmit = () => {
    if (!file || isProcessing) return
    tx.submitFile(file, model, useAI)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) { setFile(f); tx.reset() }
  }

  const handleFileSelect = (e) => {
    const f = e.target.files[0]
    if (f) { setFile(f); tx.reset() }
  }

  // ── 渲染 ────────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white border border-gray-200 rounded">

        {/* ─ Tab 切换 ─ */}
        <div className="flex border-b border-gray-200">
          {[['url', '链接提取 (B 站)'], ['file', '本地文件']].map(([key, label]) => (
            <button
              key={key}
              onClick={() => handleSwitchMode(key)}
              disabled={isProcessing}
              className={[
                'px-5 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors',
                mode === key
                  ? 'border-indigo-500 text-indigo-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'disabled:pointer-events-none disabled:opacity-50',
              ].join(' ')}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="p-5">

          {/* ═══ URL 模式 ═══ */}
          {mode === 'url' && (
            <div className="space-y-3">

              {/* 输入行 */}
              <div className="flex gap-2">
                <input
                  value={bili.url}
                  onChange={e => bili.setUrl(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && bili.parseUrl()}
                  placeholder="BV1xx411c7XD · 完整链接 · 分享文本 均可"
                  disabled={isProcessing}
                  spellCheck={false}
                  className="flex-1 font-mono text-sm border border-gray-300 px-3 py-2 rounded focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-100 disabled:bg-gray-50 disabled:text-gray-400"
                />
                <button
                  onClick={bili.parseUrl}
                  disabled={!bili.url.trim() || bili.isParsing || isProcessing}
                  className="px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {bili.isParsing ? '解析中…' : '解析'}
                </button>
              </div>

              {/* 解析错误 */}
              {bili.parseError && (
                <p className="text-xs text-red-600 border border-red-200 bg-red-50 px-3 py-2 rounded">
                  ✗ {bili.parseError}
                </p>
              )}

              {/* 预览卡片 */}
              {bili.preview && (
                <div className="border border-gray-200 rounded overflow-hidden">
                  <dl className="grid grid-cols-[5rem_1fr] gap-x-3 gap-y-1.5 text-sm p-4 bg-gray-50">
                    <dt className="text-gray-400">标题</dt>
                    <dd className="font-medium text-gray-900 break-words">{bili.preview.title}</dd>
                    <dt className="text-gray-400">UP主</dt>
                    <dd className="text-gray-700">{bili.preview.owner}</dd>
                    <dt className="text-gray-400">时长</dt>
                    <dd className="text-gray-700 font-mono">{fmtDuration(bili.preview.duration)}</dd>
                    {bili.preview.pages.length > 1 && (
                      <>
                        <dt className="text-gray-400">分P 数</dt>
                        <dd className="text-gray-700">{bili.preview.pages.length} P</dd>
                      </>
                    )}
                  </dl>

                  {/* 分P 选择（仅多P视频） */}
                  {bili.preview.pages.length > 1 && (
                    <div className="border-t border-gray-200 px-4 py-2.5 bg-white flex items-center gap-3">
                      <span className="text-xs text-gray-500 flex-shrink-0">下载分P</span>
                      <select
                        value={pageNum ?? 1}
                        onChange={e => setPageNum(Number(e.target.value))}
                        disabled={isProcessing}
                        className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-indigo-500 max-w-sm"
                      >
                        {bili.preview.pages.map(p => (
                          <option key={p.page} value={p.page}>
                            P{p.page} — {p.title} ({fmtDuration(p.duration)})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* 确认行 */}
                  <div className="border-t border-gray-200 px-4 py-2.5 bg-white flex items-center justify-between">
                    <span className="text-xs text-gray-400 font-mono">{bili.preview.bvid}</span>
                    <button
                      onClick={handleUrlSubmit}
                      disabled={isProcessing}
                      className="text-sm bg-indigo-600 text-white px-4 py-1.5 rounded hover:bg-indigo-700 disabled:opacity-40 transition-colors"
                    >
                      开始转录
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ═══ 文件模式 ═══ */}
          {mode === 'file' && (
            <>
              {!file ? (
                <div
                  onDrop={handleDrop}
                  onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                  onDragLeave={() => setDragOver(false)}
                  onClick={() => fileInputRef.current?.click()}
                  className={[
                    'border-2 border-dashed rounded p-10 text-center cursor-pointer transition-colors select-none',
                    dragOver
                      ? 'border-indigo-400 bg-indigo-50'
                      : 'border-gray-300 hover:border-gray-400 bg-gray-50',
                  ].join(' ')}
                >
                  <div className="text-4xl mb-3">📁</div>
                  <p className="text-sm text-gray-600">拖拽文件到这里，或点击选择</p>
                  <p className="text-xs text-gray-400 mt-1">MP4 / AVI / MOV / MKV / MP3 / WAV / M4A 等</p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*,audio/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
              ) : (
                <div className="border border-gray-200 rounded px-4 py-3 flex items-center justify-between bg-gray-50">
                  <div className="min-w-0">
                    <p className="text-sm font-mono font-medium truncate">{file.name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                    <button
                      onClick={handleFileSubmit}
                      disabled={isProcessing}
                      className="text-sm bg-indigo-600 text-white px-4 py-1.5 rounded hover:bg-indigo-700 disabled:opacity-40 transition-colors"
                    >
                      开始转录
                    </button>
                    {!isProcessing && (
                      <button
                        onClick={() => setFile(null)}
                        className="text-xs text-gray-400 hover:text-red-500 transition-colors"
                      >
                        移除
                      </button>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* ─ 共享配置（处理中时隐藏） ─ */}
        {!isProcessing && (
          <div className="border-t border-gray-100 px-5 py-3 bg-gray-50 flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500 font-medium">模型</span>
              <div className="flex border border-gray-300 rounded overflow-hidden text-xs">
                {MODEL_OPTIONS.map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setModel(opt.value)}
                    className={[
                      'px-3 py-1.5 transition-colors',
                      model === opt.value
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white text-gray-600 hover:bg-gray-100',
                    ].join(' ')}
                  >
                    {opt.label}
                    <span className="ml-1 opacity-60 font-normal">{opt.note}</span>
                  </button>
                ))}
              </div>
            </div>

            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={useAI}
                onChange={e => setUseAI(e.target.checked)}
                className="w-3.5 h-3.5"
              />
              <span className="text-xs text-gray-600">AI 总结润色</span>
            </label>
          </div>
        )}

        {/* ─ 进度步骤（处理中显示） ─ */}
        {isProcessing && (
          <div className="border-t border-gray-100 px-5 py-3 bg-indigo-50">
            <ProgressSteps steps={tx.steps} stepIdx={tx.stepIdx} phase={tx.phase} />
          </div>
        )}

        {/* ─ 错误行 ─ */}
        {tx.phase === 'error' && (
          <div className="border-t border-red-100 px-5 py-3 bg-red-50 flex items-center justify-between">
            <span className="text-xs text-red-600">✗ {tx.error}</span>
            <button
              onClick={tx.reset}
              className="text-xs text-indigo-600 hover:underline ml-4"
            >
              重试
            </button>
          </div>
        )}

      </div>
    </div>
  )
}

export default UploadPage

