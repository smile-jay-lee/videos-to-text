import { useState } from 'react'
import { uploadVideo } from '../utils/api'

function UploadPage({ onSuccess }) {
  const [file, setFile] = useState(null)
  const [model, setModel] = useState('base')
  const [useAI, setUseAI] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // 检查文件大小 (500MB)
      if (selectedFile.size > 500 * 1024 * 1024) {
        setError('文件大小不能超过 500MB')
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      if (droppedFile.size > 500 * 1024 * 1024) {
        setError('文件大小不能超过 500MB')
        return
      }
      setFile(droppedFile)
      setError('')
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('请选择文件')
      return
    }

    setLoading(true)
    setError('')
    setProgress(0)

    try {
      // 模拟进度
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 1000)

      const result = await uploadVideo(file, model, useAI)
      
      clearInterval(progressInterval)
      setProgress(100)
      
      setTimeout(() => {
        onSuccess(result)
      }, 500)
    } catch (err) {
      setError(err.message || '处理失败，请重试')
      setLoading(false)
      setProgress(0)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="upload-page">
      <div className="upload-card">
        <h2>📤 上传视频或音频文件</h2>
        
        <form onSubmit={handleSubmit}>
          <div 
            className={`drop-zone ${file ? 'has-file' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {!file ? (
              <>
                <div className="drop-icon">📁</div>
                <p>拖拽文件到这里或点击选择</p>
                <p className="file-types">支持: MP4, AVI, MOV, MP3, WAV, AAC 等</p>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept="video/*,audio/*"
                  className="file-input"
                  id="file-input"
                  disabled={loading}
                />
                <label htmlFor="file-input" className="file-label">
                  选择文件
                </label>
              </>
            ) : (
              <div className="file-info">
                <div className="file-icon">🎬</div>
                <div className="file-details">
                  <p className="file-name">{file.name}</p>
                  <p className="file-size">{formatFileSize(file.size)}</p>
                </div>
                {!loading && (
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="remove-file"
                  >
                    ✕
                  </button>
                )}
              </div>
            )}
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <div className="options">
            <div className="option-group">
              <label htmlFor="model">Whisper 模型:</label>
              <select
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                disabled={loading}
              >
                <option value="tiny">Tiny - 最快 (~39MB)</option>
                <option value="base">Base - 推荐 (~142MB)</option>
                <option value="small">Small - 较准确 (~466MB)</option>
                <option value="medium">Medium - 很准确 (~1.5GB)</option>
                <option value="large">Large - 最准确 (~2.9GB，首次需下载)</option>
              </select>
              <small style={{color: '#6b7280', fontSize: '0.85rem', marginTop: '0.25rem'}}>
                首次使用会自动下载模型文件
              </small>
            </div>

            <div className="option-group checkbox">
              <input
                type="checkbox"
                id="use-ai"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                disabled={loading}
              />
              <label htmlFor="use-ai">启用 AI 润色和摘要</label>
            </div>
          </div>

          {loading && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="progress-text">处理中... {progress}%</p>
            </div>
          )}

          <button
            type="submit"
            className="submit-button"
            disabled={!file || loading}
          >
            {loading ? '处理中...' : '开始转录'}
          </button>
        </form>
      </div>

      <div className="features">
        <div className="feature">
          <div className="feature-icon">⚡</div>
          <h3>高速处理</h3>
          <p>基于 Whisper 引擎，快速准确</p>
        </div>
        <div className="feature">
          <div className="feature-icon">🤖</div>
          <h3>AI 增强</h3>
          <p>智能润色和内容摘要</p>
        </div>
        <div className="feature">
          <div className="feature-icon">📊</div>
          <h3>多格式支持</h3>
          <p>支持主流视频和音频格式</p>
        </div>
      </div>
    </div>
  )
}

export default UploadPage
