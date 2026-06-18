function LabelInputPanel({
  imagePreview,
  onImageChange,
  isAnalyzing,
  analysisError,
  riskSummary,
}) {
  return (
    <div className="input-panel">
      <div className="section-heading">
        <h2>라벨 이미지 업로드</h2>
      </div>

      <label className="file-drop">
        <input type="file" accept="image/*" onChange={onImageChange} />
        {imagePreview ? (
          <img src={imagePreview} alt="업로드한 생활화학제품 라벨 미리보기" />
        ) : (
          <span>라벨 이미지 업로드</span>
        )}
      </label>
      {isAnalyzing && <p className="analysis-status">이미지를 분석하고 있습니다.</p>}
      {analysisError && <p className="analysis-error">{analysisError}</p>}
      {riskSummary}
    </div>
  )
}

export default LabelInputPanel
