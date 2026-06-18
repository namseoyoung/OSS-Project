import { useMemo, useState } from 'react'
import './App.css'
import AnalysisPanel from './components/AnalysisPanel'
import HeroSummary from './components/HeroSummary'
import LabelInputPanel from './components/LabelInputPanel'
import RiskSummary from './components/RiskSummary'
import TopBar from './components/TopBar'
import { sampleLabels } from './data/ingredientCatalog'
import { analyzeLabel, buildSummary } from './lib/analyzeLabel'

const riskLabels = {
  low: '낮음',
  medium: '보통',
  high: '높음',
  unknown: '확인 필요',
}

function App() {
  const [labelText, setLabelText] = useState('')
  const [imagePreview, setImagePreview] = useState('')
  const [largeText, setLargeText] = useState(false)
  const hasUploadedImage = Boolean(imagePreview)

  const analysis = useMemo(() => analyzeLabel(labelText, sampleLabels[0].productType), [labelText])
  const summary = buildSummary(analysis)

  const handleImageChange = (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    setImagePreview(URL.createObjectURL(file))
    setLabelText(sampleLabels[0].text)
  }

  return (
    <main className={largeText ? 'app large-text' : 'app'}>
      <TopBar largeText={largeText} onLargeTextChange={setLargeText} />
      <HeroSummary />

      <section className={hasUploadedImage ? 'workspace' : 'workspace upload-only'} aria-label="성분 분석 작업 영역">
        <LabelInputPanel
          imagePreview={imagePreview}
          onImageChange={handleImageChange}
          riskSummary={
            hasUploadedImage ? (
              <RiskSummary analysis={analysis} riskLabels={riskLabels} summary={summary} />
            ) : null
          }
        />
        {hasUploadedImage && <AnalysisPanel analysis={analysis} />}
      </section>
    </main>
  )
}

export default App
