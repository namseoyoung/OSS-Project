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

const productTypes = ['욕실 세정제', '살균제', '세탁 세제', '방향제', '다목적 세정제']

function App() {
  const [labelText, setLabelText] = useState('')
  const [productType, setProductType] = useState(sampleLabels[0].productType)
  const [imagePreview, setImagePreview] = useState('')
  const [largeText, setLargeText] = useState(false)
  const hasUploadedImage = Boolean(imagePreview)

  const analysis = useMemo(() => analyzeLabel(labelText, productType), [labelText, productType])
  const summary = buildSummary(analysis)

  const handleImageChange = (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const selectedSample = sampleLabels.find((sample) => sample.productType === productType)

    setImagePreview(URL.createObjectURL(file))
    setLabelText(selectedSample?.text ?? sampleLabels[0].text)
  }

  const handleProductTypeChange = (nextProductType) => {
    const nextSample = sampleLabels.find((sample) => sample.productType === nextProductType)

    setProductType(nextProductType)
    setLabelText(nextSample?.text ?? sampleLabels[0].text)
  }

  return (
    <main className={largeText ? 'app large-text' : 'app'}>
      <TopBar largeText={largeText} onLargeTextChange={setLargeText} />
      <HeroSummary />

      <section className={hasUploadedImage ? 'workspace' : 'workspace upload-only'} aria-label="성분 분석 작업 영역">
        <LabelInputPanel
          imagePreview={imagePreview}
          productType={productType}
          productTypes={productTypes}
          onImageChange={handleImageChange}
          onProductTypeChange={handleProductTypeChange}
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
