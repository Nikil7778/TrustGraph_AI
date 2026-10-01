import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { AuthProvider } from './context/AuthContext';
import { PipelineProvider } from './context/PipelineContext';
import { Home } from './pages/Home';
import { NewAnalysis } from './pages/NewAnalysis';
import { HistoryPage } from './pages/HistoryPage';
import { ThreatIntelligencePage } from './pages/ThreatIntelligencePage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PipelineProvider>
          <div className="flex min-h-screen bg-slate-50">
            <Sidebar />
            <div className="flex-1 overflow-x-hidden">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/new-analysis" element={<NewAnalysis />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/threat-intel" element={<ThreatIntelligencePage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </div>
          </div>
        </PipelineProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
