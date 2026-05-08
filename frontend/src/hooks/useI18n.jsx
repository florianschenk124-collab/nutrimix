import { useState, useEffect, createContext, useContext } from 'react'
import { fetchLocale } from '../api'

const I18nContext = createContext({ t: (k) => k, lang: 'de', setLang: () => {} })

export function I18nProvider({ children }) {
  const [lang, setLang] = useState('de')
  const [translations, setTranslations] = useState({})

  useEffect(() => {
    fetchLocale(lang)
      .then(setTranslations)
      .catch(() => setTranslations({}))
  }, [lang])

  const t = (key) => translations[key] || key

  return (
    <I18nContext.Provider value={{ t, lang, setLang }}>
      {children}
    </I18nContext.Provider>
  )
}

export const useI18n = () => useContext(I18nContext)
