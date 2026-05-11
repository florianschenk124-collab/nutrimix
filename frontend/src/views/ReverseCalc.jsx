import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchSalts, calcReverse } from '../api'

export default function ReverseCalc() {
  const { t, td } = useI18n()
  const [allSalts, setAllSalts] = useState([])
  const [entries, setEntries] = useState([])
  const [volumeL, setVolumeL] = useState(100)
  const [addFormula, setAddFormula] = useState('')
  const [addGrams, setAddGrams] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchSalts().then(s => {
      const filtered = s.filter(x => !x.is_premix)
      setAllSalts(filtered)
      if (filtered.length > 0) setAddFormula(filtered[0].formula)
    })
  }, [])

  const addSalt = () => {
    if (!addFormula || !addGrams || Number(addGrams) <= 0) return
    const salt = allSalts.find(s => s.formula === addFormula)
    if (!salt) return
    setEntries(prev => [...prev, {
      salt_formula: addFormula,
      salt_name: salt.name,
      grams: Number(addGrams),
    }])
    setAddGrams('')
  }

  const removeSalt = (i) => setEntries(prev => prev.filter((_, idx) => idx !== i))

  const doCalc = async () => {
    if (entries.length === 0) return
    setLoading(true)
    try {
      const res = await calcReverse({
        salts: entries.map(e => ({ salt_formula: e.salt_formula, grams: e.grams })),
        volume_l: volumeL,
      })
      setResult(res)
    } catch (e) {
      setResult(null)
    }
    setLoading(false)
  }

  const fmt = (v, d = 2) => v != null ? Number(v).toFixed(d) : '–'

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('rev.title')}</h1>
        <p className="page-subtitle">{t('rev.subtitle')}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Volumen */}
        <div className="card">
          <div className="card-title">{t('rev.card_volume')}</div>
          <div className="form-group">
            <label className="form-label">{t('rev.end_volume')}</label>
            <input className="form-input" type="number" value={volumeL}
              onChange={e => setVolumeL(Number(e.target.value))} />
          </div>
        </div>

        {/* Salz hinzufügen */}
        <div className="card">
          <div className="card-title">{t('rev.card_add')}</div>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">{t('rev.salt')}</label>
              <select className="form-select" value={addFormula}
                onChange={e => setAddFormula(e.target.value)}>
                {allSalts.map(s => (
                  <option key={s.formula} value={s.formula}>{td(s.name)}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">{t('rev.grams')}</label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input className="form-input" type="number" step="0.1" value={addGrams}
                  onChange={e => setAddGrams(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && addSalt()} />
                <button className="btn btn-primary" style={{ padding: '8px 14px' }} onClick={addSalt}>
                  ➕
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Eingewogene Salze */}
      {entries.length > 0 && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="card-title" style={{ marginBottom: 0 }}>{t('rev.card_list')}</div>
            <button className="btn" style={{ color: 'var(--error)', fontSize: 12, padding: '4px 10px' }}
              onClick={() => setEntries([])}>
              {t('rev.btn_clear')}
            </button>
          </div>
          <table className="result-table" style={{ marginTop: 10 }}>
            <thead>
              <tr>
                <th>Salz</th>
                <th style={{ textAlign: 'right' }}>Gramm</th>
                <th style={{ textAlign: 'right' }}>g/L</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e, i) => (
                <tr key={i}>
                  <td>{td(e.salt_name)}</td>
                  <td className="num">{fmt(e.grams, 1)}</td>
                  <td className="num" style={{ color: 'var(--text-secondary)' }}>
                    {fmt(e.grams / volumeL, 4)}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button onClick={() => removeSalt(i)}
                      style={{ background: 'none', border: 'none', color: 'var(--error)', cursor: 'pointer', fontSize: 14 }}>
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginBottom: 24 }}>
        <button className="btn btn-primary" onClick={doCalc}
          disabled={loading || entries.length === 0}>
          {loading ? <span className="spinner" /> : null}
          {t('rev.btn')}
        </button>
      </div>

      {/* Ergebnis */}
      {result && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Ionenkonzentrationen */}
            <div className="card">
              <div className="card-title">{t('rev.card_ions')}</div>
              <table className="result-table">
                <thead>
                  <tr>
                    <th>Ion</th>
                    <th style={{ textAlign: 'right' }}>mg/L</th>
                    <th style={{ textAlign: 'right' }}>mmol/L</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(result.ion_mg)
                    .filter(([, v]) => v > 0.01)
                    .sort((a, b) => b[1] - a[1])
                    .map(([ion, mg]) => (
                      <tr key={ion}>
                        <td style={{ fontWeight: 600 }}>{ion}</td>
                        <td className="num">{fmt(mg)}</td>
                        <td className="num" style={{ color: 'var(--text-secondary)' }}>
                          {fmt(result.ion_mmol[ion] || 0, 4)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            {/* Verhältnisse + EC */}
            <div className="card">
              <div className="card-title">{t('rev.card_ratios')}</div>
              <div className="stat-item" style={{ marginBottom: 14 }}>
                <div className="stat-label">EC (geschätzt)</div>
                <div className="stat-value">{fmt(result.ec_estimated)} mS/cm</div>
              </div>

              {result.ratios.map(r => (
                <div className="ratio-row" key={r.name}>
                  <span className="ratio-name">{r.name}</span>
                  <div className="ratio-bar-container">
                    <div className="ratio-bar-actual" style={{
                      width: `${Math.min(100, (r.actual / (r.target_max * 1.5)) * 100)}%`,
                      background: r.is_ok ? 'var(--success)' : 'var(--warning)',
                    }} />
                  </div>
                  <span className="ratio-value" style={{ color: r.is_ok ? 'var(--success)' : 'var(--warning)' }}>
                    {fmt(r.actual, 2)}{r.unit}
                  </span>
                  <span className="ratio-status">{r.is_ok ? '✅' : '⚠️'}</span>
                </div>
              ))}

              {result.closest_recipe && (
                <div className="alert alert-info" style={{ marginTop: 14 }}>
                  📋 Ähnlichstes Rezept: <strong>{result.closest_recipe}</strong>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
