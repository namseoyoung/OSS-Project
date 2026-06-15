const steps = [
  {
    order: '01',
    title: '라벨 인식',
    body: '이미지 전처리와 OCR을 통해 성분 후보 텍스트를 추출합니다.',
  },
  {
    order: '02',
    title: '성분 정규화',
    body: '오탈자와 별칭을 보정해 표준 성분명으로 맞춥니다.',
  },
  {
    order: '03',
    title: '위험도 설명',
    body: '등급, 주의사항, 민감 계층 안내를 쉬운 문장으로 제공합니다.',
  },
]

function ProcessPipeline() {
  return (
    <section className="pipeline" aria-label="서비스 처리 흐름">
      {steps.map((step) => (
        <div key={step.order}>
          <span>{step.order}</span>
          <strong>{step.title}</strong>
          <p>{step.body}</p>
        </div>
      ))}
    </section>
  )
}

export default ProcessPipeline
