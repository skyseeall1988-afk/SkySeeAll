import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';
import TacticalHUD from './components/TacticalHUD';
import SpectrumDrones from './components/SpectrumDrones';
import VisionAudio from './components/VisionAudio';
import IntelMaps from './components/IntelMaps';
import SystemControls from './components/SystemControls';
import Sidebar from './components/Sidebar';
import LiveFeedPanel from './components/LiveFeedPanel';

function App() {
  const [socket, setSocket] = useState(null);
  const [activeModule, setActiveModule] = useState('tactical');
  const [nightMode, setNightMode] = useState(false);
  const [sentries, setSentries] = useState([]);
  const [activeSentry, setActiveSentry] = useState(null);
  const [hardwareStatus, setHardwareStatus] = useState(null);
  const [liveFeeds, setLiveFeeds] = useState({
    tactical: [],
    spectrum: [],
    video: [],
    audio: []
  });

  // Fetch hardware capabilities on load
  useEffect(() => {
    fetch('/api/hardware/capabilities')
      .then(res => res.json())
      .then(data => {
        setHardwareStatus(data);
        console.log('Hardware capabilities:', data);
      })
      .catch(err => console.error('Failed to fetch hardware status:', err));
  }, []);

  useEffect(() => {
    // Initialize SocketIO connection
    const newSocket = io(window.location.origin, {
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('Connected to SkySeeAll C2 Server');
    });

    newSocket.on('tactical_update', (data) => {
      setLiveFeeds(prev => ({
        ...prev,
        tactical: [data, ...prev.tactical.slice(0, 49)]
      }));
    });

    newSocket.on('spectrum_fft', (data) => {
      setLiveFeeds(prev => ({
        ...prev,
        spectrum: [data, ...prev.spectrum.slice(0, 99)]
      }));
    });

    newSocket.on('video_frame', (data) => {
      setLiveFeeds(prev => ({
        ...prev,
        video: [data, ...prev.video.slice(0, 29)]
      }));
    });

    newSocket.on('audio_stream', (data) => {
      setLiveFeeds(prev => ({
        ...prev,
        audio: [data, ...prev.audio.slice(0, 49)]
      }));
    });

    newSocket.on('sentry_list', (data) => {
      setSentries(data);
      if (!activeSentry && data.length > 0) {
        setActiveSentry(data[0].pet_id);
      }
    });

    setSocket(newSocket);

    // Request sentry list on connect
    newSocket.emit('get_sentries');

    return () => newSocket.close();
  }, []);

  useEffect(() => {
    if (socket && activeSentry) {
      socket.emit('subscribe', { feed: activeModule, pet_id: activeSentry });
    }
  }, [socket, activeModule, activeSentry]);

  const renderActiveModule = () => {
    const props = { socket, activeSentry, liveFeeds, hardwareStatus };
    
    switch (activeModule) {
      case 'tactical':
        return <TacticalHUD {...props} />;
      case 'spectrum':
        return <SpectrumDrones {...props} />;
      case 'vision':
        return <VisionAudio {...props} />;
      case 'intel':
        return <IntelMaps {...props} />;
      case 'system':
        return <SystemControls {...props} />;
      default:
        return <TacticalHUD {...props} />;
    }
  };

  return (
    <div className={`app ${nightMode ? 'night-mode' : ''}`}>
      <Sidebar 
        activeModule={activeModule}
        setActiveModule={setActiveModule}
        nightMode={nightMode}
        setNightMode={setNightMode}
      />
      
      <div className="main-container">
        <header className="top-bar acrylic">
          <div className="logo-section">
            <h1>⚡ SkySeeAll</h1>
            <span className="version">v14.3</span>
          </div>
          
          <div className="sentry-selector">
            <label>Active Sentry:</label>
            <select 
              value={activeSentry || ''} 
              onChange={(e) => setActiveSentry(e.target.value)}
              className="fluent-select"
            >
              {sentries.map(sentry => (
                <option key={sentry.pet_id} value={sentry.pet_id}>
                  {sentry.pet_name} ({sentry.pet_id})
                </option>
              ))}
            </select>
          </div>

          <div className="status-indicators">
            <div className="status-item">
              <span className={`indicator pulse ${socket?.connected ? 'online' : 'offline'}`}></span>
              <span>{socket?.connected ? 'Connected' : 'Offline'}</span>
            </div>
            <div className="status-item">
              <span className="indicator pulse active"></span>
              <span>{sentries.length} Sentries</span>
            </div>
          </div>
        </header>

        <div className="content-area">
          <div className="module-container">
            {renderActiveModule()}
          </div>
          
          <LiveFeedPanel 
            activeModule={activeModule}
            liveFeeds={liveFeeds}
            socket={socket}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
