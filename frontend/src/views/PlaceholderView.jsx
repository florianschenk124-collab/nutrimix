import { useI18n } from '../hooks/useI18n'
export default function PlaceholderView({ icon, name }) {
  const { t } = useI18n()
  return (<div className="placeholder-view"><span className="placeholder-icon">{icon}</span>
    <span className="placeholder-text">{name}</span>
    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{t('ui.coming_soon')}</span></div>)
}
