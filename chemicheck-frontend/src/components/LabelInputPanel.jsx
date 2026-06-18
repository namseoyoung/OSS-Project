function LabelInputPanel({
  imagePreview,
  onImageChange,
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
      {riskSummary}
    </div>
  )
}

export default LabelInputPanel
