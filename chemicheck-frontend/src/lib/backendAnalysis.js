const riskMeta = {
  low: {
    label: '낮음',
    score: 1,
  },
  medium: {
    label: '보통',
    score: 2,
  },
  high: {
    label: '높음',
    score: 3,
  },
  unknown: {
    label: '확인 필요',
    score: 0,
  },
}

const normalizeRisk = (riskLevel) => {
  const normalized = String(riskLevel || 'unknown').toLowerCase()

  if (normalized === 'low' || normalized === 'medium' || normalized === 'high') {
    return normalized
  }

  return 'unknown'
}

export const mapBackendAnalysis = (payload) => {
  const riskAnalysis = payload.risk_analysis ?? {}
  const riskExplanation = payload.risk_explanation ?? {}
  const normalizedResults = payload.normalized_results ?? []
  const explanations = riskExplanation.ingredient_explanations ?? []
  const ingredientResults = riskAnalysis.ingredient_results ?? []
  const candidates = payload.ocr?.ingredients ?? normalizedResults.map((item) => item.original_name).filter(Boolean)
  const seenIngredients = new Set()

  const matchedIngredients = explanations.reduce((items, explanation, index) => {
    const key = String(explanation.standard_name || explanation.original_name || index).trim().toLowerCase()

    if (seenIngredients.has(key)) {
      return items
    }

    const riskResult = ingredientResults.find((item) => (
      item.original_name === explanation.original_name
      && item.standard_name === explanation.standard_name
    )) ?? ingredientResults[index] ?? {}

    if (!riskResult.risk_found) {
      return items
    }

    const risk = normalizeRisk(explanation.risk_level)
    const normalized = normalizedResults.find((item) => (
      item.original_name === explanation.original_name
      && item.standard_name === explanation.standard_name
    )) ?? normalizedResults[index] ?? {}

    seenIngredients.add(key)

    items.push({
      id: `${explanation.standard_name}-${index}`,
      name: explanation.standard_name,
      matchedAlias: normalized.original_name ?? explanation.original_name ?? explanation.standard_name,
      category: explanation.category || '성분 정보',
      risk,
      riskMeta: riskMeta[risk],
      concerns: [explanation.basis || 'CSV 기반 위험도 분류'].filter(Boolean),
      guidance: [explanation.warning].filter(Boolean),
      sensitiveNote: explanation.description,
    })

    return items
  }, [])

  const sortedIngredients = matchedIngredients.toSorted((a, b) => b.riskMeta.score - a.riskMeta.score)

  const riskCounts = sortedIngredients.reduce(
    (counts, ingredient) => ({
      ...counts,
      [ingredient.risk]: counts[ingredient.risk] + 1,
    }),
    { low: 0, medium: 0, high: 0, unknown: 0 },
  )
  const unmatchedCandidates = normalizedResults
    .filter((item) => !item.matched)
    .map((item) => item.original_name)
    .filter(Boolean)
  const unknownIngredients = unmatchedCandidates.map((candidate, index) => ({
    id: `unknown-${candidate}-${index}`,
    name: candidate,
    matchedAlias: candidate,
    category: '정규화되지 않은 성분 후보',
    risk: 'unknown',
    riskMeta: riskMeta.unknown,
    concerns: ['성분 DB 또는 alias 사전에서 일치 항목을 찾지 못했습니다.'],
    guidance: ['성분명을 다시 확인하거나 alias 사전에 해당 표기를 추가해 주세요.'],
    sensitiveNote: 'OCR 결과가 부정확하거나 신규/미등록 성분일 수 있어 추가 확인이 필요합니다.',
  }))

  return {
    productType: '',
    candidates,
    matchedIngredients: sortedIngredients,
    unknownIngredients,
    unmatchedCandidates,
    overallRisk: normalizeRisk(riskAnalysis.final_risk_level ?? riskExplanation.final_risk_level),
    riskCounts,
    rawText: payload.ocr?.raw_text ?? '',
    cleanText: payload.ocr?.clean_text ?? '',
  }
}

export const uploadLabelImage = async (file) => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? ''
  const formData = new FormData()
  formData.append('image', file)

  let response

  try {
    response = await fetch(`${apiBaseUrl}/api/analyze-label`, {
      method: 'POST',
      body: formData,
    })
  } catch {
    throw new Error('백엔드 서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해 주세요.')
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null)
    const errorText = errorBody ? '' : await response.text().catch(() => '')
    throw new Error(errorBody?.detail ?? errorText ?? '이미지 분석 중 오류가 발생했습니다.')
  }

  return mapBackendAnalysis(await response.json())
}
