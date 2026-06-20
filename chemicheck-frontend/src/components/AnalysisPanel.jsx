function AnalysisPanel({ analysis }) {
  const unknownIngredients = analysis.unknownIngredients ?? []
  const hasMatchedIngredients = analysis.matchedIngredients.length > 0

  return (
    <div className="result-panel">
      <div className="section-heading">
        <p className="eyebrow">위험도 분석</p>
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

      <div className="recognition-summary" aria-label="OCR 성분 후보">
        <div>
          <span>추가 확인</span>
          <strong>{unknownIngredients.length || 0}개</strong>
        </div>
      </div>

      <div className="ingredient-list">
        {hasMatchedIngredients ? (
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

      {unknownIngredients.length > 0 && (
        <section className="unknown-ingredients" aria-label="추가 확인이 필요한 성분">
          <div>
            <h3>추가 확인이 필요한 성분</h3>
            <p>OCR 인식 결과 또는 DB 미등록 성분으로, 위험도 산정에는 포함하지 않았습니다.</p>
          </div>
          <ul>
            {unknownIngredients.map((ingredient) => (
              <li key={ingredient.id}>{ingredient.name}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

export default AnalysisPanel
