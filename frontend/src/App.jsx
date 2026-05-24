import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Upload, CheckSquare, Activity } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Ingestion from './pages/Ingestion';
import Review from './pages/Review';

function Sidebar() {
  const location = useLocation();
  const menuItems = [
    { path: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { path: '/ingestion', icon: <Upload size={20} />, label: 'Data Ingestion' },
    { path: '/review', icon: <CheckSquare size={20} />, label: 'Analyst Review' },
  ];

  return (
    <div className="sidebar glass-panel">
      <div>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity color="var(--primary-color)" /> Breathe ESG
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Carbon Data Platform</p>
      </div>
      
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link 
              key={item.path} 
              to={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderRadius: '8px',
                textDecoration: 'none',
                color: isActive ? 'var(--primary-color)' : 'var(--text-secondary)',
                background: isActive ? 'rgba(0, 242, 254, 0.1)' : 'transparent',
                fontWeight: isActive ? 600 : 500,
                transition: 'all 0.3s ease'
              }}
            >
              {item.icon}
              {item.label}
            </Link>
          )
        })}
      </nav>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="layout">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ingestion" element={<Ingestion />} />
            <Route path="/review" element={<Review />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
