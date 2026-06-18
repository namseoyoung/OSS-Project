import { useMemo, useState } from 'react'
import './App.css'
import AnalysisPanel from './components/AnalysisPanel'
import HeroSummary from './components/HeroSummary'
import LabelInputPanel from './components/LabelInputPanel'
import RiskSummary from './components/RiskSummary'
import TopBar from './components/TopBar'
import { buildSummary } from './lib/analyzeLabel'
import { uploadLabelImage } from './lib/backendAnalysis'

const riskLabels = {
  low: '낮음',
  medium: '보통',
  high: '높음',
  unknown: '확인 필요',
}

function App() {
  const [analysis, setAnalysis] = useState(null)
  const [imagePreview, setImagePreview] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState('')
  const [largeText, setLargeText] = useState(false)
  const hasUploadedImage = Boolean(imagePreview)

  const summary = useMemo(() => (analysis ? buildSummary(analysis) : ''), [analysis])

  const handleImageChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    setImagePreview(URL.createObjectURL(file))
    setAnalysis(null)
    setAnalysisError('')
    setIsAnalyzing(true)

    try {
      setAnalysis(await uploadLabelImage(file))
    } catch (error) {
      setAnalysisError(error.message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <main className={largeText ? 'app large-text' : 'app'}>
      <TopBar largeText={largeText} onLargeTextChange={setLargeText} />
      <HeroSummary />

      <section className={hasUploadedImage ? 'workspace' : 'workspace upload-only'} aria-label="성분 분석 작업 영역">
        <LabelInputPanel
          imagePreview={imagePreview}
          onImageChange={handleImageChange}
          isAnalyzing={isAnalyzing}
          analysisError={analysisError}
          riskSummary={
            analysis ? (
              <RiskSummary analysis={analysis} riskLabels={riskLabels} summary={summary} />
            ) : null
          }
        />
        {hasUploadedImage && analysis && <AnalysisPanel analysis={analysis} />}
      </section>
    </main>
  )
}

export default App
