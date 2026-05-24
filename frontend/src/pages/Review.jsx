import React, { useState, useEffect } from 'react';
import api from '../api';
import { Check, X, Edit2 } from 'lucide-react';

export default function Review() {
  const [records, setRecords] = useState([]);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [editingId, setEditingId] = useState(null);
  const [editVal, setEditVal] = useState('');

  useEffect(() => {
    fetchRecords();
  }, [statusFilter]);

  const fetchRecords = async () => {
    try {
      const res = await api.get(`/records/?status=${statusFilter}`);
      setRecords(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprove = async (id) => {
    try {
      await api.patch(`/records/${id}/`, { status: 'APPROVED' });
      fetchRecords();
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (id) => {
    try {
      await api.patch(`/records/${id}/`, { status: 'REJECTED' });
      fetchRecords();
    } catch (err) {
      console.error(err);
    }
  };

  const saveEdit = async (id) => {
    try {
      await api.patch(`/records/${id}/`, { normalized_quantity: editVal });
      setEditingId(null);
      fetchRecords();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1 style={{ margin: 0 }}>Analyst Review</h1>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['PENDING', 'APPROVED', 'REJECTED'].map(status => (
            <button 
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`btn ${statusFilter === status ? 'btn-primary' : 'btn-secondary'}`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-panel table-container">
        <table>
          <thead>
            <tr>
              <th>Reference ID</th>
              <th>Category (Scope)</th>
              <th>Activity Type</th>
              <th>Quantity</th>
              <th>Calculated (kg CO2e)</th>
              <th>Status</th>
              {statusFilter === 'PENDING' && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {records.length === 0 && (
              <tr><td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No records found.</td></tr>
            )}
            {records.map(record => (
              <tr key={record.id}>
                <td>{record.original_reference_id}</td>
                <td>
                  <div style={{ fontWeight: 500 }}>{record.category}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{record.scope.replace('_', ' ')}</div>
                </td>
                <td>{record.activity_type}</td>
                <td>
                  {editingId === record.id ? (
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <input 
                        type="number" 
                        value={editVal} 
                        onChange={(e) => setEditVal(e.target.value)} 
                        style={{ width: '100px', padding: '6px' }}
                      />
                      <button className="btn btn-primary" style={{ padding: '6px' }} onClick={() => saveEdit(record.id)}>Save</button>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {Number(record.normalized_quantity).toLocaleString()} {record.normalized_unit}
                      {statusFilter === 'PENDING' && (
                        <Edit2 size={14} style={{ cursor: 'pointer', color: 'var(--text-secondary)' }} onClick={() => { setEditingId(record.id); setEditVal(record.normalized_quantity); }} />
                      )}
                    </div>
                  )}
                </td>
                <td style={{ fontWeight: 600, color: 'var(--primary-color)' }}>
                  {Number(record.calculated_emissions).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </td>
                <td>
                  <span className={`badge badge-${record.status.toLowerCase()}`}>{record.status}</span>
                </td>
                {statusFilter === 'PENDING' && (
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => handleApprove(record.id)} style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-color)', border: 'none', borderRadius: '4px', padding: '6px', cursor: 'pointer' }}>
                        <Check size={18} />
                      </button>
                      <button onClick={() => handleReject(record.id)} style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger-color)', border: 'none', borderRadius: '4px', padding: '6px', cursor: 'pointer' }}>
                        <X size={18} />
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
