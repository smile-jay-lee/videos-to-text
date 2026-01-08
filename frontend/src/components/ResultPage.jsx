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
      alert('已复制到剪贴板')
    } catch (err) {
      console.error('复制失败:', err)
    }
  }

  return (
    <div className="result-page">
      <div className="result-header">
        <button onClick={onBack} className="back-button">
          ← 返回上传
        </button>
        <h2>✅ 转录完成</h2>
      </div>

      <div className="result-info">
        <div className="info-item">
          <span className="info-label">文件名:</span>
          <span className="info-value">{result.filename}</span>
        </div>
        {result.duration && (
          <div className="info-item">
            <span className="info-label">时长:</span>
            <span className="info-value">{Math.round(result.duration)}秒</span>
          </div>
        )}
        {result.model && (
          <div className="info-item">
            <span className="info-label">模型:</span>
            <span className="info-value">{result.model}</span>
          </div>
        )}
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'transcription' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcription')}
        >
          📝 转录文本
        </button>
        {result.polished_text && (
          <button
            className={`tab ${activeTab === 'polished' ? 'active' : ''}`}
            onClick={() => setActiveTab('polished')}
          >
            ✨ AI 润色
          </button>
        )}
        {result.summary && (
          <button
            className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
            onClick={() => setActiveTab('summary')}
          >
            📋 智能摘要
          </button>
        )}
      </div>

      <div className="result-content">
        {activeTab === 'transcription' && (
          <div className="text-box">
            <div className="text-actions">
              <button 
                onClick={() => handleCopy(result.transcription)}
                className="action-btn"
              >
                📋 复制
              </button>
              <button 
                onClick={() => handleDownload(result.transcription, `${result.filename}_transcription.txt`)}
                className="action-btn"
              >
                💾 下载
              </button>
            </div>
            <pre className="text-content">{result.transcription}</pre>
          </div>
        )}

        {activeTab === 'polished' && result.polished_text && (
          <div className="text-box">
            <div className="text-actions">
              <button 
                onClick={() => handleCopy(result.polished_text)}
                className="action-btn"
              >
                📋 复制
              </button>
              <button 
                onClick={() => handleDownload(result.polished_text, `${result.filename}_polished.txt`)}
                className="action-btn"
              >
                💾 下载
              </button>
            </div>
            <pre className="text-content">{result.polished_text}</pre>
          </div>
        )}

        {activeTab === 'summary' && result.summary && (
          <div className="text-box">
            <div className="text-actions">
              <button 
                onClick={() => handleCopy(result.summary)}
                className="action-btn"
              >
                📋 复制
              </button>
              <button 
                onClick={() => handleDownload(result.summary, `${result.filename}_summary.txt`)}
                className="action-btn"
              >
                💾 下载
              </button>
            </div>
            <pre className="text-content">{result.summary}</pre>
          </div>
        )}
      </div>

      {result.output_files && result.output_files.length > 0 && (
        <div className="output-files">
          <h3>📂 输出文件</h3>
          <ul>
            {result.output_files.map((file, index) => (
              <li key={index}>
                <a href={`/api/download/${file}`} download>
                  {file}
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
