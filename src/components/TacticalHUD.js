import React, { useState, useEffect } from 'react';
import './TacticalHUD.css';

const TacticalHUD = ({ socket, activeSentry, liveFeeds, hardwareStatus }) => {
  const [wifiNetworks, setWifiNetworks] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [selectedNetwork, setSelectedNetwork] = useState(null);
  const [internetKilled, setInternetKilled] = useState(false);

  const isFeatureAvailable = (feature) => {
    return hardwareStatus?.features?.[feature] !== false;
  };

  const getEmulationBadge = (feature) => {
    if (!hardwareStatus) return null;
    const available = hardwareStatus.features?.[feature];
    const realHW = hardwareStatus.capabilities?.wifi_managed || hardwareStatus.capabilities?.wifi_monitor;
    
    if (!available) {
      return <span className="hw-badge unavailable">🔴 Hardware Required</span>;
    } else if (!realHW && available) {
      return <span className="hw-badge emulated">🟡 Emulated</span>;
    } else {
      return <span className="hw-badge available">🟢 Hardware</span>;
    }
  };

  const startWifiScan = () => {
    if (!socket || !activeSentry) return;
    setScanning(true);
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'wifi_scan',
      parameters: {}
    });
  };

  const startNmapScan = (target) => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'nmap_scan',
      parameters: { target }
    });
  };

  const killInternet = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'kill_internet',
      parameters: {}
    });
    setInternetKilled(true);
  };

  const restoreInternet = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'restore_internet',
      parameters: {}
    });
    setInternetKilled(false);
  };

  const captureHandshake = (bssid) => {
    if (!socket || !activeSentry) return;
    killInternet();
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'capture_handshake',
      parameters: { bssid }
    });
  };

  useEffect(() => {
    if (liveFeeds.tactical.length > 0) {
      setWifiNetworks(liveFeeds.tactical);
      setScanning(false);
    }
  }, [liveFeeds.tactical]);

  return (
    <div className="tactical-hud">
      <div className="fluent-card">
        <div className="card-header">
          <h2 className="card-title">🎯 Tactical HUD - Network Reconnaissance</h2>
          <div className="header-actions">
            {getEmulationBadge('wifi_scanning')}
            {internetKilled ? (
              <button className="fluent-button warning" onClick={restoreInternet}>
                🌐 Restore Internet
              </button>
            ) : (
              <button className="fluent-button danger" onClick={killInternet}>
                🚫 Kill Internet
              </button>
            )}
          </div>
        </div>

        <div className="grid-3">
          <button 
            className="fluent-button" 
            onClick={startWifiScan}
            disabled={scanning || !isFeatureAvailable('wifi_scanning')}
          >
            {scanning ? '⏳ Scanning...' : '📡 Wi-Fi Radar Scan'}
          </button>
          <button 
            className="fluent-button"
            onClick={() => {
              const target = prompt('Enter target IP or range (e.g., 192.168.1.0/24):');
              if (target) startNmapScan(target);
            }}
            disabled={!isFeatureAvailable('wifi_scanning')}
          >
            🔍 Nmap Scan
          </button>
          <button 
            className="fluent-button"
            disabled={!hardwareStatus?.capabilities?.bluetooth}
          >
            📶 Bluetooth Scan
          </button>
        </div>
      </div>

      <div className="fluent-card">
        <div className="card-header">
          <h3 className="card-title">Wi-Fi Networks Detected</h3>
          <span className="badge">{wifiNetworks.length} Networks</span>
        </div>

        <div className="network-grid">
          {wifiNetworks.map((network, index) => (
            <div 
              key={index} 
              className={`network-card reveal-hover ${selectedNetwork === index ? 'selected' : ''}`}
              onClick={() => setSelectedNetwork(index)}
            >
              <div className="network-header">
                <div className="network-ssid">{network.ssid || 'Hidden Network'}</div>
                <div className={`signal-strength signal-${network.signal > -50 ? 'strong' : network.signal > -70 ? 'medium' : 'weak'}`}>
                  {network.signal} dBm
                </div>
              </div>
              
              <div className="network-details">
                <div className="detail-row">
                  <span className="detail-label">BSSID:</span>
                  <span className="detail-value mono">{network.bssid}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Channel:</span>
                  <span className="detail-value">{network.channel}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Security:</span>
                  <span className="detail-value">{network.security || 'Open'}</span>
                </div>
              </div>

              {selectedNetwork === index && (
                <div className="network-actions">
                  <button 
                    className="fluent-button small"
                    onClick={(e) => {
                      e.stopPropagation();
                      captureHandshake(network.bssid);
                    }}
                  >
                    🎣 Capture Handshake
                  </button>
                  <button 
                    className="fluent-button small danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      alert('Deauth attack initiated (safety: internet will be killed)');
                    }}
                  >
                    ⚠️ Deauth
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>

        {wifiNetworks.length === 0 && (
          <div className="empty-state">
            <p>No networks detected. Click "Wi-Fi Radar Scan" to start scanning.</p>
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">IoT Discovery</h3>
          </div>
          <button className="fluent-button">🔌 Scan IoT Devices</button>
          <button className="fluent-button">🖨️ Discover Printers</button>
          <button className="fluent-button">📹 Find IP Cameras</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">Network Tools</h3>
          </div>
          <button className="fluent-button">🌐 DNS Lookup</button>
          <button className="fluent-button">📂 SMB Browser</button>
          <button className="fluent-button">📁 FTP Scanner</button>
        </div>
      </div>
    </div>
  );
};

export default TacticalHUD;
