import { ingredientCatalog, riskLevels } from '../data/ingredientCatalog'

const normalize = (value) =>
  value
    .toLowerCase()
    .replace(/[()[\]{}·ㆍ,./:;|+_-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

const splitCandidates = (text) =>
  text
    .split(/[\n,;:|/]+/)
    .map((item) => item.replace(/성분|전성분|주요 성분|함유|사용 시|주의/gi, '').trim())
    .filter(Boolean)

export const analyzeLabel = (rawText, productType) => {
  const normalizedText = normalize(rawText)
  const candidates = splitCandidates(rawText)

  const matchedIngredients = ingredientCatalog
    .map((ingredient) => {
      const matchedAlias = [ingredient.name, ...ingredient.aliases].find((alias) =>
        normalizedText.includes(normalize(alias)),
      )

      return matchedAlias
        ? {
            ...ingredient,
            matchedAlias,
            riskMeta: riskLevels[ingredient.risk],
          }
        : null
    })
    .filter(Boolean)
    .sort((a, b) => b.riskMeta.score - a.riskMeta.score)

  const highestScore = matchedIngredients[0]?.riskMeta.score ?? 0
  const overallRisk =
    highestScore >= 3 ? 'high' : highestScore === 2 ? 'medium' : matchedIngredients.length ? 'low' : 'unknown'

  const riskCounts = matchedIngredients.reduce(
    (counts, ingredient) => ({
      ...counts,
      [ingredient.risk]: counts[ingredient.risk] + 1,
    }),
    { low: 0, medium: 0, high: 0 },
  )

  return {
    productType,
    candidates,
    matchedIngredients,
    unmatchedCandidates: candidates.filter(
      (candidate) =>
        !matchedIngredients.some((ingredient) =>
          normalize(candidate).includes(normalize(ingredient.matchedAlias)),
        ),
    ),
    overallRisk,
    riskCounts,
  }
}

export const buildSummary = (analysis) => {
  if (analysis.overallRisk === 'unknown') {
    return '인식된 성분이 부족합니다. 라벨의 성분 영역을 더 선명하게 입력하거나 직접 성분명을 추가해 주세요.'
  }

  if (analysis.overallRisk === 'high') {
    return '고위험 성분이 포함되어 있습니다. 사용 전 환기, 보호장비, 혼합 금지 조건을 먼저 확인하세요.'
  }

  if (analysis.overallRisk === 'medium') {
    return '주의가 필요한 성분이 있습니다. 민감 계층 사용 여부와 제품 사용 환경을 함께 확인하세요.'
  }

  return '현재 입력된 성분 기준으로는 전반적인 위험도가 낮습니다. 그래도 표시된 사용량과 헹굼 안내를 지켜 주세요.'
}
