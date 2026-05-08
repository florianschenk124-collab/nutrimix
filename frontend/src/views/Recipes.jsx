import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes, deleteRecipe } from '../api'

const MACRO_IONS = ['NO3', 'NH4', 'H2PO4', 'K', 'Ca', 'Mg', 'SO4']
const MICRO_IONS = ['Fe', 'Mn', 'Zn', 'Cu', 'B', 'Mo']

export default function Recipes() {
  const { t } = useI18n()
  const [recipes, setRecipes] = useState([])
  const [selected, setSelected] = useState(null)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const load = () => {
    fetchRecipes()
      .then(r => { setRecipes(r); if (r.length > 0 && !selected) setSelected(r[0]) })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const filtered = recipes.filter(r => {
    if (filter === 'custom') return r.is_custom
    if (filter === 'standard') return !r.is_custom
    return true
  })

  const handleDelete = async (name) => {
    await deleteRecipe(name)
    setSelected(null)
    load()
  }

  const fmt = (v, d = 2) => v > 0 ? Number(v).toFixed(d) : '–'

  if (loading) return <div className="placeholder-view"><span className="spinner" /></div>

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('recipes.title')}</h1>
        <p className="page-subtitle">{t('recipes.subtitle')}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 16 }}>
        <div className="card" style={{ padding: 8 }}>
          {/* Filter */}
          <div style={{ display: 'flex', gap: 4, padding: '4px 6px', marginBottom: 4 }}>
            {[
              { key: 'all', label: t('recipes.filter_all') },
              { key: 'standard', label: t('recipes.filter_standard') },
              { key: 'custom', label: t('recipes.filter_custom') },
            ].map(f => (
              <button key={f.key} className="btn" style={{
                padding: '3px 8px', fontSize: 10,
                background: filter === f.key ? 'var(--accent-bg-hover)' : 'transparent',
                color: filter === f.key ? 'var(--text-accent)' : 'var(--text-muted)',
                border: 'none',
              }} onClick={() => setFilter(f.key)}>{f.label}</button>
            ))}
          </div>
          {filtered.map(r => (
            <button key={r.name}
              className={`nav-item ${selected?.name === r.name ? 'active' : ''}`}
              onClick={() => setSelected(r)} style={{ width: '100%', margin: '1px 0' }}>
              <span className="nav-icon">{r.is_custom ? '⭐' : '📋'}</span>
              <span>{r.name}</span>
            </button>
          ))}
        </div>

        {selected && (
          <div>
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div className="card-title">📋 {selected.name}</div>
                {selected.is_custom && (
                  <button className="btn" style={{ color: 'var(--error)', fontSize: 12, padding: '4px 10px' }}
                    onClick={() => handleDelete(selected.name)}>🗑</button>
                )}
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>{selected.description}</p>
              <div className="stats-grid" style={{ marginBottom: 16 }}>
                <StatItem label="pH" value={`${selected.ph_min} – ${selected.ph_max}`} />
                <StatItem label="EC" value={selected.ec_target > 0 ? `${selected.ec_target} mS/cm` : '–'} />
                <StatItem label="N gesamt" value={`${fmt(selected.total_n)} mg/L`} />
                {selected.source && <StatItem label="Quelle" value={selected.source} />}
              </div>
              {selected.suitable_plants.length > 0 && (
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>🌱 {selected.suitable_plants.join(', ')}</div>
              )}
            </div>

            <div className="card">
              <div className="card-title">Makronährstoffe (mg/L)</div>
              <table className="result-table">
                <thead><tr><th>Ion</th><th style={{ textAlign: 'right' }}>mg/L</th><th style={{ textAlign: 'right' }}>mmol/L</th></tr></thead>
                <tbody>
                  {MACRO_IONS.filter(ion => (selected.ions_mg[ion] || 0) > 0).map(ion => (
                    <tr key={ion}>
                      <td style={{ fontWeight: 600 }}>{ion}</td>
                      <td className="num">{fmt(selected.ions_mg[ion])}</td>
                      <td className="num" style={{ color: 'var(--text-secondary)' }}>{fmt(selected.ions_mmol[ion], 4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card">
              <div className="card-title">Mikronährstoffe (mg/L)</div>
              <table className="result-table">
                <thead><tr><th>Ion</th><th style={{ textAlign: 'right' }}>mg/L</th><th style={{ textAlign: 'right' }}>mmol/L</th></tr></thead>
                <tbody>
                  {MICRO_IONS.filter(ion => (selected.ions_mg[ion] || 0) > 0).map(ion => (
                    <tr key={ion}>
                      <td style={{ fontWeight: 600 }}>{ion}</td>
                      <td className="num">{fmt(selected.ions_mg[ion])}</td>
                      <td className="num" style={{ color: 'var(--text-secondary)' }}>{fmt(selected.ions_mmol[ion], 4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatItem({ label, value }) {
  return <div className="stat-item"><div className="stat-label">{label}</div><div className="stat-value" style={{ fontSize: 14 }}>{value}</div></div>
}
