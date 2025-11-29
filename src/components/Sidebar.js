import React from 'react';
import './Sidebar.css';

const Sidebar = ({ activeModule, setActiveModule, nightMode, setNightMode }) => {
  const modules = [
    { id: 'tactical', icon: '🎯', name: 'Tactical HUD', desc: 'Network Scanning' },
    { id: 'spectrum', icon: '📡', name: 'Spectrum', desc: 'Radio & Drones' },
    { id: 'vision', icon: '📹', name: 'Vision', desc: 'Media & Audio' },
    { id: 'intel', icon: '🗺️', name: 'Intel', desc: 'OSINT & Maps' },
    { id: 'system', icon: '⚙️', name: 'System', desc: 'Controls' }
  ];

  return (
    <div className="sidebar acrylic">
      <div className="sidebar-modules">
        {modules.map(module => (
          <div
            key={module.id}
            className={`sidebar-item ${activeModule === module.id ? 'active' : ''}`}
            onClick={() => setActiveModule(module.id)}
          >
            <div className="module-icon">{module.icon}</div>
            <div className="module-info">
              <div className="module-name">{module.name}</div>
              <div className="module-desc">{module.desc}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div 
          className="sidebar-item"
          onClick={() => setNightMode(!nightMode)}
        >
          <div className="module-icon">{nightMode ? '☀️' : '🌙'}</div>
          <div className="module-info">
            <div className="module-name">Night Mode</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
