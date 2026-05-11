import { useState, useEffect, createContext, useContext, useCallback } from 'react'
import { fetchLocale } from '../api'

const I18nContext = createContext({ t: (k) => k, td: (s) => s, lang: 'de', setLang: () => {} })

export function I18nProvider({ children }) {
  const [lang, setLang] = useState('de')
  const [translations, setTranslations] = useState({})

  useEffect(() => {
    fetchLocale(lang)
      .then(setTranslations)
      .catch(() => setTranslations({}))
  }, [lang])

  const t = useCallback((key) => translations[key] || key, [translations])

  // td() – Daten-Level Übersetzung
  // Handles: exact match, salt names, salt notes, data translations
  // Also handles " | " separated multi-descriptions
  const td = useCallback((text) => {
    if (!text || lang === 'de') return text
    // Try exact matches first
    const direct = translations[`data.${text}`]
      || translations[`salt.name.${text}`]
      || translations[`salt.note.${text}`]
    if (direct) return direct
    // Handle " | " separated strings (e.g. compatibility descriptions)
    if (text.includes(' | ')) {
      return text.split(' | ').map(part => {
        const p = translations[`data.${part.trim()}`]
          || translations[`salt.name.${part.trim()}`]
          || part.trim()
        return p
      }).join(' | ')
    }
    return text
  }, [translations, lang])

  return (
    <I18nContext.Provider value={{ t, td, lang, setLang }}>
      {children}
    </I18nContext.Provider>
  )
}

export const useI18n = () => useContext(I18nContext)
