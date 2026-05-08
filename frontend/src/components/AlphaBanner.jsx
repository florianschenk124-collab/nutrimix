import { useState } from 'react'
import { useI18n } from '../hooks/useI18n'

export default function AlphaBanner() {
  const { t } = useI18n()
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  return (
    <div style={{
      background: 'linear-gradient(90deg, rgba(224,164,88,0.15), rgba(212,95,95,0.1))',
      borderBottom: '1px solid rgba(224,164,88,0.3)',
      padding: '8px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 12,
      fontSize: 12,
      color: 'var(--warning)',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 16 }}>⚠️</span>
        <span>
          <strong>Alpha v0.5.0</strong>
          {' – '}
          {t('alpha.disclaimer')}
        </span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        style={{
          background: 'none',
          border: 'none',
          color: 'var(--text-muted)',
          cursor: 'pointer',
          fontSize: 14,
          padding: '2px 6px',
          flexShrink: 0,
        }}
      >
        ✕
      </button>
    </div>
  )
}
