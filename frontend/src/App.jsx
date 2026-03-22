import { useState } from 'react'
import UploadPage from './components/UploadPage'
import ResultPage from './components/ResultPage'
import HistoryPage from './components/HistoryPage'
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
  
  const handleViewHistory = () => {
    setCurrentPage('history')
  }
  
  const handleViewResult = (data) => {
    setResult(data)
    setCurrentPage('result')
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Sleek Top Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={handleBackToUpload}>
            <span className="text-2xl">🎬</span>
            <h1 className="text-lg font-semibold text-slate-800 tracking-tight">视频转文字</h1>
          </div>
          
          <nav className="flex items-center gap-1 bg-slate-100/50 p-1 rounded-lg border border-slate-200/60">
            <button 
              onClick={() => setCurrentPage('upload')}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
                currentPage === 'upload' 
                  ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200/50' 
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
              }`}
            >
              上传
            </button>
            <button 
              onClick={handleViewHistory}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
                currentPage === 'history' 
                  ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200/50' 
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
              }`}
            >
              历史记录
            </button>
          </nav>
        </div>
      </header>
      
      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        {currentPage === 'upload' && (
          <UploadPage onSuccess={handleUploadSuccess} />
        )}
        {currentPage === 'history' && (
          <HistoryPage onViewResult={handleViewResult} />
        )}
        {currentPage === 'result' && result && (
          <ResultPage result={result} onBack={handleBackToUpload} />
        )}
      </main>

      {/* Minimal Footer */}
      <footer className="py-6 text-center text-sm text-slate-400">
        <p>&copy; 2026 视频转文字系统 | Powered by OpenAI Whisper</p>
      </footer>
    </div>
  )
}

export default App
