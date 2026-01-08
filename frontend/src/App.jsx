import { useState } from 'react'
import UploadPage from './components/UploadPage'
import ResultPage from './components/ResultPage'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('upload')
  const [result, setResult] = useState(null)

  const handleUploadSuccess = (data) => {
    setResult(data)
    setCurrentPage('result')
  }

  const handleBackToUpload = () => {
    setCurrentPage('upload')
    setResult(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🎬 视频转文字</h1>
          <p className="subtitle">基于 Whisper 的智能语音识别系统</p>
        </div>
      </header>
      
      <main className="app-main">
        <div className="container">
          {currentPage === 'upload' && (
            <UploadPage onSuccess={handleUploadSuccess} />
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
