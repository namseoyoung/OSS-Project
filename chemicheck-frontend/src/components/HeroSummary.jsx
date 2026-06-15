import heroImage from '../assets/hero.png'

function HeroSummary({ analysis, summary, riskLabels }) {
  return (
    <section className="hero-section" aria-labelledby="hero-title">
      <div className="hero-copy">
        <div>
          <p className="status-pill">라벨을 읽고, 성분을 쉽게 풀어드립니다</p>
          <h2 id="hero-title">복잡한 화학 성분표를 안전 등급과 생활 지침으로 변환합니다.</h2>
          <p>
            제품 라벨에서 추출한 성분을 정규화하고 위험도를 분류해, 고령층과 임산부, 영유아 보호자도 바로
            이해할 수 있는 설명을 제공합니다.
          </p>
        </div>
        <img src={heroImage} alt="" aria-hidden="true" />
      </div>
      <div className={`risk-meter risk-${analysis.overallRisk}`} aria-label={`현재 위험도 ${riskLabels[analysis.overallRisk]}`}>
        <span>종합 위험도</span>
        <strong>{riskLabels[analysis.overallRisk]}</strong>
        <p>{summary}</p>
      </div>
    </section>
  )
}

export default HeroSummary
