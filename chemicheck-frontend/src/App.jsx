import { useMemo, useState } from 'react'
import './App.css'
import AnalysisPanel from './components/AnalysisPanel'
import HeroSummary from './components/HeroSummary'
import LabelInputPanel from './components/LabelInputPanel'
import ProcessPipeline from './components/ProcessPipeline'
import TopBar from './components/TopBar'
import { sampleLabels } from './data/ingredientCatalog'
import { analyzeLabel, buildSummary } from './lib/analyzeLabel'

const riskLabels = {
  low: '낮음',
  medium: '보통',
  high: '높음',
  unknown: '확인 필요',
}

const productTypes = ['욕실 세정제', '살균제', '세탁 세제', '방향제', '다목적 세정제']

function App() {
  const [labelText, setLabelText] = useState(sampleLabels[0].text)
  const [productType, setProductType] = useState(sampleLabels[0].productType)
  const [imagePreview, setImagePreview] = useState('')
  const [largeText, setLargeText] = useState(false)

  const analysis = useMemo(() => analyzeLabel(labelText, productType), [labelText, productType])
  const summary = buildSummary(analysis)

  const handleImageChange = (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    setImagePreview(URL.createObjectURL(file))
  }

  const applySample = (sample) => {
    setLabelText(sample.text)
    setProductType(sample.productType)
  }

  return (
    <main className={largeText ? 'app large-text' : 'app'}>
      <TopBar largeText={largeText} onLargeTextChange={setLargeText} />
      <HeroSummary analysis={analysis} summary={summary} riskLabels={riskLabels} />

      <section className="workspace" aria-label="성분 분석 작업 영역">
        <LabelInputPanel
          imagePreview={imagePreview}
          labelText={labelText}
          productType={productType}
          productTypes={productTypes}
          sampleLabels={sampleLabels}
          onImageChange={handleImageChange}
          onLabelTextChange={setLabelText}
          onProductTypeChange={setProductType}
          onSampleApply={applySample}
        />
        <AnalysisPanel analysis={analysis} />
      </section>

      <ProcessPipeline />
    </main>
  )
}

export default App
