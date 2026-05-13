import { useState, useEffect, createContext, useContext, useCallback } from 'react'
import { fetchLocale, setApiLang } from '../api'

const I18nContext = createContext({
  t: (k) => k, td: (s) => s, sd: (name, formula) => formula,
  lang: 'en', setLang: () => {},
  displayMode: 'formula', setDisplayMode: () => {},
})

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState('en')
  const [translations, setTranslations] = useState({})
  const [displayMode, setDisplayMode] = useState('formula') // "formula" | "name"

  const setLang = useCallback((newLang) => {
    setLangState(newLang)
    setApiLang(newLang)
  }, [])

  useEffect(() => {
    setApiLang(lang)
    fetchLocale(lang)
      .then(setTranslations)
      .catch(() => setTranslations({}))
  }, [lang])

  // t() – UI-Key
  const t = useCallback((key) => translations[key] || key, [translations])

  // td() – Daten-Level (Rezeptnamen, Pflanzennamen, Beschreibungen)
  const td = useCallback((text) => {
    if (!text || lang === 'de') return text
    const direct = translations[`data.${text}`]
      || translations[`salt.name.${text}`]
      || translations[`salt.note.${text}`]
    if (direct) return direct
    if (text.includes(' | ')) {
      return text.split(' | ').map(part => {
        return translations[`data.${part.trim()}`]
          || translations[`salt.name.${part.trim()}`]
          || part.trim()
      }).join(' | ')
    }
    return text
  }, [translations, lang])

  // sd() – Salz-Anzeige: Formel oder Name je nach displayMode
  // Aufruf: sd(salt.name, salt.formula) oder sd(name, formula)
  const sd = useCallback((name, formula) => {
    if (displayMode === 'formula') return formula || name
    // Name-Modus: übersetzen
    if (lang === 'de') return name
    return translations[`salt.name.${name}`] || name
  }, [displayMode, translations, lang])

  return (
    <I18nContext.Provider value={{ t, td, sd, lang, setLang, displayMode, setDisplayMode }}>
      {children}
    </I18nContext.Provider>
  )
}

export const useI18n = () => useContext(I18nContext)
