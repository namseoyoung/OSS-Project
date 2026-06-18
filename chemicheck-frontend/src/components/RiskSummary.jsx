function RiskSummary({ analysis, riskLabels, summary }) {
  return (
    <div
      className={`risk-meter risk-${analysis.overallRisk}`}
      aria-label={`현재 위험도 ${riskLabels[analysis.overallRisk]}`}
    >
      <span>종합 위험도</span>
      <strong>{riskLabels[analysis.overallRisk]}</strong>
      <p>{summary}</p>
    </div>
  )
}

export default RiskSummary
