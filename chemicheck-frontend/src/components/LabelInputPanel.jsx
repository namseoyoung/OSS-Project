function LabelInputPanel({
  imagePreview,
  labelText,
  productType,
  productTypes,
  sampleLabels,
  onImageChange,
  onLabelTextChange,
  onProductTypeChange,
  onSampleApply,
}) {
  return (
    <div className="input-panel">
      <div className="section-heading">
        <p className="eyebrow">1. 라벨 입력</p>
        <h2>제품 라벨 이미지와 OCR 텍스트</h2>
      </div>

      <label className="file-drop">
        <input type="file" accept="image/*" onChange={onImageChange} />
        {imagePreview ? (
          <img src={imagePreview} alt="업로드한 생활화학제품 라벨 미리보기" />
        ) : (
          <span>라벨 이미지 업로드</span>
        )}
      </label>

      <label className="field-label" htmlFor="product-type">
        제품군
      </label>
      <select id="product-type" value={productType} onChange={(event) => onProductTypeChange(event.target.value)}>
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
        onChange={(event) => onLabelTextChange(event.target.value)}
        rows={8}
        placeholder="예: 성분: 차아염소산나트륨, 계면활성제, 향료"
      />

      <div className="sample-actions" aria-label="예시 라벨">
        {sampleLabels.map((sample) => (
          <button key={sample.name} type="button" onClick={() => onSampleApply(sample)}>
            {sample.name}
          </button>
        ))}
      </div>
    </div>
  )
}

export default LabelInputPanel
