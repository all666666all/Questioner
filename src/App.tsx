import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import StartAssessment from './pages/StartAssessment'
import AssessmentInProgress from './pages/AssessmentInProgress'
import AssessmentSummary from './pages/AssessmentSummary'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Routes>
          <Route path="/" element={<StartAssessment />} />
          <Route path="/assessment" element={<AssessmentInProgress />} />
          <Route path="/summary" element={<AssessmentSummary />} />
        </Routes>
        <Toaster />
      </div>
    </Router>
  )
}

export default App
