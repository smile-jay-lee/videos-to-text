import { useState, useEffect } from 'react'
import { getHistory, getHistoryDetail, deleteHistory } from '../utils/api'

function HistoryPage({ onViewResult }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    setError('')
    
    try {
      const data = await getHistory()
      setHistory(data.history || [])
    } catch (err) {
      setError(err.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleView = async (taskId) => {
    try {
      const data = await getHistoryDetail(taskId)
      
      const result = {
        task_id: data.task_id,
        filename: data.metadata?.filename || '未知',
        model: data.metadata?.model || 'unknown',
        duration: data.metadata?.duration,
        transcription: data.transcription,
        polished_text: data.polished_text,
        summary: data.summary
      }
      
      onViewResult(result)
    } catch (err) {
      alert('加载失败: ' + err.message)
    }
  }

  const handleDelete = async (taskId, filename) => {
    if (!confirm(`确定要删除 "${filename}" 吗？`)) {
      return
    }
    
    try {
      await deleteHistory(taskId)
      loadHistory()
    } catch (err) {
      alert('删除失败: ' + err.message)
    }
  }

  const formatDate = (isoString) => {
    if (!isoString) return '未知时间'
    const date = new Date(isoString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatSize = (bytes) => {
    if (!bytes) return '未知'
    const kb = bytes / 1024
    const mb = kb / 1024
    
    if (mb >= 1) {
      return `${mb.toFixed(2)} MB`
    } else if (kb >= 1) {
      return `${kb.toFixed(2)} KB`
    }
    return `${bytes} B`
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-500">
        <div className="w-10 h-10 border-4 border-slate-200 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
        <p className="text-sm font-medium">加载中...</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">历史记录</h2>
          <p className="text-sm text-slate-500 mt-1">共 {history.length} 条转录记录</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600 flex items-center gap-2">
          <span>⚠️</span> {error}
        </div>
      )}

      {history.length === 0 ? (
        <div className="text-center py-24 bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="text-5xl mb-4 opacity-50">📭</div>
          <p className="text-lg font-medium text-slate-900 mb-1">暂无历史记录</p>
          <p className="text-sm text-slate-500">上传文件后会在这里显示历史记录</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div key={item.task_id} className="group flex flex-col sm:flex-row sm:items-center gap-4 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-slate-300 transition-all">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 text-2xl flex-shrink-0">
                🎬
              </div>
              
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-semibold text-slate-900 mb-1.5 truncate">
                  {item.filename}
                </h3>
                
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500 font-medium">
                  <span className="flex items-center gap-1.5">
                    <span className="text-slate-400">🕐</span> {formatDate(item.created_at)}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="text-slate-400">📊</span> {item.model || 'unknown'}
                  </span>
                  {item.duration && (
                    <span className="flex items-center gap-1.5">
                      <span className="text-slate-400">⏱️</span> {Math.round(item.duration)}秒
                    </span>
                  )}
                  <span className="flex items-center gap-1.5">
                    <span className="text-slate-400">💾</span> {formatSize(item.file_size)}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center gap-2 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleView(item.task_id)}
                  className="px-4 py-2 text-sm font-medium bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 active:scale-95 transition-all"
                >
                  查看
                </button>
                <button
                  onClick={() => handleDelete(item.task_id, item.filename)}
                  className="px-4 py-2 text-sm font-medium bg-red-50 text-red-600 rounded-lg hover:bg-red-100 active:scale-95 transition-all"
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default HistoryPage
