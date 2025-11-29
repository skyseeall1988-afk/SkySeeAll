import React, { useState, useEffect, useRef } from 'react';
import './SpectrumDrones.css';

const SpectrumDrones = ({ socket, activeSentry, liveFeeds }) => {
  const [sdrActive, setSdrActive] = useState(false);
  const [frequency, setFrequency] = useState(100.0);
  const [aircraft, setAircraft] = useState([]);
  const canvasRef = useRef(null);

  const startSDR = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'start_sdr',
      parameters: { frequency }
    });
    setSdrActive(true);
  };

  const stopSDR = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'stop_sdr',
      parameters: {}
    });
    setSdrActive(false);
  };

  const tuneFrequency = (freq) => {
    if (!socket || !activeSentry) return;
    setFrequency(freq);
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'tune_frequency',
      parameters: { frequency: freq }
    });
  };

  useEffect(() => {
    // Draw waterfall from spectrum data
    if (liveFeeds.spectrum.length > 0 && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const latestData = liveFeeds.spectrum[0];
      
      if (latestData.fft) {
        const width = canvas.width;
        const height = canvas.height;
        
        // Shift existing data down
        const imageData = ctx.getImageData(0, 0, width, height - 1);
        ctx.putImageData(imageData, 0, 1);
        
        // Draw new line
        latestData.fft.forEach((value, i) => {
          const x = (i / latestData.fft.length) * width;
          const hue = 240 - (value * 120); // Blue to red
          ctx.fillStyle = `hsl(${hue}, 80%, 50%)`;
          ctx.fillRect(x, 0, width / latestData.fft.length, 1);
        });
      }
    }
  }, [liveFeeds.spectrum]);

  return (
    <div className="spectrum-drones">
      <div className="fluent-card">
        <div className="card-header">
          <h2 className="card-title">📡 Spectrum & Drones - Radio Frequency Analysis</h2>
          <div className="sdr-status">
            <span className={`indicator pulse ${sdrActive ? 'active' : 'offline'}`}></span>
            <span>{sdrActive ? 'SDR Active' : 'SDR Idle'}</span>
          </div>
        </div>

        <div className="frequency-controls">
          <div className="freq-input-group">
            <label>Frequency (MHz):</label>
            <input 
              type="number" 
              className="fluent-input"
              value={frequency}
              onChange={(e) => setFrequency(parseFloat(e.target.value))}
              step="0.1"
              min="24"
              max="1766"
            />
          </div>

          <div className="freq-buttons">
            {!sdrActive ? (
              <button className="fluent-button success" onClick={startSDR}>
                ▶️ Start SDR
              </button>
            ) : (
              <button className="fluent-button danger" onClick={stopSDR}>
                ⏹️ Stop SDR
              </button>
            )}
            <button 
              className="fluent-button"
              onClick={() => tuneFrequency(frequency)}
              disabled={!sdrActive}
            >
              🎚️ Tune
            </button>
          </div>
        </div>

        <div className="waterfall-container">
          <h3>Spectrum Waterfall</h3>
          <canvas 
            ref={canvasRef}
            width={800}
            height={400}
            className="waterfall-canvas"
          />
        </div>

        <div className="preset-frequencies">
          <h4>Quick Tune Presets</h4>
          <div className="grid-3">
            <button className="fluent-button" onClick={() => tuneFrequency(88.5)}>
              📻 FM Radio (88.5)
            </button>
            <button className="fluent-button" onClick={() => tuneFrequency(121.5)}>
              ✈️ Aviation (121.5)
            </button>
            <button className="fluent-button" onClick={() => tuneFrequency(155.0)}>
              🚓 Police (155.0)
            </button>
            <button className="fluent-button" onClick={() => tuneFrequency(433.92)}>
              🏠 IoT (433.92)
            </button>
            <button className="fluent-button" onClick={() => tuneFrequency(915.0)}>
              📡 ISM Band (915.0)
            </button>
            <button className="fluent-button" onClick={() => tuneFrequency(1090.0)}>
              🛩️ ADS-B (1090.0)
            </button>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">✈️ Aircraft Tracking (ADS-B)</h3>
          </div>
          <button 
            className="fluent-button"
            onClick={() => {
              if (socket && activeSentry) {
                socket.emit('command', {
                  pet_id: activeSentry,
                  command_type: 'track_aircraft',
                  parameters: {}
                });
              }
            }}
          >
            🛫 Start ADS-B Tracking
          </button>
          <div className="aircraft-list">
            {aircraft.length > 0 ? (
              aircraft.map((plane, idx) => (
                <div key={idx} className="aircraft-item">
                  <span>✈️ {plane.callsign}</span>
                  <span>{plane.altitude} ft</span>
                </div>
              ))
            ) : (
              <p className="empty-text">No aircraft detected</p>
            )}
          </div>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🚁 Drone Detection</h3>
          </div>
          <button className="fluent-button">📡 Scan for Drones (Wi-Fi)</button>
          <button className="fluent-button">📶 Scan for Drones (Bluetooth)</button>
          <button className="fluent-button">📻 RF Drone Signatures</button>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🌊 Marine Tracking (AIS)</h3>
          </div>
          <button className="fluent-button">🚢 Track Ships</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">📡 Sensor Monitoring</h3>
          </div>
          <button className="fluent-button">🚗 Tire Pressure Sensors</button>
          <button className="fluent-button">🌡️ Weather Stations</button>
          <button className="fluent-button">⚡ Electric Meters</button>
        </div>
      </div>
    </div>
  );
};

export default SpectrumDrones;
