import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchSalts } from '../api'

const CATEGORIES = [
  { key: '', locale: 'salts.filter_all' },
  { key: 'macro', locale: 'salts.filter_macro' },
  { key: 'chelate', locale: 'salts.filter_chelate' },
  { key: 'micro', locale: 'salts.filter_micro' },
  { key: 'premix', locale: 'salts.filter_premix' },
]

export default function SaltDatabase() {
  const { t, td } = useI18n()
  const [salts, setSalts] = useState([])
  const [filter, setFilter] = useState('')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSalts().then(s => { setSalts(s); setLoading(false) })
  }, [])

  const filtered = salts.filter(s => {
    if (filter && s.category !== filter) return false
    if (search) {
      const q = search.toLowerCase()
      return s.name.toLowerCase().includes(q) || s.formula.toLowerCase().includes(q)
    }
    return true
  })

  const fmt = (v, d = 2) => v > 0 ? Number(v).toFixed(d) : '–'

  if (loading) return <div className="placeholder-view"><span className="spinner" /></div>

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('salts.title')}</h1>
        <p className="page-subtitle">{t('salts.subtitle')}</p>
      </div>

      {/* Filter */}
      <div className="card" style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        {CATEGORIES.map(c => (
          <button key={c.key} className="btn"
            style={{
              padding: '5px 14px', fontSize: 12,
              background: filter === c.key ? 'var(--accent-bg-hover)' : 'var(--bg-input)',
              color: filter === c.key ? 'var(--text-accent)' : 'var(--text-secondary)',
              border: `1px solid ${filter === c.key ? 'var(--accent)' : 'var(--border-subtle)'}`,
            }}
            onClick={() => setFilter(c.key)}>
            {t(c.locale)}
          </button>
        ))}
        <input className="form-input" placeholder={t('c.search_salt')} value={search}
          onChange={e => setSearch(e.target.value)} style={{ maxWidth: 200, marginLeft: 'auto' }} />
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{filtered.length} {t('salts.count')}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 350px' : '1fr', gap: 16 }}>
        <div className="card" style={{ padding: 0, overflow: 'auto' }}>
          <table className="result-table">
            <thead><tr>
              <th style={{ padding: '10px 14px' }}>{t('salts.col_name')}</th>
              <th style={{ padding: '10px 14px' }}>{t('salts.col_formula')}</th>
              <th style={{ padding: '10px 14px', textAlign: 'right' }}>{t('salts.col_molar')}</th>
              <th style={{ padding: '10px 14px', textAlign: 'right' }}>{t('salts.col_sol')}</th>
              <th style={{ padding: '10px 14px' }}>{t('salts.col_tank')}</th>
            </tr></thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.formula} onClick={() => setSelected(s)} style={{
                  cursor: 'pointer',
                  background: selected?.formula === s.formula ? 'var(--accent-bg)' : undefined,
                }}>
                  <td style={{ padding: '7px 14px', fontWeight: 500 }}>{sd(s.name,s.formula)}</td>
                  <td style={{ padding: '7px 14px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{s.formula}</td>
                  <td className="num" style={{ padding: '7px 14px' }}>{fmt(s.molar_mass)}</td>
                  <td className="num" style={{ padding: '7px 14px' }}>{fmt(s.solubility_20, 0)}</td>
                  <td style={{ padding: '7px 14px' }}>
                    <span className={`tank-badge tank-${s.tank.toLowerCase()}`} style={{ width: 22, height: 22, fontSize: 11 }}>{s.tank}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {selected && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="card-title" style={{ marginBottom: 4 }}>{selected.name}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>{selected.formula}</div>
              </div>
              <button onClick={() => setSelected(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 16 }}>✕</button>
            </div>
            <div className="stats-grid" style={{ marginBottom: 14 }}>
              <div className="stat-item"><div className="stat-label">{t('salts.det_molar')}</div><div className="stat-value" style={{ fontSize: 13 }}>{fmt(selected.molar_mass)} g/mol</div></div>
              <div className="stat-item"><div className="stat-label">{t('salts.det_sol')}</div><div className="stat-value" style={{ fontSize: 13 }}>{fmt(selected.solubility_20, 0)} g/L</div></div>
              <div className="stat-item"><div className="stat-label">Tank</div><div className="stat-value" style={{ fontSize: 13 }}>{selected.tank}</div></div>
              {selected.cost_per_kg > 0 && <div className="stat-item"><div className="stat-label">Preis</div><div className="stat-value" style={{ fontSize: 13 }}>{fmt(selected.cost_per_kg)} €/kg</div></div>}
            </div>
            <div className="card-title" style={{ fontSize: 11 }}>{t('salts.mg_per_g_salt')}</div>
            <table className="result-table">
              <thead><tr><th>Ion</th><th style={{ textAlign: 'right' }}>mg/g</th></tr></thead>
              <tbody>
                {Object.entries(selected.mg_ion_per_gram).filter(([, v]) => v > 0.001).sort((a, b) => b[1] - a[1]).map(([ion, mg]) => (
                  <tr key={ion}><td style={{ fontWeight: 600 }}>{ion}</td><td className="num">{fmt(mg, 3)}</td></tr>
                ))}
              </tbody>
            </table>
            {selected.notes && <div className="alert alert-info" style={{ marginTop: 12, fontSize: 12 }}>{td(selected.notes)}</div>}
          </div>
        )}
      </div>
    </div>
  )
}
