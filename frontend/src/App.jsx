import { useState } from 'react'
import UploadPage from './components/UploadPage'
import ResultPage from './components/ResultPage'
import HistoryPage from './components/HistoryPage'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('upload')
  const [result, setResult] = useState(null)

  const handleUploadSuccess = (data) => {
    console.log('App.jsx handleUploadSuccess called with:', data)
    console.log('Has transcription:', !!data.transcription)
    console.log('Transcription length:', data.transcription?.length)
    
    setResult(data)
    setCurrentPage('result')
    
    console.log('Current page set to: result')
  }

  const handleBackToUpload = () => {
    setCurrentPage('upload')
    setResult(null)
  }
  
  const handleViewHistory = () => {
    setCurrentPage('history')
  }
  
  const handleViewResult = (data) => {
    setResult(data)
    setCurrentPage('result')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🎬 视频转文字</h1>
          <p className="subtitle">基于 Whisper 的智能语音识别系统</p>
          
          <nav className="app-nav">
            <button 
              onClick={() => setCurrentPage('upload')}
              className={currentPage === 'upload' ? 'active' : ''}
            >
              📤 上传
            </button>
            <button 
              onClick={handleViewHistory}
              className={currentPage === 'history' ? 'active' : ''}
            >
              📂 历史记录
            </button>
          </nav>
        </div>
      </header>
      
      <main className="app-main">
        <div className="container">
          {currentPage === 'upload' && (
            <UploadPage onSuccess={handleUploadSuccess} />
          )}
          {currentPage === 'history' && (
            <HistoryPage onViewResult={handleViewResult} />
          )}
          {currentPage === 'result' && result && (
            <ResultPage result={result} onBack={handleBackToUpload} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>&copy; 2026 视频转文字系统 | Powered by OpenAI Whisper</p>
        </div>
      </footer>
    </div>
  )
}

export default App
