import { useState } from 'react'

function ResultPage({ result, onBack }) {
  const [activeTab, setActiveTab] = useState('transcription')

  const handleDownload = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      // Optional: Add a toast notification here instead of alert
    } catch (err) {
      console.error('复制失败:', err)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8 flex items-center gap-4">
        <button 
          onClick={onBack} 
          className="p-2 -ml-2 text-slate-400 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          title="返回"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            ✅ 转录完成
          </h2>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden mb-6">
        <div className="flex flex-wrap gap-x-8 gap-y-4 p-5 bg-slate-50/50 border-b border-slate-200 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-slate-500 font-medium">文件名</span>
            <span className="text-slate-900 font-medium">{result.filename}</span>
          </div>
          {result.duration && (
            <div className="flex items-center gap-2">
              <span className="text-slate-500 font-medium">时长</span>
              <span className="text-slate-900 font-mono">{Math.round(result.duration)}秒</span>
            </div>
          )}
          {result.model && (
            <div className="flex items-center gap-2">
              <span className="text-slate-500 font-medium">模型</span>
              <span className="text-slate-900 bg-slate-100 px-2 py-0.5 rounded">{result.model}</span>
            </div>
          )}
        </div>

        <div className="p-1 border-b border-slate-200 bg-slate-50/50 flex gap-1">
          <button
            className={`px-4 py-2.5 text-sm font-medium rounded-lg transition-all ${
              activeTab === 'transcription' 
                ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200' 
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
            onClick={() => setActiveTab('transcription')}
          >
            📝 转录文本
          </button>
          {result.polished_text && (
            <button
              className={`px-4 py-2.5 text-sm font-medium rounded-lg transition-all ${
                activeTab === 'polished' 
                  ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200' 
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
              onClick={() => setActiveTab('polished')}
            >
              ✨ AI 润色
            </button>
          )}
          {result.summary && (
            <button
              className={`px-4 py-2.5 text-sm font-medium rounded-lg transition-all ${
                activeTab === 'summary' 
                  ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200' 
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
              onClick={() => setActiveTab('summary')}
            >
              📋 智能摘要
            </button>
          )}
        </div>

        <div className="p-6">
          {activeTab === 'transcription' && (
            <div className="space-y-4">
              <div className="flex justify-end gap-2">
                <button 
                  onClick={() => handleCopy(result.transcription)}
                  className="px-3 py-1.5 text-xs font-medium bg-slate-100 text-slate-700 rounded hover:bg-slate-200 active:scale-95 transition-all"
                >
                  📋 复制
                </button>
                <button 
                  onClick={() => handleDownload(result.transcription, `${result.filename}_transcription.txt`)}
                  className="px-3 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100 active:scale-95 transition-all"
                >
                  💾 下载
                </button>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 max-h-[500px] overflow-y-auto">
                <pre className="whitespace-pre-wrap break-words font-sans text-slate-800 text-base leading-relaxed">
                  {result.transcription}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'polished' && result.polished_text && (
            <div className="space-y-4">
              <div className="flex justify-end gap-2">
                <button 
                  onClick={() => handleCopy(result.polished_text)}
                  className="px-3 py-1.5 text-xs font-medium bg-slate-100 text-slate-700 rounded hover:bg-slate-200 active:scale-95 transition-all"
                >
                  📋 复制
                </button>
                <button 
                  onClick={() => handleDownload(result.polished_text, `${result.filename}_polished.txt`)}
                  className="px-3 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100 active:scale-95 transition-all"
                >
                  💾 下载
                </button>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 max-h-[500px] overflow-y-auto">
                <pre className="whitespace-pre-wrap break-words font-sans text-slate-800 text-base leading-relaxed">
                  {result.polished_text}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'summary' && result.summary && (
            <div className="space-y-4">
              <div className="flex justify-end gap-2">
                <button 
                  onClick={() => handleCopy(result.summary)}
                  className="px-3 py-1.5 text-xs font-medium bg-slate-100 text-slate-700 rounded hover:bg-slate-200 active:scale-95 transition-all"
                >
                  📋 复制
                </button>
                <button 
                  onClick={() => handleDownload(result.summary, `${result.filename}_summary.txt`)}
                  className="px-3 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100 active:scale-95 transition-all"
                >
                  💾 下载
                </button>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 max-h-[500px] overflow-y-auto">
                <pre className="whitespace-pre-wrap break-words font-sans text-slate-800 text-base leading-relaxed">
                  {result.summary}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>

      {result.output_files && result.output_files.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
          <h3 className="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <span>📂</span> 输出文件
          </h3>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {result.output_files.map((file, index) => (
              <li key={index}>
                <a 
                  href={`/api/download/${file}`} 
                  download
                  className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 hover:text-indigo-700 transition-all text-sm font-medium text-slate-700 group"
                >
                  <span className="text-slate-400 group-hover:text-indigo-500">📄</span>
                  <span className="truncate">{file}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default ResultPage
