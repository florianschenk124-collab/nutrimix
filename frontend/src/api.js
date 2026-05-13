/**
 * NutrientMixer API Client
 *
 * Sendet X-Lang Header mit jeder Anfrage, damit das Backend
 * Warnungen, Schritte und Beschreibungen in der richtigen Sprache liefert.
 */

const BASE = ''

// Aktuelle Sprache – wird von useI18n gesetzt
let _currentLang = 'en'
export const setApiLang = (lang) => { _currentLang = lang }
export const getApiLang = () => _currentLang

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Lang': _currentLang,
      ...options.headers,
    },
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API ${res.status}: ${body}`)
  }
  if (res.status === 204) return null
  return res.json()
}

// ── Rezepte ──
export const fetchRecipes = () => request('/api/recipes')
export const fetchRecipe = (name) => request(`/api/recipes/${encodeURIComponent(name)}`)
export const createRecipe = (data) => request('/api/recipes', { method: 'POST', body: JSON.stringify(data) })
export const deleteRecipe = (name) => request(`/api/recipes/${encodeURIComponent(name)}`, { method: 'DELETE' })

// ── Wasserprofile ──
export const fetchWaterProfiles = () => request('/api/water-profiles')
export const createWaterProfile = (data) => request('/api/water-profiles', { method: 'POST', body: JSON.stringify(data) })
export const deleteWaterProfile = (name) => request(`/api/water-profiles/${encodeURIComponent(name)}`, { method: 'DELETE' })

// ── Salze ──
export const fetchSalts = () => request('/api/salts')
export const fetchPremixes = () => request('/api/salts/premixes')
export const fetchIons = () => request('/api/ions')

// ── Rechner ──
export const calculate = (params) => request('/api/calculate', { method: 'POST', body: JSON.stringify(params) })

// ── Tools ──
export const fetchAcids = () => request('/api/tools/ph/acids')
export const fetchBases = () => request('/api/tools/ph/bases')
export const calcPhCorrection = (params) => request('/api/tools/ph', { method: 'POST', body: JSON.stringify(params) })
export const calcDilution = (params) => request('/api/tools/dilution', { method: 'POST', body: JSON.stringify(params) })
export const calcReverse = (params) => request('/api/tools/reverse', { method: 'POST', body: JSON.stringify(params) })
export const checkCompatibility = (formulas) => request('/api/tools/compatibility', { method: 'POST', body: JSON.stringify({ salt_formulas: formulas }) })
export const fetchCompatibilityMatrix = () => request('/api/tools/compatibility/matrix')

// ── Stammdaten ──
export const fetchPlants = () => request('/api/plants')
export const fetchGrowthPlans = () => request('/api/growth-plans')
export const fetchSettings = () => request('/api/settings')
export const updateSettings = (data) => request('/api/settings', { method: 'PUT', body: JSON.stringify(data) })

// ── Lokalisierung ──
export const fetchLocale = (lang) => request(`/api/locales/${lang}`)
