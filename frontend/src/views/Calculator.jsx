import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes, fetchWaterProfiles, fetchPremixes, calculate } from '../api'

export default function Calculator() {
  const { t, td, sd } = useI18n()
  const [recipes, setRecipes] = useState([])
  const [waterProfiles, setWaterProfiles] = useState([])
  const [premixes, setPremixes] = useState([])
  const [params, setParams] = useState({
    recipe_name: '', water_profile_name: 'Osmosewasser', volume_l: 1000,
    concentrate_factor: 100, fe_chelate: 'Fe-DTPA', nh4_source: 'NH4NO3',
    p_source: 'KH2PO4', micro_source: 'individual', dose_ratio: '1:1',
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sections, setSections] = useState({ target_actual: true, summary: true, ratios: true, solubility: false, warnings: true, protocol: false })

  useEffect(() => {
    Promise.all([fetchRecipes(), fetchWaterProfiles(), fetchPremixes()]).then(([r, w, p]) => {
      setRecipes(r); setWaterProfiles(w); setPremixes(p)
      if (r.length > 0 && !params.recipe_name) setParams(prev => ({ ...prev, recipe_name: r[0].name }))
    }).catch(e => setError(e.message))
  }, [])

  const set = (k, v) => setParams(prev => ({ ...prev, [k]: v }))
  const toggle = (k) => setSections(prev => ({ ...prev, [k]: !prev[k] }))
  const doCalc = async () => {
    setLoading(true); setError(null)
    try { setResult(await calculate(params)) } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  const dc = (v) => Math.abs(v) <= 2 ? 'delta-ok' : Math.abs(v) <= 10 ? 'delta-warn' : 'delta-bad'
  const fmt = (v, d = 2) => v != null ? Number(v).toFixed(d) : '–'

  return (<div>
    <div className="page-header"><h1 className="page-title">{t('calc.title')}</h1><p className="page-subtitle">{t('calc.subtitle')}</p></div>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <div className="card"><div className="card-title">{t('calc.card_recipe')} & {t('calc.card_water')}</div>
        <div className="form-grid">
          <div className="form-group"><label className="form-label">{t('c.recipe')}</label>
            <select className="form-select" value={params.recipe_name} onChange={e => set('recipe_name', e.target.value)}>
              {recipes.map(r => <option key={r.name} value={r.name}>{r.is_custom ? '⭐ ' : ''}{td(r.name)}</option>)}</select></div>
          <div className="form-group"><label className="form-label">{t('c.water_profile')}</label>
            <select className="form-select" value={params.water_profile_name} onChange={e => set('water_profile_name', e.target.value)}>
              {waterProfiles.map(w => <option key={w.name} value={w.name}>{td(w.name)}</option>)}</select></div></div></div>
      <div className="card"><div className="card-title">{t('calc.card_params')}</div>
        <div className="form-grid">
          <div className="form-group"><label className="form-label">{t('c.volume_l')}</label><input className="form-input" type="number" value={params.volume_l} onChange={e => set('volume_l', Number(e.target.value))} /></div>
          <div className="form-group"><label className="form-label">{t('c.conc_factor')}</label><input className="form-input" type="number" value={params.concentrate_factor} onChange={e => set('concentrate_factor', Number(e.target.value))} /></div>
          <div className="form-group"><label className="form-label">{t('c.dose_ratio')}</label>
            <select className="form-select" value={params.dose_ratio} onChange={e => set('dose_ratio', e.target.value)}>
              <option value="1:1">1:1</option><option value="2:3">2:3</option><option value="3:2">3:2</option></select></div></div></div></div>
    <div className="card"><div className="card-title">{t('calc.card_salts')}</div>
      <div className="form-grid">
        <div className="form-group"><label className="form-label">{t('calc.fe_label')}</label>
          <select className="form-select" value={params.fe_chelate} onChange={e => set('fe_chelate', e.target.value)}>
            <option value="Fe-DTPA">Fe-DTPA (11%) – pH ≤7.0</option><option value="Fe-EDTA">Fe-EDTA (13%) – pH ≤6.0</option>
            <option value="Fe-EDDHA">Fe-EDDHA (6%) – pH ≤11</option><option value="Fe-HBED">Fe-HBED (6%) – pH ≤12</option>
            <option value="from_premix">{t('calc.fe_from_premix')}</option>
            <option value="none">{t('calc.fe_none')}</option></select></div>
        <div className="form-group"><label className="form-label">{t('calc.nh4_label')}</label>
          <select className="form-select" value={params.nh4_source} onChange={e => set('nh4_source', e.target.value)}>
            <option value="NH4NO3">NH₄NO₃</option><option value="MAP">MAP – NH₄H₂PO₄ (+ P)</option><option value="DAP">DAP – (NH₄)₂HPO₄ (+ P)</option></select></div>
        <div className="form-group"><label className="form-label">{t('calc.p_label')}</label>
          <select className="form-select" value={params.p_source} onChange={e => set('p_source', e.target.value)}>
            <option value="KH2PO4">KH₂PO₄ (+ K)</option><option value="MAP">MAP – NH₄H₂PO₄ (+ NH₄)</option><option value="H3PO4">H₃PO₄ 85%</option></select></div>
        <div className="form-group"><label className="form-label">{t('settings.micro_nutrients')}</label>
          <select className="form-select" value={params.micro_source} onChange={e => set('micro_source', e.target.value)}>
            <option value="individual">{t('b.micro_individual')}</option>
            {premixes.map(p => <option key={p.formula} value={p.formula}>{p.name}</option>)}</select></div></div>
      <div className="alert alert-info" style={{ marginTop: 10, fontSize: 11 }}>{t('calc.auto_info')}</div></div>
    <div style={{ marginBottom: 24 }}><button className="btn btn-primary" onClick={doCalc} disabled={loading || !params.recipe_name}>
      {loading ? <span className="spinner" /> : null} {t('calc.btn')}</button>
      {error && <span style={{ color: 'var(--error)', marginLeft: 16, fontSize: 13 }}>{error}</span>}</div>

    {result && (<div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <TankCard t={t} td={td} sd={sd} label={t('calc.tank_a')} tank="a" salts={result.tank_a} />
        <TankCard t={t} td={td} sd={sd} label={t('calc.tank_b')} tank="b" salts={result.tank_b} /></div>
      <CC title={t('calc.summary')} open={sections.summary} onToggle={() => toggle('summary')}>
        <div className="stats-grid">
          <SI label={t('c.ec_estimated')} value={`${fmt(result.ec_ionic)} mS/cm`} className={result.ec_rating?.includes('✅') ? 'success' : 'warning'} />
          <SI label={t('calc.max_factor')} value={`${fmt(result.max_concentrate_factor, 0)}x`} />
          <SI label={t('costs.title')} value={result.total_cost > 0 ? `${fmt(result.total_cost, 2)} €` : '–'} />
          <SI label={t('calc.dose_label')} value={`${result.dose_ratio_a}:${result.dose_ratio_b}`} /></div></CC>
      <CC title={t('calc.target_actual')} open={sections.target_actual} onToggle={() => toggle('target_actual')}>
        <table className="result-table"><thead><tr><th>{t('calc.col_ion')}</th><th style={{textAlign:'right'}}>{t('b.target')} mg/L</th>
          <th style={{textAlign:'right'}}>{t('calc.col_water')}</th><th style={{textAlign:'right'}}>{t('b.actual')} mg/L</th>
          <th style={{textAlign:'right'}}>{t('calc.col_delta')}</th></tr></thead>
          <tbody>{['NO3','NH4','H2PO4','K','Ca','Mg','SO4','Fe','Mn','Zn','Cu','B','Mo']
            .filter(i=>(result.target_mg[i]||0)>0||(result.achieved_mg[i]||0)>0).map(i=>{
              const tg=result.target_mg[i]||0,w=result.water_mg[i]||0,a=result.achieved_mg[i]||0,d=result.delta_mg[i]||0
              return(<tr key={i}><td style={{fontWeight:600}}>{i}</td><td className="num">{fmt(tg)}</td>
                <td className="num" style={{color:'var(--text-muted)'}}>{w>0?fmt(w):'–'}</td><td className="num">{fmt(a)}</td>
                <td className={`num ${dc(d)}`}>{d>0?'+':''}{fmt(d)}</td></tr>)})}</tbody></table></CC>
      <CC title={t('calc.ratios')} open={sections.ratios} onToggle={() => toggle('ratios')}>
        {result.ratios.map(r=>(<div className="ratio-row" key={r.name}><span className="ratio-name">{r.name}</span>
          <div className="ratio-bar-container"><div className="ratio-bar-actual" style={{width:`${Math.min(100,(r.actual/(r.target_max*1.5))*100)}%`,background:r.is_ok?'var(--success)':'var(--warning)'}}/></div>
          <span className="ratio-value" style={{color:r.is_ok?'var(--success)':'var(--warning)'}}>{fmt(r.actual,2)}{r.unit}</span>
          <span className="ratio-status">{r.is_ok?'✅':'⚠️'}</span></div>))}</CC>
      <CC title={t('calc.solubility')} open={sections.solubility} onToggle={() => toggle('solubility')}>
        <table className="result-table"><thead><tr><th>{t('calc.col_salt')}</th><th style={{textAlign:'right'}}>{t('calc.col_g_conc')}</th>
          <th style={{textAlign:'right'}}>{t('calc.col_solubility')}</th><th style={{textAlign:'right'}}>{t('calc.col_saturation')}</th><th>{t('calc.col_status')}</th></tr></thead>
          <tbody>{result.solubility_checks.map(c=>(<tr key={c.salt_name}><td>{sd(c.salt_name,c.formula||c.salt_name)}</td>
            <td className="num">{fmt(c.g_per_l_concentrate,1)}</td><td className="num">{fmt(c.solubility_limit,0)}</td>
            <td className="num" style={{color:c.saturation_pct>80?'var(--warning)':c.is_ok?'var(--text-primary)':'var(--error)'}}>{fmt(c.saturation_pct,1)}%</td>
            <td>{c.is_ok?(c.saturation_pct>70?'⚠️':'✅'):'⛔'}</td></tr>))}</tbody></table></CC>
      {(result.warnings.length>0||result.water_warnings.length>0||result.ab_warnings.length>0)&&(
        <CC title={t('calc.warnings')} open={sections.warnings} onToggle={() => toggle('warnings')}>
          {result.ab_warnings.length===0&&<div className="alert alert-success">{t('calc.ab_ok')}</div>}
          {[...result.water_warnings,...result.warnings,...result.ab_warnings].map((w,i)=>(<div className="alert alert-warning" key={i}>{w}</div>))}</CC>)}
      <CC title={t('calc.protocol')} open={sections.protocol} onToggle={() => toggle('protocol')}>
        {result.steps.map((s,i)=><div className="protocol-step" key={i}>{s}</div>)}</CC></div>)}</div>)
}
function TankCard({t,td,sd,label,tank,salts}){return(<div className="card"><div className="tank-header"><span className={`tank-badge tank-${tank}`}>{tank.toUpperCase()}</span><span className="tank-label">{label}</span></div>
  <table className="result-table"><thead><tr><th>{t('calc.col_salt')}</th><th style={{textAlign:'right'}}>{t('calc.col_g_l')}</th><th style={{textAlign:'right'}}>{t('calc.col_g_total')}</th><th style={{textAlign:'right'}}>{t('calc.col_g_tank')}</th></tr></thead>
    <tbody>{salts.map(s=>(<tr key={s.salt_formula}><td>{sd(s.salt_name,s.salt_formula)}</td><td className="num">{Number(s.g_per_l).toFixed(4)}</td><td className="num">{Number(s.g_total).toFixed(1)}</td><td className="num" style={{fontWeight:600}}>{Number(s.g_concentrate).toFixed(1)}</td></tr>))}</tbody></table></div>)}
function SI({label,value,className=''}){return <div className="stat-item"><div className="stat-label">{label}</div><div className={`stat-value ${className}`}>{value}</div></div>}
function CC({title,open,onToggle,children}){return(<div className="card"><div className="collapsible-header" onClick={onToggle}><div className="card-title" style={{marginBottom:0}}>{title}</div><span className={`collapse-icon ${open?'open':''}`}>▼</span></div>{open&&<div style={{marginTop:14}}>{children}</div>}</div>)}
