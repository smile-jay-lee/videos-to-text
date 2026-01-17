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
      
      // 构造result对象传给ResultPage
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
      alert('删除成功')
      loadHistory() // 重新加载列表
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
      <div className="history-page">
        <div className="loading">
          <div className="spinner"></div>
          <p>加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <h2>📂 历史记录</h2>
        <p className="history-subtitle">共 {history.length} 条记录</p>
      </div>

      {error && (
        <div className="error-box">
          ⚠️ {error}
        </div>
      )}

      {history.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <p>暂无历史记录</p>
          <p className="empty-hint">上传文件后会在这里显示历史记录</p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div key={item.task_id} className="history-item">
              <div className="history-item-icon">
                🎬
              </div>
              
              <div className="history-item-content">
                <div className="history-item-title">
                  {item.filename}
                </div>
                
                <div className="history-item-meta">
                  <span>🕐 {formatDate(item.created_at)}</span>
                  <span>📊 {item.model || 'unknown'}</span>
                  {item.duration && (
                    <span>⏱️ {Math.round(item.duration)}秒</span>
                  )}
                  <span>💾 {formatSize(item.file_size)}</span>
                </div>
              </div>
              
              <div className="history-item-actions">
                <button
                  onClick={() => handleView(item.task_id)}
                  className="action-btn primary"
                  title="查看详情"
                >
                  👁️ 查看
                </button>
                <button
                  onClick={() => handleDelete(item.task_id, item.filename)}
                  className="action-btn danger"
                  title="删除记录"
                >
                  🗑️ 删除
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
