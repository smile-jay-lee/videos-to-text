import { useState, useEffect, useRef } from 'react'
import { useBiliPreview }   from '../hooks/useBiliPreview'
import { useTranscription } from '../hooks/useTranscription'

// ── 常量 ─────────────────────────────────────────────────────────────────────

const MODEL_OPTIONS = [
  { value: 'base',   label: 'Base',   note: '快速' },
  { value: 'small',  label: 'Small',  note: '推荐' },
  { value: 'medium', label: 'Medium', note: '精准' },
  { value: 'large',  label: 'Large',  note: '最慢但最全' },
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
    <div className="flex items-center flex-wrap gap-y-3">
      {steps.map((step, idx) => {
        const done   = phase === 'done' || idx < stepIdx
        const active = phase === 'processing' && idx === stepIdx
        return (
          <div key={step} className="flex items-center">
            <div className={`flex items-center gap-2 text-sm font-medium transition-colors ${
              done   ? 'text-emerald-600' :
              active ? 'text-indigo-600' :
                       'text-slate-400'
            }`}>
              <span className={`inline-block w-2 h-2 rounded-full transition-colors ${
                done   ? 'bg-emerald-500' :
                active ? 'bg-indigo-500 animate-pulse' :
                         'bg-slate-300'
              }`} />
              {STEP_LABELS[step] ?? step}
            </div>
            {idx < steps.length - 1 && (
              <span className={`mx-3 text-sm ${done ? 'text-emerald-400' : 'text-slate-300'}`}>→</span>
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
  const [model, setModel]       = useState('medium')
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
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

        {/* ─ Tab 切换 ─ */}
        <div className="flex border-b border-slate-200 bg-slate-50/50">
          {[['url', '链接提取 (B 站)'], ['file', '本地文件']].map(([key, label]) => (
            <button
              key={key}
              onClick={() => handleSwitchMode(key)}
              disabled={isProcessing}
              className={[
                'flex-1 py-4 text-sm font-medium transition-colors relative',
                mode === key
                  ? 'text-indigo-600 bg-white'
                  : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50',
                'disabled:pointer-events-none disabled:opacity-50',
              ].join(' ')}
            >
              {label}
              {mode === key && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600" />
              )}
            </button>
          ))}
        </div>

        <div className="p-6 sm:p-8">

          {/* ═══ URL 模式 ═══ */}
          {mode === 'url' && (
            <div className="space-y-4">
              
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700 block">视频链接</label>
                {/* 输入行 */}
                <div className="flex gap-3">
                  <input
                    value={bili.url}
                    onChange={e => bili.setUrl(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && bili.parseUrl()}
                    placeholder="BV1xx411c7XD · 完整链接 · 分享文本 均可"
                    disabled={isProcessing}
                    spellCheck={false}
                    className="flex-1 font-mono text-sm border border-slate-300 px-4 py-2.5 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:bg-slate-50 disabled:text-slate-400 transition-all"
                  />
                  <button
                    onClick={bili.parseUrl}
                    disabled={!bili.url.trim() || bili.isParsing || isProcessing}
                    className="px-6 py-2.5 text-sm font-medium bg-slate-900 text-white rounded-xl hover:bg-slate-800 active:scale-95 disabled:opacity-50 disabled:active:scale-100 transition-all shadow-sm"
                  >
                    {bili.isParsing ? '解析中…' : '解析'}
                  </button>
                </div>
              </div>

              {/* 解析错误 */}
              {bili.parseError && (
                <p className="text-sm text-red-600 border border-red-200 bg-red-50 px-4 py-3 rounded-xl">
                  {bili.parseError}
                </p>
              )}

              {/* 预览卡片 */}
              {bili.preview && (
                <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">
                  <dl className="grid grid-cols-[5rem_1fr] gap-x-4 gap-y-2 text-sm p-5 bg-slate-50/50">
                    <dt className="text-slate-500 font-medium">标题</dt>
                    <dd className="font-medium text-slate-900 break-words">{bili.preview.title}</dd>
                    <dt className="text-slate-500 font-medium">UP主</dt>
                    <dd className="text-slate-700">{bili.preview.owner}</dd>
                    <dt className="text-slate-500 font-medium">时长</dt>
                    <dd className="text-slate-700 font-mono">{fmtDuration(bili.preview.duration)}</dd>
                    {bili.preview.pages.length > 1 && (
                      <>
                        <dt className="text-slate-500 font-medium">分P 数</dt>
                        <dd className="text-slate-700">{bili.preview.pages.length} P</dd>
                      </>
                    )}
                  </dl>

                  {/* 分P 选择（仅多P视频） */}
                  {bili.preview.pages.length > 1 && (
                    <div className="border-t border-slate-200 px-5 py-3.5 bg-white flex items-center gap-4">
                      <span className="text-sm font-medium text-slate-700 flex-shrink-0">下载分P</span>
                      <select
                        value={pageNum ?? 1}
                        onChange={e => setPageNum(Number(e.target.value))}
                        disabled={isProcessing}
                        className="flex-1 text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 max-w-sm transition-all"
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
                  <div className="border-t border-slate-200 px-5 py-4 bg-white flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-mono bg-slate-100 px-2 py-1 rounded">{bili.preview.bvid}</span>
                    <button
                      onClick={handleUrlSubmit}
                      disabled={isProcessing}
                      className="text-sm font-medium bg-indigo-600 text-white px-6 py-2.5 rounded-xl hover:bg-indigo-700 active:scale-95 disabled:opacity-50 disabled:active:scale-100 transition-all shadow-sm"
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
                    'border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all select-none',
                    dragOver
                      ? 'border-indigo-500 bg-indigo-50/50 scale-[1.02]'
                      : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50',
                  ].join(' ')}
                >
                  <div className="text-5xl mb-4 opacity-80">📁</div>
                  <p className="text-base font-medium text-slate-700">拖拽文件到这里，或点击选择</p>
                  <p className="text-sm text-slate-500 mt-2">支持 MP4, AVI, MP3, WAV, M4A 等格式</p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*,audio/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
              ) : (
                <div className="border border-slate-200 rounded-xl p-5 flex items-center justify-between bg-white shadow-sm">
                  <div className="min-w-0 flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600 text-xl">
                      📄
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900 truncate">{file.name}</p>
                      <p className="text-xs text-slate-500 mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0 ml-4">
                    {!isProcessing && (
                      <button
                        onClick={() => setFile(null)}
                        className="text-sm font-medium text-slate-500 hover:text-red-600 transition-colors"
                      >
                        移除
                      </button>
                    )}
                    <button
                      onClick={handleFileSubmit}
                      disabled={isProcessing}
                      className="text-sm font-medium bg-indigo-600 text-white px-6 py-2.5 rounded-xl hover:bg-indigo-700 active:scale-95 disabled:opacity-50 disabled:active:scale-100 transition-all shadow-sm"
                    >
                      开始转录
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* ─ 共享配置（处理中时隐藏） ─ */}
        {!isProcessing && (
          <div className="border-t border-slate-200 px-6 py-4 bg-slate-50 flex flex-wrap items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-slate-700">模型选择</span>
              <div className="flex bg-slate-200/50 p-1 rounded-lg">
                {MODEL_OPTIONS.map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setModel(opt.value)}
                    className={[
                      'px-4 py-1.5 text-sm font-medium rounded-md transition-all',
                      model === opt.value
                        ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200'
                        : 'text-slate-600 hover:text-slate-900',
                    ].join(' ')}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <label className="flex items-center gap-2 cursor-pointer select-none group">
              <div className="relative flex items-center">
                <input
                  type="checkbox"
                  checked={useAI}
                  onChange={e => setUseAI(e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-10 h-5.5 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4.5 after:w-4.5 after:transition-all peer-checked:bg-indigo-600"></div>
              </div>
              <span className="text-sm font-medium text-slate-700 group-hover:text-slate-900 transition-colors">AI 总结润色</span>
            </label>
          </div>
        )}

        {/* ─ 进度步骤（处理中显示） ─ */}
        {isProcessing && (
          <div className="border-t border-indigo-100 px-6 py-5 bg-indigo-50/50">
            <ProgressSteps steps={tx.steps} stepIdx={tx.stepIdx} phase={tx.phase} />
          </div>
        )}

        {/* ─ 错误行 ─ */}
        {tx.phase === 'error' && (
          <div className="border-t border-red-100 px-6 py-4 bg-red-50 flex items-center justify-between">
            <div className="flex items-center gap-2 text-red-600">
              <span className="text-lg">⚠️</span>
              <span className="text-sm font-medium">{tx.error}</span>
            </div>
            <button
              onClick={tx.reset}
              className="text-sm font-medium text-red-700 hover:text-red-800 hover:underline ml-4"
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

