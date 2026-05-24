import React, { useState, useEffect } from 'react';
import api from '../api';
import { UploadCloud, Server } from 'lucide-react';

export default function Ingestion() {
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const res = await api.get('/data-sources/');
      setSources(res.data);
      if (res.data.length > 0) setSelectedSource(res.data[0].id);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedSource) return;
    
    setLoading(true);
    setMessage(null);
    
    const source = sources.find(s => s.id === selectedSource);
    
    try {
      if (source.source_type === 'TRAVEL') {
        // Mock JSON API sync
        const payload = await fetch('http://localhost:5173/samples/concur_trip.json').then(res => res.json()).catch(() => ({
          "data": [{"id": "DEMO-123", "airDetails": {"distance": 1500, "departureDate": "2026-06-01T00:00:00Z"}}]
        }));
        
        await api.post('/sync-travel/', { data_source_id: source.id, payload });
        setMessage({ type: 'success', text: 'Concur API Data synced successfully!' });
      } else {
        // File Upload
        if (!file) {
           setMessage({ type: 'error', text: 'Please select a file to upload.' });
           setLoading(false);
           return;
        }
        const formData = new FormData();
        formData.append('file', file);
        formData.append('data_source_id', source.id);
        
        await api.post('/upload/', formData, { headers: { 'Content-Type': 'multipart/form-data' }});
        setMessage({ type: 'success', text: 'File uploaded and parsed successfully!' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'An error occurred during ingestion.' });
    }
    setLoading(false);
  };

  const activeSource = sources.find(s => s.id === selectedSource);

  return (
    <div className="animate-fade-in">
      <h1 style={{ marginBottom: '32px' }}>Data Ingestion</h1>
      
      <div className="glass-panel" style={{ padding: '32px', maxWidth: '600px' }}>
        <form onSubmit={handleUpload}>
          <div className="input-group">
            <label>Target Data Source</label>
            <select value={selectedSource} onChange={(e) => setSelectedSource(e.target.value)}>
              {sources.map(s => (
                <option key={s.id} value={s.id}>{s.source_type} - {s.client}</option>
              ))}
            </select>
          </div>

          {activeSource && activeSource.source_type !== 'TRAVEL' && (
            <div className="input-group" style={{ marginTop: '24px' }}>
              <label>Upload File (CSV / Export)</label>
              <div style={{
                border: '2px dashed var(--surface-border)',
                padding: '40px',
                textAlign: 'center',
                borderRadius: '12px',
                background: 'rgba(0,0,0,0.2)',
                cursor: 'pointer'
              }}>
                <UploadCloud size={48} color="var(--primary-color)" style={{ marginBottom: '16px' }}/>
                <br/>
                <input type="file" onChange={(e) => setFile(e.target.files[0])} style={{ background: 'transparent', border: 'none' }}/>
              </div>
            </div>
          )}

          {activeSource && activeSource.source_type === 'TRAVEL' && (
            <div style={{
              background: 'rgba(0, 242, 254, 0.05)',
              border: '1px solid var(--primary-color)',
              padding: '20px',
              borderRadius: '12px',
              marginTop: '24px',
              display: 'flex',
              alignItems: 'center',
              gap: '16px'
            }}>
              <Server size={32} color="var(--primary-color)" />
              <div>
                <h4 style={{ margin: '0 0 4px 0' }}>API Integration</h4>
                <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Clicking sync will trigger a pull from the Concur Travel API.</p>
              </div>
            </div>
          )}

          {message && (
            <div style={{ 
              marginTop: '24px', 
              padding: '16px', 
              borderRadius: '8px',
              background: message.type === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
              color: message.type === 'error' ? 'var(--danger-color)' : 'var(--success-color)',
              border: `1px solid ${message.type === 'error' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
            }}>
              {message.text}
            </div>
          )}

          <div style={{ marginTop: '32px' }}>
            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
              {loading ? 'Processing...' : (activeSource?.source_type === 'TRAVEL' ? 'Sync from API' : 'Upload & Process')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
