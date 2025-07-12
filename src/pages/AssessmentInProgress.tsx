import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Slider } from '@/components/ui/slider'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Badge } from '@/components/ui/badge'
import { Brain, Clock, Target, CheckCircle } from 'lucide-react'

interface Question {
  question: string
  options: string[]
  correct_answer_index: number
  knowledge_tag: string
  explanation: string
  difficulty_level: number
  estimated_time: number
}

interface Domain {
  index: number
  name: string
  description: string
  difficulty: number
  accessible: boolean
  status: string
}

export default function AssessmentInProgress() {
  const location = useLocation()
  const navigate = useNavigate()
  const [selectedDomain, setSelectedDomain] = useState<number | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [selectedAnswer, setSelectedAnswer] = useState<string>('')
  const [confidence, setConfidence] = useState([50])
  const [progress, setProgress] = useState(0)
  const [domains, setDomains] = useState<Domain[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const assessmentData = location.state?.assessmentData
    if (assessmentData?.domains) {
      setDomains(assessmentData.domains)
    } else {
      navigate('/')
    }
  }, [location.state, navigate])

  const handleStartDomain = async (domainIndex: number) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/start-domain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain_index: domainIndex }),
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentQuestion(data.question)
        setSelectedDomain(domainIndex)
        setSelectedAnswer('')
        setConfidence([50])
      }
    } catch (error) {
      console.error('Error starting domain:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer || selectedDomain === null) return

    setIsLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/submit-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answer_index: parseInt(selectedAnswer),
          confidence: confidence[0] / 100
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setProgress(data.progress || 0)
        
        if (data.completed) {
          navigate('/summary')
        } else if (data.question) {
          setCurrentQuestion(data.question)
          setSelectedAnswer('')
          setConfidence([50])
        }
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!domains.length) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <Brain className="h-16 w-16 text-blue-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Loading Assessment...</h2>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Assessment in Progress</h1>
          <Progress value={progress} className="w-full max-w-md mx-auto" />
          <p className="text-sm text-gray-600 mt-2">{Math.round(progress)}% Complete</p>
        </div>

        {!currentQuestion ? (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Select a Knowledge Domain</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {domains.map((domain) => (
                <Card
                  key={domain.index}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    domain.accessible ? 'bg-white' : 'bg-gray-50 opacity-60'
                  }`}
                  onClick={() => domain.accessible && handleStartDomain(domain.index)}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg">{domain.name}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant={domain.status === 'completed' ? 'default' : 'secondary'}>
                          {domain.status}
                        </Badge>
                        {domain.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-600" />}
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-2">{domain.description}</p>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Target className="h-4 w-4" />
                      <span>Difficulty: {domain.difficulty}/100</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-blue-600" />
                {domains[selectedDomain!]?.name}
              </CardTitle>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Target className="h-4 w-4" />
                  <span>Difficulty: {currentQuestion.difficulty_level}/100</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>Est. {currentQuestion.estimated_time}s</span>
                </div>
                <Badge variant="outline">{currentQuestion.knowledge_tag}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">{currentQuestion.question}</h3>
                <RadioGroup value={selectedAnswer} onValueChange={setSelectedAnswer}>
                  {currentQuestion.options.map((option, index) => (
                    <div key={index} className="flex items-center space-x-2 p-3 rounded-lg hover:bg-gray-50">
                      <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                      <Label htmlFor={`option-${index}`} className="flex-1 cursor-pointer">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              <div className="space-y-4">
                <Label className="text-sm font-medium">
                  Confidence Level: {confidence[0]}%
                </Label>
                <Slider
                  value={confidence}
                  onValueChange={setConfidence}
                  max={100}
                  min={0}
                  step={10}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Not confident</span>
                  <span>Very confident</span>
                </div>
              </div>

              <Button
                onClick={handleSubmitAnswer}
                disabled={!selectedAnswer || isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
              >
                {isLoading ? 'Submitting...' : 'Submit Answer'}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
