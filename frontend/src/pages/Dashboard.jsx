import React, { useState, useEffect } from 'react';
import api from '../api';
import { Cloud, FileWarning, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area } from 'recharts';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_emissions_approved: 0,
    pending_reviews_count: 0,
    failed_uploads_count: 0,
    emissions_by_scope: [],
    emissions_by_category: [],
    emissions_over_time: []
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get('/stats/');
      setStats(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const COLORS = ['#00f2fe', '#4facfe', '#10b981', '#f59e0b', '#8b5cf6'];

  return (
    <div className="animate-fade-in">
      <h1 style={{ marginBottom: '32px' }}>Dashboard Overview</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '12px' }}>
            <Cloud size={32} color="var(--success-color)" />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)', margin: '0 0 8px 0', fontSize: '0.9rem' }}>Approved Emissions</p>
            <h2 style={{ margin: 0 }}>{Number(stats.total_emissions_approved).toLocaleString(undefined, {maximumFractionDigits: 0})} <span style={{fontSize: '1rem', color: 'var(--text-secondary)'}}>kg CO2e</span></h2>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '16px', borderRadius: '12px' }}>
            <Clock size={32} color="var(--warning-color)" />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)', margin: '0 0 8px 0', fontSize: '0.9rem' }}>Pending Reviews</p>
            <h2 style={{ margin: 0 }}>{stats.pending_reviews_count}</h2>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '16px', borderRadius: '12px' }}>
            <FileWarning size={32} color="var(--danger-color)" />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)', margin: '0 0 8px 0', fontSize: '0.9rem' }}>Failed Uploads</p>
            <h2 style={{ margin: 0 }}>{stats.failed_uploads_count}</h2>
          </div>
        </div>

      </div>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '32px' }}>
        <h3 style={{ marginTop: 0, marginBottom: '24px', color: 'var(--text-secondary)' }}>Emissions Over Time (kg CO2e)</h3>
        <div style={{ height: '300px' }}>
          {stats.emissions_over_time && stats.emissions_over_time.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.emissions_over_time} margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary-color)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--primary-color)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-border)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                <YAxis stroke="var(--text-secondary)" tickFormatter={(val) => `${val/1000}k`} tick={{fontSize: 12}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-color)', border: '1px solid var(--surface-border)', borderRadius: '8px' }}
                  itemStyle={{ color: 'var(--primary-color)' }}
                  formatter={(value) => `${Number(value).toLocaleString()} kg CO2e`}
                />
                <Area type="monotone" dataKey="value" stroke="var(--primary-color)" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>No approved data yet.</div>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '24px', color: 'var(--text-secondary)' }}>Emissions by Scope</h3>
          <div style={{ height: '300px' }}>
            {stats.emissions_by_scope && stats.emissions_by_scope.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.emissions_by_scope}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                    stroke="none"
                  >
                    {stats.emissions_by_scope.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-color)', border: '1px solid var(--surface-border)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--text-primary)' }}
                    formatter={(value) => `${Number(value).toLocaleString()} kg`}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>No approved data yet.</div>
            )}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '24px', color: 'var(--text-secondary)' }}>Emissions by Category</h3>
          <div style={{ height: '300px' }}>
            {stats.emissions_by_category && stats.emissions_by_category.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.emissions_by_category} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-border)" horizontal={false} />
                  <XAxis type="number" stroke="var(--text-secondary)" tickFormatter={(val) => `${val/1000}k`} />
                  <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" width={120} tick={{fill: 'var(--text-primary)', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-color)', border: '1px solid var(--surface-border)', borderRadius: '8px' }}
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    formatter={(value) => `${Number(value).toLocaleString()} kg CO2e`}
                  />
                  <Bar dataKey="value" fill="var(--primary-color)" radius={[0, 4, 4, 0]}>
                    {stats.emissions_by_category.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>No approved data yet.</div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
