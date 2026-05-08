import { useState } from 'react'
import { I18nProvider } from './hooks/useI18n'
import Sidebar from './components/Sidebar'
import AlphaBanner from './components/AlphaBanner'
import Calculator from './views/Calculator'
import Recipes from './views/Recipes'
import RecipeEditor from './views/RecipeEditor'
import RecipeCompare from './views/RecipeCompare'
import WaterProfiles from './views/WaterProfiles'
import PhCorrection from './views/PhCorrection'
import Dilution from './views/Dilution'
import ReverseCalc from './views/ReverseCalc'
import SaltDatabase from './views/SaltDatabase'
import Plants from './views/Plants'
import GrowthPhases from './views/GrowthPhases'
import Compatibility from './views/Compatibility'
import CostManager from './views/CostManager'
import Labels from './views/Labels'
import ExportImport from './views/ExportImport'
import Settings from './views/Settings'

export default function App() {
  const [activeView, setActiveView] = useState('calculator')

  const renderView = () => {
    switch (activeView) {
      case 'calculator':      return <Calculator />
      case 'recipes':         return <Recipes />
      case 'new_recipe':      return <RecipeEditor />
      case 'recipe_compare':  return <RecipeCompare />
      case 'water_profiles':  return <WaterProfiles />
      case 'ph_correction':   return <PhCorrection />
      case 'dilution':        return <Dilution />
      case 'reverse':         return <ReverseCalc />
      case 'salt_database':   return <SaltDatabase />
      case 'plants':          return <Plants />
      case 'growth_phases':   return <GrowthPhases />
      case 'compatibility':   return <Compatibility />
      case 'costs':           return <CostManager />
      case 'labels':          return <Labels />
      case 'export_import':   return <ExportImport />
      case 'settings':        return <Settings />
      default:                return <Calculator />
    }
  }

  return (
    <I18nProvider>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <AlphaBanner />
        <div className="app-layout" style={{ flex: 1, minHeight: 0 }}>
          <Sidebar activeView={activeView} onNavigate={setActiveView} />
          <main className="content-area">
            {renderView()}
          </main>
        </div>
      </div>
    </I18nProvider>
  )
}
