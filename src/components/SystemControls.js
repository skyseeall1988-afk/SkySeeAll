import React, { useState, useEffect } from 'react';
import './SystemControls.css';

const SystemControls = ({ socket, activeSentry }) => {
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    battery: 100
  });
  const [services, setServices] = useState([]);
  const [sshConnected, setSshConnected] = useState(false);

  useEffect(() => {
    // Simulate system stats updates
    const interval = setInterval(() => {
      setSystemStats({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: 65 + Math.random() * 10,
        battery: 80 + Math.random() * 20
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const connectSSH = () => {
    const host = prompt('Enter SSH host (user@host):');
    if (!host || !socket || !activeSentry) return;
    
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'ssh_connect',
      parameters: { host }
    });
    setSshConnected(true);
  };

  const executeCommand = () => {
    const command = prompt('Enter command to execute:');
    if (!command || !socket || !activeSentry) return;
    
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'execute_command',
      parameters: { command }
    });
  };

  const restartService = (serviceName) => {
    if (!socket || !activeSentry) return;
    
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'restart_service',
      parameters: { service: serviceName }
    });
  };

  return (
    <div className="system-controls">
      <div className="fluent-card">
        <div className="card-header">
          <h2 className="card-title">⚙️ System & Controls - Remote Administration</h2>
          <div className="ssh-status">
            <span className={`indicator ${sshConnected ? 'active' : 'offline'}`}></span>
            <span>{sshConnected ? 'SSH Connected' : 'SSH Disconnected'}</span>
          </div>
        </div>

        <div className="grid-2">
          <div className="stat-card cpu">
            <div className="stat-icon">🖥️</div>
            <div className="stat-info">
              <div className="stat-label">CPU Usage</div>
              <div className="stat-value">{systemStats.cpu.toFixed(1)}%</div>
            </div>
            <div className="stat-bar">
              <div 
                className="stat-fill cpu-fill"
                style={{ width: `${systemStats.cpu}%` }}
              />
            </div>
          </div>

          <div className="stat-card memory">
            <div className="stat-icon">💾</div>
            <div className="stat-info">
              <div className="stat-label">Memory Usage</div>
              <div className="stat-value">{systemStats.memory.toFixed(1)}%</div>
            </div>
            <div className="stat-bar">
              <div 
                className="stat-fill memory-fill"
                style={{ width: `${systemStats.memory}%` }}
              />
            </div>
          </div>

          <div className="stat-card disk">
            <div className="stat-icon">💿</div>
            <div className="stat-info">
              <div className="stat-label">Disk Usage</div>
              <div className="stat-value">{systemStats.disk.toFixed(1)}%</div>
            </div>
            <div className="stat-bar">
              <div 
                className="stat-fill disk-fill"
                style={{ width: `${systemStats.disk}%` }}
              />
            </div>
          </div>

          <div className="stat-card battery">
            <div className="stat-icon">🔋</div>
            <div className="stat-info">
              <div className="stat-label">Battery Level</div>
              <div className="stat-value">{systemStats.battery.toFixed(1)}%</div>
            </div>
            <div className="stat-bar">
              <div 
                className="stat-fill battery-fill"
                style={{ width: `${systemStats.battery}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🔌 Remote Access</h3>
          </div>
          <button className="fluent-button" onClick={connectSSH}>
            🔐 SSH Connect
          </button>
          <button className="fluent-button">📁 SFTP Browser</button>
          <button className="fluent-button">📱 ADB Shell (Android)</button>
          <button className="fluent-button">🖥️ VNC Viewer</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">⚡ Command Execution</h3>
          </div>
          <button className="fluent-button" onClick={executeCommand}>
            💻 Execute Command
          </button>
          <button className="fluent-button">📝 Run Script</button>
          <button className="fluent-button">🔄 Update System</button>
          <button className="fluent-button danger">🔴 Reboot System</button>
        </div>
      </div>

      <div className="fluent-card">
        <div className="card-header">
          <h3 className="card-title">🛠️ Service Management</h3>
        </div>
        <div className="services-grid">
          {['nginx', 'postgresql', 'redis', 'docker', 'ssh', 'firewall'].map(service => (
            <div key={service} className="service-item">
              <div className="service-info">
                <span className="indicator pulse active"></span>
                <span className="service-name">{service}</span>
              </div>
              <div className="service-actions">
                <button 
                  className="fluent-button small success"
                  onClick={() => restartService(service)}
                >
                  🔄 Restart
                </button>
                <button className="fluent-button small danger">
                  ⏹️ Stop
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🔧 Hardware Checks</h3>
          </div>
          <button className="fluent-button">📡 Dongle Check</button>
          <button className="fluent-button">📶 Network Interfaces</button>
          <button className="fluent-button">🎤 Audio Devices</button>
          <button className="fluent-button">📹 Video Devices</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">📊 Logs & Monitoring</h3>
          </div>
          <button className="fluent-button">📋 System Logs</button>
          <button className="fluent-button">🔍 Search Logs</button>
          <button className="fluent-button">📈 Performance Monitor</button>
          <button className="fluent-button">⚠️ Error Reports</button>
        </div>
      </div>
    </div>
  );
};

export default SystemControls;
