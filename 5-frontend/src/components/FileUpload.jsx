// frontend/src/components/FileUpload.jsx
import React from 'react';
import InfoTooltip from './InfoTooltip';
import { API_BASE_URL } from '../config';

const DESTINATIONS = {
  practitioner: 'Practitioner',
  continuous_integration: 'Continuous Integration',
};

function FileUpload({ setIsProcessing }) {
  const [file, setFile] = React.useState(null);
  const [destination, setDestination] = React.useState('practitioner');
  const [message, setMessage] = React.useState('');
  const [messageType, setMessageType] = React.useState('info');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const clearFeedback = () => {
    setMessage('');
    setError('');
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      setError('Por favor, selecciona un archivo.');
      return;
    }

    setLoading(true);
    setIsProcessing(true);
    clearFeedback();

    const formData = new FormData();
    formData.append('file', file);
    formData.append('destination', destination);

    try {
      // ⭐ AHORA SE USA EL BACKEND REAL EN AZURE
      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.status === 202 && data.task_id) {
        pollTaskStatus(data.task_id);
      } else {
        setError(data.error || 'Ocurrió un error al subir el archivo.');
        setLoading(false);
        setIsProcessing(false);
      }
    } catch {
      setError('Error de conexión con el servidor.');
      setLoading(false);
      setIsProcessing(false);
    }
  };

  const pollTaskStatus = (taskId) => {
    const interval = setInterval(async () => {
      try {
        // ⭐ Polling al backend real
        const response = await fetch(`${API_BASE_URL}/api/upload/status/${taskId}`);
        const data = await response.json();

        if (response.ok) {
          if (data.status === 'procesando') {
            setMessage(data.message);
            setMessageType('info');
          }

          if (data.status === 'completado') {
            setMessage(data.message);
            setMessageType('success');
            clearInterval(interval);
            setLoading(false);
            setIsProcessing(false);
            setFile(null);
          }

          if (data.status === 'error') {
            setError(data.message || 'Ocurrió un error durante el procesamiento.');
            clearInterval(interval);
            setLoading(false);
            setIsProcessing(false);
          }
        }
      } catch {
        setError('Error de conexión al verificar el estado.');
        clearInterval(interval);
        setLoading(false);
        setIsProcessing(false);
      }
    }, 1000);
  };

  const getMessageIcon = () => {
    if (messageType === 'success') return 'check_circle';
    if (messageType === 'info' && loading) return 'hourglass_top';
    return 'info';
  };

  return (
    <div className="bg-background-dark/50 border border-primary/20 rounded-xl p-8 shadow-lg backdrop-blur-sm">
      <form onSubmit={handleSubmit}>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-end">

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary uppercase">Destino del Dato</label>
            <select
              className="form-select w-full h-14 pl-4 pr-10 bg-black/40 border border-primary/30 text-white rounded-lg font-mono"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              disabled={loading}
            >
              <option value="practitioner">{DESTINATIONS.practitioner}</option>
              <option value="continuous_integration">{DESTINATIONS.continuous_integration}</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary uppercase">Seleccionar Archivo CSV</label>
            <div className="relative h-14 flex items-center">
              <input
                accept=".csv"
                className="absolute inset-0 opacity-0 cursor-pointer"
                type="file"
                onChange={handleFileChange}
                disabled={loading}
              />
              <div className="flex items-center justify-between w-full h-full px-4 bg-black/40 border border-primary/30 text-white rounded-lg pointer-events-none font-mono">
                <InfoTooltip text="El archivo debe ser .csv y codificado en UTF-8.">
                  <span className={`truncate ${file ? 'text-white' : 'text-gray-400'}`}>
                    {file ? file.name : 'NINGÚN ARCHIVO SELECCIONADO'}
                  </span>
                </InfoTooltip>
              </div>
            </div>
          </div>

        </div>

        <div className="mt-10 text-center">
          <button 
            type="submit" 
            className="w-full md:w-auto h-12 px-10 bg-primary text-white font-bold rounded-lg shadow-glow-primary"
            disabled={loading || !file}
          >
            {loading ? 'PROCESANDO...' : 'SUBIR ARCHIVO'}
          </button>
        </div>

        <div className="mt-6 text-center h-6">
          {message && (
            <p className={`font-mono flex items-center justify-center gap-2 ${messageType === 'success' ? 'text-green-400' : 'text-cyan-400'}`}>
              <span className="material-symbols-outlined text-xl">{getMessageIcon()}</span>
              {message}
            </p>
          )}

          {error && (
            <p className="text-red-400 font-mono flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-xl">error</span>
              {error}
            </p>
          )}
        </div>

      </form>
    </div>
  );
}

export default FileUpload;