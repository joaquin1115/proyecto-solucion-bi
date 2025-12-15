import { useState } from 'react'
import FileUpload from './components/FileUpload'
import Dashboard from './components/Dashboard'
import ServiceOwnerDashboard from './components/ServiceOwnerDashboard'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [isProcessing, setIsProcessing] = useState(false);

  const isUploadActive = activeTab === 'upload';
  const isDashboardActive = activeTab === 'dashboard';
  const isServiceOwnerDashboardActive = activeTab === 'serviceOwner';

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 animate-fade-in-up">
      <div className="w-full max-w-6xl mx-auto">
        <h1 className="text-5xl md:text-6xl font-display font-bold text-center text-white mb-10 tracking-wider">
          DASHBOARD NIVELES DE MADUREZ
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <button 
            onClick={() => setActiveTab('upload')}
            className={`group relative flex items-center justify-center gap-3 w-full h-16 px-6 text-white font-bold text-lg rounded-lg transition-all duration-300 shadow-glow-primary ${isUploadActive ? 'bg-primary' : 'bg-primary/20 border border-primary/50 hover:bg-primary/30'}`}
          >
            <span className="material-symbols-outlined">upload</span>
            SUBIR DATOS
          </button>
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`group relative flex items-center justify-center gap-3 w-full h-16 px-6 text-white font-bold text-lg rounded-lg transition-all duration-300 shadow-glow-primary ${isDashboardActive ? 'bg-primary' : 'bg-primary/20 border border-primary/50 hover:bg-primary/30'} disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary/20`}
            disabled={isProcessing}
          >
            <span className="material-symbols-outlined">bar_chart</span>
            VER DASHBOARD GLOBAL
          </button>
          <button 
            onClick={() => setActiveTab('serviceOwner')}
            className={`group relative flex items-center justify-center gap-3 w-full h-16 px-6 text-white font-bold text-lg rounded-lg transition-all duration-300 shadow-glow-primary ${isServiceOwnerDashboardActive ? 'bg-primary' : 'bg-primary/20 border border-primary/50 hover:bg-primary/30'} disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary/20`}
            disabled={isProcessing}
          >
            <span className="material-symbols-outlined">monitoring</span>
            VER DASHBOARD POR SERVICIO
          </button>
        </div>
        <main>
          {isUploadActive && <FileUpload setIsProcessing={setIsProcessing} />}
          {isDashboardActive && <Dashboard />}
          {isServiceOwnerDashboardActive && <ServiceOwnerDashboard />}
        </main>
      </div>
    </div>
  );
}

export default App
