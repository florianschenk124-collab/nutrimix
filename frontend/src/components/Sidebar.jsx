import { useI18n } from '../hooks/useI18n'

const NAV_GROUPS = [
  {
    items: [
      { key: 'recipes',        icon: '📋', locale: 'nav.recipes' },
      { key: 'new_recipe',     icon: '➕', locale: 'nav.new_recipe' },
      { key: 'recipe_compare', icon: '⚖️', locale: 'nav.recipe_compare' },
    ],
  },
  {
    label: 'nav.group.calculation',
    items: [
      { key: 'calculator',   icon: '🧮', locale: 'nav.calculator' },
      { key: 'ph_correction', icon: '🧪', locale: 'nav.ph_correction' },
      { key: 'dilution',     icon: '🔬', locale: 'nav.dilution' },
      { key: 'reverse',      icon: '🔄', locale: 'nav.reverse' },
    ],
  },
  {
    label: 'nav.group.data',
    items: [
      { key: 'water_profiles', icon: '💧', locale: 'nav.water_profiles' },
      { key: 'plants',         icon: '🌱', locale: 'nav.plants' },
      { key: 'growth_phases',  icon: '📅', locale: 'nav.growth_phases' },
      { key: 'salt_database',  icon: '🧂', locale: 'nav.salt_database' },
      { key: 'compatibility',  icon: '🔬', locale: 'nav.compatibility' },
    ],
  },
  {
    label: 'nav.group.tools',
    items: [
      { key: 'costs',        icon: '💰', locale: 'nav.costs' },
      { key: 'labels',       icon: '🏷️', locale: 'nav.labels' },
      { key: 'export_import', icon: '📦', locale: 'nav.export_import' },
      { key: 'settings',     icon: '⚙️', locale: 'nav.settings' },
    ],
  },
]

export default function Sidebar({ activeView, onNavigate }) {
  const { t } = useI18n()

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">🌿 NutrientMixer</div>
        <div className="sidebar-subtitle">{t('app.title')}</div>
      </div>

      <nav className="sidebar-nav">
        {NAV_GROUPS.map((group, gi) => (
          <div key={gi}>
            {group.label && (
              <div className="nav-group-label">{t(group.label)}</div>
            )}
            {group.items.map(({ key, icon, locale }) => (
              <button
                key={key}
                className={`nav-item ${activeView === key ? 'active' : ''}`}
                onClick={() => onNavigate(key)}
              >
                <span className="nav-icon">{icon}</span>
                <span>{t(locale)}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">v0.5.0</div>
    </aside>
  )
}
