function TopBar({ largeText, onLargeTextChange }) {
  return (
    <header className="topbar" aria-label="서비스 소개">
      <div>
        <p className="eyebrow">OCR 및 AI 기반 생활화학제품 성분 분석</p>
        <h1>ChemiCheck</h1>
      </div>
      <label className="access-toggle">
        <input
          type="checkbox"
          checked={largeText}
          onChange={(event) => onLargeTextChange(event.target.checked)}
        />
        큰 글씨
      </label>
    </header>
  )
}

export default TopBar
