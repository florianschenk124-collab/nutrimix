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

  // t() – UI-Key Übersetzung (z.B. t('calc.title'))
  const t = useCallback((key) => translations[key] || key, [translations])

  // td() – Daten-Level Übersetzung (Salznamen, Rezeptnamen, Pflanzennamen, etc.)
  // Sucht in: data.{text}, salt.name.{text}, salt.note.{text}
  // Falls nichts gefunden → Originaltext zurück
  const td = useCallback((text) => {
    if (!text || lang === 'de') return text
    return translations[`data.${text}`]
      || translations[`salt.name.${text}`]
      || translations[`salt.note.${text}`]
      || text
  }, [translations, lang])

  return (
    <I18nContext.Provider value={{ t, td, lang, setLang }}>
      {children}
    </I18nContext.Provider>
  )
}

export const useI18n = () => useContext(I18nContext)
