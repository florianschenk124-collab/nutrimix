import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchWaterProfiles, createWaterProfile, deleteWaterProfile } from '../api'

const WATER_IONS = [
  { key: 'ca', label: 'Ca²⁺' }, { key: 'mg', label: 'Mg²⁺' },
  { key: 'na', label: 'Na⁺' }, { key: 'k', label: 'K⁺' },
  { key: 'cl', label: 'Cl⁻' }, { key: 'so4', label: 'SO₄²⁻' },
  { key: 'hco3', label: 'HCO₃⁻' }, { key: 'no3', label: 'NO₃⁻' },
  { key: 'fe', label: 'Fe' },
]

const EMPTY = { name: '', ca: 0, mg: 0, na: 0, k: 0, cl: 0, so4: 0, hco3: 0, no3: 0, fe: 0, ec: 0, ph: 7.0 }

export default function WaterProfiles() {
  const { t } = useI18n()
  const [profiles, setProfiles] = useState([])
  const [selected, setSelected] = useState(null)
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  const load = () => {
    fetchWaterProfiles().then(p => {
      setProfiles(p)
      if (!selected && p.length > 0) setSelected(p[0])
    })
  }
  useEffect(load, [])

  const selectP = (p) => { setSelected(p); setEditing(null); setMsg('') }
  const startEdit = (p) => setEditing({ ...p })
  const startNew = () => { setEditing({ ...EMPTY }); setSelected(null) }
  const setF = (k, v) => setEditing(prev => ({ ...prev, [k]: v }))

  const save = async () => {
    if (!editing.name.trim()) return
    setSaving(true)
    try {
      await createWaterProfile(editing)
      setMsg(t('water.saved'))
      setEditing(null)
      load()
    } catch (e) {
      setMsg(t('gen.error') + ': ' + e.message)
    }
    setSaving(false)
  }

  const remove = async (name) => {
    await deleteWaterProfile(name)
    setSelected(null)
    load()
  }

  const fmt = (v) => v > 0 ? Number(v).toFixed(2) : '–'

  const renderEditor = () => (
    <div className="card">
      <div className="card-title">
        {editing.name ? `✏️ ${editing.name}` : `➕ ${t('water.new')}`}
      </div>
      <div className="form-grid" style={{ marginBottom: 16 }}>
        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
          <label className="form-label">{t('water.name')}</label>
          <input className="form-input" value={editing.name} placeholder={t('water.name_ph')}
            onChange={e => setF('name', e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">{t('water.ec')}</label>
          <input className="form-input" type="number" step="0.01" value={editing.ec}
            onChange={e => setF('ec', Number(e.target.value))} />
        </div>
        <div className="form-group">
          <label className="form-label">{t('water.ph')}</label>
          <input className="form-input" type="number" step="0.1" value={editing.ph}
            onChange={e => setF('ph', Number(e.target.value))} />
        </div>
      </div>
      <div className="card-title" style={{ fontSize: 12 }}>{t('water.ions_header')}</div>
      <div className="form-grid">
        {WATER_IONS.map(({ key, label }) => (
          <div className="form-group" key={key}>
            <label className="form-label">{label}</label>
            <input className="form-input" type="number" step="0.1" value={editing[key]}
              onChange={e => setF(key, Number(e.target.value))} />
          </div>
        ))}
      </div>
      <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
        <button className="btn btn-primary" onClick={save} disabled={saving}>{t('water.btn_save')}</button>
        <button className="btn" style={{ color: 'var(--text-secondary)' }} onClick={() => setEditing(null)}>
          {t('water.cancel')}
        </button>
        {msg && <span style={{ fontSize: 12, color: 'var(--success)' }}>{msg}</span>}
      </div>
    </div>
  )

  const renderDetail = () => (
    <div>
      <div className="card">
        <div className="card-title">💧 {selected.name}</div>
        <div className="stats-grid" style={{ marginBottom: 16 }}>
          <div className="stat-item">
            <div className="stat-label">EC</div>
            <div className="stat-value" style={{ fontSize: 14 }}>{selected.ec} mS/cm</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">pH</div>
            <div className="stat-value" style={{ fontSize: 14 }}>{selected.ph}</div>
          </div>
        </div>
        <table className="result-table">
          <thead><tr><th>{t('calc.col_ion')}</th><th style={{ textAlign: 'right' }}>{t('gen.mg_l')}</th></tr></thead>
          <tbody>
            {WATER_IONS.filter(({ key }) => selected[key] > 0).map(({ key, label }) => (
              <tr key={key}><td>{label}</td><td className="num">{fmt(selected[key])}</td></tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
          <button className="btn btn-primary" style={{ padding: '7px 16px' }}
            onClick={() => startEdit(selected)}>{t('water.btn_edit')}</button>
          {selected.is_custom && (
            <button className="btn" style={{ color: 'var(--error)' }}
              onClick={() => remove(selected.name)}>{t('water.btn_delete')}</button>
          )}
        </div>
      </div>
    </div>
  )

  const renderPlaceholder = () => (
    <div className="placeholder-view">
      <span className="placeholder-text">{t('water.select_hint')}</span>
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('water.title')}</h1>
        <p className="page-subtitle">{t('water.subtitle')}</p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 16 }}>
        <div className="card" style={{ padding: 8 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 10px' }}>
            <div className="card-title" style={{ marginBottom: 0 }}>{t('water.card_list')}</div>
            <button className="btn btn-primary" style={{ padding: '5px 12px', fontSize: 12 }} onClick={startNew}>➕</button>
          </div>
          {profiles.map(p => (
            <button key={p.name}
              className={`nav-item ${selected?.name === p.name ? 'active' : ''}`}
              onClick={() => selectP(p)}
              style={{ width: '100%', margin: '1px 0' }}>
              <span className="nav-icon">{p.is_custom ? '⭐' : '💧'}</span>
              <span style={{ fontSize: 12 }}>{p.name}</span>
            </button>
          ))}
        </div>
        <div>
          {editing ? renderEditor() : selected ? renderDetail() : renderPlaceholder()}
        </div>
      </div>
    </div>
  )
}
