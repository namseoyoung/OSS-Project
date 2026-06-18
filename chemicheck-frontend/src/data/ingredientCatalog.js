export const riskLevels = {
  low: {
    label: '낮음',
    tone: '안전 사용 가능',
    score: 1,
    description: '일반적인 사용 조건에서는 상대적으로 우려가 낮은 성분입니다.',
  },
  medium: {
    label: '보통',
    tone: '주의 필요',
    score: 2,
    description: '환기, 피부 접촉, 민감 계층 사용 여부를 확인해야 하는 성분입니다.',
  },
  high: {
    label: '높음',
    tone: '사용 전 확인',
    score: 3,
    description: '자극성, 흡입 위험, 환경 유해성 등으로 사용 조건을 엄격히 확인해야 합니다.',
  },
}

export const ingredientCatalog = [
  {
    id: 'sodium-hypochlorite',
    name: '차아염소산나트륨',
    aliases: ['sodium hypochlorite', '차아염소산 나트륨', '락스', '표백제'],
    category: '산화성 표백 성분',
    risk: 'high',
    concerns: ['흡입 자극', '피부 자극', '혼합 사용 위험'],
    guidance: [
      '밀폐된 공간에서는 사용하지 말고 창문을 열어 환기하세요.',
      '산성 세정제나 암모니아 성분과 함께 사용하지 마세요.',
      '장갑을 착용하고 어린이 손이 닿지 않는 곳에 보관하세요.',
    ],
    sensitiveNote: '영유아, 임산부, 호흡기 질환자는 사용 공간에 오래 머물지 않는 것이 좋습니다.',
  },
  {
    id: 'benzalkonium-chloride',
    name: '염화벤잘코늄',
    aliases: ['benzalkonium chloride', 'benzalkonium', '염화 벤잘코늄', 'bkc'],
    category: '살균 보존 성분',
    risk: 'medium',
    concerns: ['피부 자극', '눈 자극', '흡입 주의'],
    guidance: [
      '분사형 제품은 얼굴 가까이에서 사용하지 마세요.',
      '피부에 직접 닿았다면 흐르는 물로 씻어내세요.',
      '반려동물이나 영유아가 있는 공간에서는 잔류 여부를 확인하세요.',
    ],
    sensitiveNote: '민감성 피부 사용자는 반복 노출을 줄이는 편이 안전합니다.',
  },
  {
    id: 'ethanol',
    name: '에탄올',
    aliases: ['ethanol', 'ethyl alcohol', '알코올', '에틸알코올'],
    category: '용제 및 살균 성분',
    risk: 'medium',
    concerns: ['인화성', '피부 건조', '흡입 자극'],
    guidance: [
      '화기 주변에서 사용하지 마세요.',
      '사용 후 손이나 피부가 건조하면 보습제를 함께 사용하세요.',
      '넓은 면적에 사용할 때는 환기하세요.',
    ],
    sensitiveNote: '아토피나 건조성 피부가 있다면 잦은 접촉을 피하세요.',
  },
  {
    id: 'citric-acid',
    name: '구연산',
    aliases: ['citric acid', '시트릭애씨드', '구연산수'],
    category: '산도 조절 및 세정 보조 성분',
    risk: 'low',
    concerns: ['눈 자극 가능', '금속 부식 가능'],
    guidance: [
      '눈에 들어가지 않도록 주의하세요.',
      '대리석이나 민감한 금속 표면에는 장시간 방치하지 마세요.',
      '사용 후 표면을 깨끗한 물로 닦아내세요.',
    ],
    sensitiveNote: '일반적인 생활 사용에서는 우려가 낮지만 직접 접촉은 줄이는 것이 좋습니다.',
  },
  {
    id: 'limonene',
    name: '리모넨',
    aliases: ['limonene', 'd-limonene', '디리모넨', '향료'],
    category: '향료 성분',
    risk: 'medium',
    concerns: ['피부 민감 반응', '알레르기 가능성', '수생 환경 유해성'],
    guidance: [
      '향에 민감하면 소량으로 먼저 확인하세요.',
      '피부에 닿는 제품은 사용 후 이상 반응을 살펴보세요.',
      '남은 원액을 배수구에 한꺼번에 버리지 마세요.',
    ],
    sensitiveNote: '영유아나 알레르기 체질 사용자는 무향 제품을 우선 고려하세요.',
  },
  {
    id: 'sodium-carbonate',
    name: '탄산나트륨',
    aliases: ['sodium carbonate', '탄산 나트륨', 'washing soda'],
    category: '알칼리 세정 성분',
    risk: 'medium',
    concerns: ['눈 자극', '피부 자극', '분말 흡입 주의'],
    guidance: [
      '분말을 붓거나 섞을 때 눈과 코에 들어가지 않게 하세요.',
      '고무장갑을 착용하고 사용 후 손을 씻으세요.',
      '물에 녹일 때 튐이 없도록 천천히 섞으세요.',
    ],
    sensitiveNote: '피부가 약한 사용자는 직접 접촉을 피하는 것이 좋습니다.',
  },
  {
    id: 'surfactant',
    name: '계면활성제',
    aliases: ['surfactant', '음이온계면활성제', '비이온계면활성제', '계면 활성제'],
    category: '세정 성분',
    risk: 'low',
    concerns: ['피부 건조', '잔류 가능성'],
    guidance: [
      '식기나 표면에 사용한 뒤에는 충분히 헹구세요.',
      '원액이 피부에 오래 닿지 않도록 하세요.',
      '사용량 안내를 넘기지 않는 것이 좋습니다.',
    ],
    sensitiveNote: '영유아용 물품에는 잔류 세제가 남지 않도록 충분히 헹구세요.',
  },
]

export const sampleLabels = [
  {
    name: '욕실 세정제',
    productType: '욕실 세정제',
    text: '성분: 차아염소산나트륨, 계면활성제, 향료, 정제수. 사용 시 충분히 환기하십시오.',
  },
  {
    name: '살균 스프레이',
    productType: '살균제',
    text: '전성분: 에탄올, 염화벤잘코늄, 리모넨, 정제수. 화기 근처 사용 금지.',
  },
  {
    name: '친환경 다목적 세정제',
    productType: '다목적 세정제',
    text: '주요 성분: 구연산, 탄산나트륨, 비이온계면활성제, 레몬향.',
  },
]
