import { useMemo, useState } from 'react'
import './App.css'
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
      <header className="topbar" aria-label="서비스 소개">
        <div>
          <p className="eyebrow">OCR 및 AI 기반 생활화학제품 성분 분석</p>
          <h1>ChemiCheck</h1>
        </div>
        <label className="access-toggle">
          <input
            type="checkbox"
            checked={largeText}
            onChange={(event) => setLargeText(event.target.checked)}
          />
          큰 글씨
        </label>
      </header>

      <section className="hero-section" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="status-pill">라벨을 읽고, 성분을 쉽게 풀어드립니다</p>
          <h2 id="hero-title">복잡한 화학 성분표를 안전 등급과 생활 지침으로 변환합니다.</h2>
          <p>
            제품 라벨에서 추출한 성분을 정규화하고 위험도를 분류해, 고령층과 임산부, 영유아 보호자도 바로
            이해할 수 있는 설명을 제공합니다.
          </p>
        </div>
        <div className={`risk-meter risk-${analysis.overallRisk}`} aria-label={`현재 위험도 ${riskLabels[analysis.overallRisk]}`}>
          <span>종합 위험도</span>
          <strong>{riskLabels[analysis.overallRisk]}</strong>
          <p>{summary}</p>
        </div>
      </section>

      <section className="workspace" aria-label="성분 분석 작업 영역">
        <div className="input-panel">
          <div className="section-heading">
            <p className="eyebrow">1. 라벨 입력</p>
            <h2>제품 라벨 이미지와 OCR 텍스트</h2>
          </div>

          <label className="file-drop">
            <input type="file" accept="image/*" onChange={handleImageChange} />
            {imagePreview ? (
              <img src={imagePreview} alt="업로드한 생활화학제품 라벨 미리보기" />
            ) : (
              <span>라벨 이미지 업로드</span>
            )}
          </label>

          <label className="field-label" htmlFor="product-type">
            제품군
          </label>
          <select id="product-type" value={productType} onChange={(event) => setProductType(event.target.value)}>
            {productTypes.map((type) => (
              <option key={type}>{type}</option>
            ))}
          </select>

          <label className="field-label" htmlFor="label-text">
            OCR 추출 텍스트
          </label>
          <textarea
            id="label-text"
            value={labelText}
            onChange={(event) => setLabelText(event.target.value)}
            rows={8}
            placeholder="예: 성분: 차아염소산나트륨, 계면활성제, 향료"
          />

          <div className="sample-actions" aria-label="예시 라벨">
            {sampleLabels.map((sample) => (
              <button key={sample.name} type="button" onClick={() => applySample(sample)}>
                {sample.name}
              </button>
            ))}
          </div>
        </div>

        <div className="result-panel">
          <div className="section-heading">
            <p className="eyebrow">2. 위험도 분석</p>
            <h2>성분별 결과</h2>
          </div>

          <div className="stats-grid" aria-label="위험도별 성분 수">
            <div>
              <span>높음</span>
              <strong>{analysis.riskCounts.high}</strong>
            </div>
            <div>
              <span>보통</span>
              <strong>{analysis.riskCounts.medium}</strong>
            </div>
            <div>
              <span>낮음</span>
              <strong>{analysis.riskCounts.low}</strong>
            </div>
          </div>

          <div className="ingredient-list">
            {analysis.matchedIngredients.length ? (
              analysis.matchedIngredients.map((ingredient) => (
                <article className={`ingredient-card risk-${ingredient.risk}`} key={ingredient.id}>
                  <div>
                    <span className="risk-badge">{ingredient.riskMeta.label}</span>
                    <h3>{ingredient.name}</h3>
                    <p>{ingredient.category}</p>
                  </div>
                  <dl>
                    <div>
                      <dt>인식 표기</dt>
                      <dd>{ingredient.matchedAlias}</dd>
                    </div>
                    <div>
                      <dt>주요 우려</dt>
                      <dd>{ingredient.concerns.join(', ')}</dd>
                    </div>
                  </dl>
                  <ul>
                    {ingredient.guidance.map((guide) => (
                      <li key={guide}>{guide}</li>
                    ))}
                  </ul>
                  <p className="sensitive-note">{ingredient.sensitiveNote}</p>
                </article>
              ))
            ) : (
              <div className="empty-state">
                <h3>아직 매칭된 성분이 없습니다</h3>
                <p>성분명을 쉼표나 줄바꿈으로 구분해 입력하면 분석 결과가 표시됩니다.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="pipeline" aria-label="서비스 처리 흐름">
        <div>
          <span>01</span>
          <strong>라벨 인식</strong>
          <p>이미지 전처리와 OCR을 통해 성분 후보 텍스트를 추출합니다.</p>
        </div>
        <div>
          <span>02</span>
          <strong>성분 정규화</strong>
          <p>오탈자와 별칭을 보정해 표준 성분명으로 맞춥니다.</p>
        </div>
        <div>
          <span>03</span>
          <strong>위험도 설명</strong>
          <p>등급, 주의사항, 민감 계층 안내를 쉬운 문장으로 제공합니다.</p>
        </div>
      </section>
    </main>
  )
}

export default App
