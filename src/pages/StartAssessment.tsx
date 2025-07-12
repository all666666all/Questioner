import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Brain, BookOpen, Target } from 'lucide-react'

export default function StartAssessment() {
  const [topic, setTopic] = useState('')
  const [numDomains, setNumDomains] = useState([5])
  const navigate = useNavigate()

  const handleStartAssessment = async () => {
    if (!topic.trim()) {
      return
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/start-assessment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          num_domains: numDomains[0]
        }),
      })

      if (response.ok) {
        const data = await response.json()
        navigate('/assessment', { state: { assessmentData: data } })
      }
    } catch (error) {
      console.error('Error starting assessment:', error)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Brain className="h-16 w-16 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI-Powered Adaptive Testing
          </h1>
          <p className="text-lg text-gray-600">
            Discover your knowledge gaps and get personalized learning recommendations
          </p>
        </div>

        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              Start Your Assessment
            </CardTitle>
            <CardDescription>
              Enter a topic you'd like to be assessed on and choose the number of knowledge domains to explore.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="topic" className="text-sm font-medium">
                Assessment Topic
              </Label>
              <Input
                id="topic"
                placeholder="e.g., Machine Learning, Data Science, Web Development"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="text-base"
              />
            </div>

            <div className="space-y-4">
              <Label className="text-sm font-medium">
                Number of Knowledge Domains: {numDomains[0]}
              </Label>
              <Slider
                value={numDomains}
                onValueChange={setNumDomains}
                max={10}
                min={2}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>2 domains</span>
                <span>10 domains</span>
              </div>
            </div>

            <Button
              onClick={handleStartAssessment}
              disabled={!topic.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-base font-medium"
            >
              <BookOpen className="h-4 w-4 mr-2" />
              Start Assessment
            </Button>
          </CardContent>
        </Card>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="p-4">
            <div className="text-2xl font-bold text-blue-600 mb-1">Adaptive</div>
            <div className="text-sm text-gray-600">Questions adjust to your skill level</div>
          </div>
          <div className="p-4">
            <div className="text-2xl font-bold text-green-600 mb-1">Personalized</div>
            <div className="text-sm text-gray-600">Tailored learning recommendations</div>
          </div>
          <div className="p-4">
            <div className="text-2xl font-bold text-purple-600 mb-1">Intelligent</div>
            <div className="text-sm text-gray-600">AI-powered assessment engine</div>
          </div>
        </div>
      </div>
    </div>
  )
}
