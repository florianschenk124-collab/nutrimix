import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchSettings, updateSettings } from '../api'

export default function Settings() {
  const { t, setLang } = useI18n()
  const [settings, setSettings] = useState(null)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => { fetchSettings().then(setSettings) }, [])

  const set = (key, val) => setSettings(prev => ({ ...prev, [key]: val }))

  const save = async () => {
    setSaving(true)
    try {
      await updateSettings(settings)
      setLang(settings.language)
      setMsg(t('settings.saved'))
      setTimeout(() => setMsg(''), 3000)
    } catch (e) { setMsg('Fehler: ' + e.message) }
    setSaving(false)
  }

  if (!settings) return <div className="placeholder-view"><span className="spinner" /></div>

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('settings.title')}</h1>
        <p className="page-subtitle">{t('settings.subtitle')}</p>
      </div>

      {/* Sprache */}
      <div className="card">
        <div className="card-title">{t('settings.card_lang')}</div>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('settings.language')}</label>
            <select className="form-select" value={settings.language} onChange={e => set('language', e.target.value)}>
              <option value="de">🇩🇪 Deutsch</option>
              <option value="en">🇬🇧 English</option>
            </select>
          </div>
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>{t('settings.lang_hint')}</div>
      </div>

      {/* Allgemein */}
      <div className="card">
        <div className="card-title">{t('settings.card_general')}</div>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('settings.default_unit')}</label>
            <select className="form-select" value={settings.default_unit} onChange={e => set('default_unit', e.target.value)}>
              <option value="mg/L (ppm)">mg/L (ppm)</option>
              <option value="mmol/L">mmol/L</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">{t('settings.default_vol')}</label>
            <input className="form-input" type="number" value={settings.default_volume} onChange={e => set('default_volume', Number(e.target.value))} />
          </div>
          <div className="form-group">
            <label className="form-label">{t('settings.default_conc')}</label>
            <input className="form-input" type="number" value={settings.default_concentrate_factor} onChange={e => set('default_concentrate_factor', Number(e.target.value))} />
          </div>
        </div>
      </div>

      {/* EC-Schätzung */}
      <div className="card">
        <div className="card-title">{t('settings.card_ec')}</div>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('settings.ec_method')}</label>
            <select className="form-select" value={settings.ec_method} onChange={e => set('ec_method', e.target.value)}>
              <option value="ionic">Ionenspezifisch (genauer)</option>
              <option value="simple">TDS-basiert (schnell)</option>
            </select>
          </div>
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6, whiteSpace: 'pre-line' }}>{t('settings.ec_hint')}</div>
      </div>

      {/* Standard-Salzauswahl */}
      <div className="card">
        <div className="card-title">{t('settings.card_salts')}</div>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Fe-Chelat:</label>
            <select className="form-select" value={settings.fe_chelate} onChange={e => set('fe_chelate', e.target.value)}>
              <option value="Fe-DTPA">Fe-DTPA (11%)</option>
              <option value="Fe-EDTA">Fe-EDTA (13%)</option>
              <option value="Fe-EDDHA">Fe-EDDHA (6%)</option>
              <option value="Fe-HBED">Fe-HBED (6%)</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">NH₄-Quelle:</label>
            <select className="form-select" value={settings.nh4_source} onChange={e => set('nh4_source', e.target.value)}>
              <option value="NH4NO3">NH₄NO₃</option>
              <option value="MAP">MAP (NH₄H₂PO₄)</option>
              <option value="DAP">DAP ((NH₄)₂HPO₄)</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">P-Quelle:</label>
            <select className="form-select" value={settings.p_source} onChange={e => set('p_source', e.target.value)}>
              <option value="KH2PO4">KH₂PO₄</option>
              <option value="MAP">MAP</option>
              <option value="H3PO4">H₃PO₄</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">{t('c.dose_ratio')}</label>
            <select className="form-select" value={settings.dose_ratio} onChange={e => set('dose_ratio', e.target.value)}>
              <option value="1:1">1:1</option>
              <option value="2:3">2:3</option>
              <option value="3:2">3:2</option>
            </select>
          </div>
        </div>
      </div>

      {/* Regelwerk */}
      <div className="card">
        <div className="card-title">{t('settings.card_rules')}</div>
        <pre style={{
          fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-secondary)',
          whiteSpace: 'pre-wrap', background: 'var(--bg-input)', padding: 14,
          borderRadius: 'var(--radius-sm)', lineHeight: 1.6,
        }}>
          {t('settings.rules_text')}
        </pre>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button className="btn btn-primary" onClick={save} disabled={saving}>{t('settings.btn_save')}</button>
        {msg && <span style={{ fontSize: 13, color: 'var(--success)' }}>{msg}</span>}
      </div>
    </div>
  )
}
