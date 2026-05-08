/**
 * NutrientMixer API Client
 *
 * Alle Backend-Aufrufe an die FastAPI-Instanz.
 * Im Dev-Modus läuft der Proxy über Vite (port 3000 → 8000).
 */

const BASE = ''  // Vite proxy handles /api → backend

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API ${res.status}: ${body}`)
  }
  if (res.status === 204) return null
  return res.json()
}

// ── Rezepte ──────────────────────────────────────────────────

export const fetchRecipes = () => request('/api/recipes')
export const fetchRecipe = (name) => request(`/api/recipes/${encodeURIComponent(name)}`)
export const createRecipe = (data) => request('/api/recipes', { method: 'POST', body: JSON.stringify(data) })
export const deleteRecipe = (name) => request(`/api/recipes/${encodeURIComponent(name)}`, { method: 'DELETE' })

// ── Wasserprofile ────────────────────────────────────────────

export const fetchWaterProfiles = () => request('/api/water-profiles')
export const createWaterProfile = (data) => request('/api/water-profiles', { method: 'POST', body: JSON.stringify(data) })
export const deleteWaterProfile = (name) => request(`/api/water-profiles/${encodeURIComponent(name)}`, { method: 'DELETE' })

// ── Salze ────────────────────────────────────────────────────

export const fetchSalts = () => request('/api/salts')
export const fetchPremixes = () => request('/api/salts/premixes')
export const fetchIons = () => request('/api/ions')

// ── Rechner (Solver) ─────────────────────────────────────────

export const calculate = (params) => request('/api/calculate', {
  method: 'POST',
  body: JSON.stringify(params),
})

// ── Tools ────────────────────────────────────────────────────

export const fetchAcids = () => request('/api/tools/ph/acids')
export const fetchBases = () => request('/api/tools/ph/bases')
export const calcPhCorrection = (params) => request('/api/tools/ph', { method: 'POST', body: JSON.stringify(params) })
export const calcDilution = (params) => request('/api/tools/dilution', { method: 'POST', body: JSON.stringify(params) })
export const calcReverse = (params) => request('/api/tools/reverse', { method: 'POST', body: JSON.stringify(params) })
export const checkCompatibility = (formulas) => request('/api/tools/compatibility', { method: 'POST', body: JSON.stringify({ salt_formulas: formulas }) })
export const fetchCompatibilityMatrix = () => request('/api/tools/compatibility/matrix')

// ── Stammdaten ───────────────────────────────────────────────

export const fetchPlants = () => request('/api/plants')
export const fetchGrowthPlans = () => request('/api/growth-plans')
export const fetchSettings = () => request('/api/settings')
export const updateSettings = (data) => request('/api/settings', { method: 'PUT', body: JSON.stringify(data) })

// ── Lokalisierung ────────────────────────────────────────────

export const fetchLocale = (lang) => request(`/api/locales/${lang}`)
