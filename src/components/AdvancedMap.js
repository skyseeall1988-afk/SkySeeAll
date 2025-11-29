// V14.6 Feature: Advanced Interactive Mapping with Satellite Imagery & Live Tracking
import React, { useState, useEffect, useRef } from 'react';
import './AdvancedMap.css';

const AdvancedMap = () => {
    const [mapMode, setMapMode] = useState('satellite'); // satellite, street, hybrid, terrain
    const [imageryDate, setImageryDate] = useState('live'); // live (1-5 days), recent (1-6 months)
    const [overlays, setOverlays] = useState({
        cellTowers: true,
        wifi: true,
        bluetooth: true,
        drones: true,
        cameras: true,
        devices: true,
        coverage: true,
        tracking: true
    });
    const [splitScreen, setSplitScreen] = useState(false);
    const [selectedCamera, setSelectedCamera] = useState(null);
    const [userLocation, setUserLocation] = useState({ lat: 37.7749, lon: -122.4194 });
    const [trackingData, setTrackingData] = useState({
        cellTowers: [],
        wifiNetworks: [],
        bluetoothDevices: [],
        drones: [],
        cameras: [],
        connectedDevices: []
    });
    const [distanceInfo, setDistanceInfo] = useState(null);
    const [walkingPath, setWalkingPath] = useState([]);
    const [frequencyScanner, setFrequencyScanner] = useState({
        active: false,
        frequency: 2412, // MHz
        mode: 'scan' // scan, tune, monitor
    });
    const [savedConnections, setSavedConnections] = useState([]);
    const mapRef = useRef(null);
    const cameraStreamRef = useRef(null);

    useEffect(() => {
        initializeMap();
        startLiveTracking();
        loadSavedConnections();
    }, []);

    useEffect(() => {
        if (overlays.cellTowers) fetchCellTowers();
        if (overlays.wifi) fetchWifiNetworks();
        if (overlays.bluetooth) fetchBluetoothDevices();
        if (overlays.drones) fetchDrones();
        if (overlays.cameras) fetchCameras();
    }, [overlays, userLocation]);

    const initializeMap = () => {
        // Initialize Leaflet map with satellite imagery
        // Using multiple tile providers for up-to-date imagery
        console.log('Initializing advanced map with satellite imagery');
    };

    const startLiveTracking = () => {
        // Real-time location tracking with 2-3 second updates
        const interval = setInterval(() => {
            updateUserLocation();
            updateWalkingPath();
            calculateDistances();
            scanNearbyDevices();
        }, 2500); // 2.5 second intervals

        return () => clearInterval(interval);
    };

    const updateUserLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const newLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    setUserLocation(newLocation);
                    setWalkingPath(prev => [...prev, newLocation]);
                },
                (error) => console.error('Geolocation error:', error),
                { enableHighAccuracy: true, timeout: 2000, maximumAge: 0 }
            );
        }
    };

    const fetchCellTowers = async () => {
        // OpenCelliD API or Mozilla Location Service for cell tower data
        try {
            const response = await fetch('/intel/cell_towers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: userLocation.lat,
                    lon: userLocation.lon,
                    radius: 5000 // 5km
                })
            });
            const data = await response.json();
            setTrackingData(prev => ({ ...prev, cellTowers: data.towers || [] }));
        } catch (error) {
            console.error('Cell tower fetch error:', error);
        }
    };

    const fetchWifiNetworks = async () => {
        try {
            const response = await fetch('/tactical/wifi_scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    use_proxy: true,
                    location: { lat: userLocation.lat, lon: userLocation.lon }
                })
            });
            const data = await response.json();
            setTrackingData(prev => ({ ...prev, wifiNetworks: data.networks || [] }));
        } catch (error) {
            console.error('Wi-Fi scan error:', error);
        }
    };

    const fetchBluetoothDevices = async () => {
        try {
            const response = await fetch('/tactical/bluetooth_scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pet_id: 'dashboard' })
            });
            const data = await response.json();
            setTrackingData(prev => ({ ...prev, bluetoothDevices: data.devices || [] }));
        } catch (error) {
            console.error('Bluetooth scan error:', error);
        }
    };

    const fetchDrones = async () => {
        try {
            const response = await fetch('/spectrum/detect_drones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: userLocation.lat,
                    lon: userLocation.lon,
                    pet_id: 'dashboard'
                })
            });
            const data = await response.json();
            
            // Also fetch from drone tracking API (e.g., AirMap, DroneRadar)
            const droneApiResponse = await fetch('/spectrum/drone_registry', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: userLocation.lat,
                    lon: userLocation.lon,
                    radius: 10000 // 10km
                })
            });
            const droneApiData = await droneApiResponse.json();
            
            setTrackingData(prev => ({ 
                ...prev, 
                drones: [...(data.drones || []), ...(droneApiData.drones || [])]
            }));
        } catch (error) {
            console.error('Drone detection error:', error);
        }
    };

    const fetchCameras = async () => {
        try {
            const response = await fetch('/vision/public_webcams', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: userLocation.lat,
                    lon: userLocation.lon,
                    radius: 50
                })
            });
            const data = await response.json();
            setTrackingData(prev => ({ ...prev, cameras: data.webcams || [] }));
        } catch (error) {
            console.error('Camera fetch error:', error);
        }
    };

    const calculateDistances = () => {
        // Calculate distance to nearest cell tower, Wi-Fi AP, etc.
        const distances = {
            nearestCellTower: null,
            nearestWifi: null,
            nearestCamera: null,
            connectedCellTower: null,
            signalStrength: null
        };

        if (trackingData.cellTowers.length > 0) {
            const nearest = findNearestPoint(userLocation, trackingData.cellTowers);
            distances.nearestCellTower = {
                ...nearest,
                distance: calculateDistance(userLocation, nearest)
            };
        }

        if (trackingData.wifiNetworks.length > 0) {
            const nearest = findNearestPoint(userLocation, trackingData.wifiNetworks);
            distances.nearestWifi = {
                ...nearest,
                distance: calculateDistance(userLocation, nearest)
            };
        }

        setDistanceInfo(distances);
    };

    const calculateDistance = (point1, point2) => {
        // Haversine formula for distance calculation
        const R = 6371e3; // Earth radius in meters
        const φ1 = point1.lat * Math.PI / 180;
        const φ2 = point2.lat * Math.PI / 180;
        const Δφ = (point2.lat - point1.lat) * Math.PI / 180;
        const Δλ = (point2.lon - point1.lon) * Math.PI / 180;

        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        return R * c; // Distance in meters
    };

    const findNearestPoint = (origin, points) => {
        let nearest = points[0];
        let minDistance = Infinity;

        points.forEach(point => {
            const distance = calculateDistance(origin, point);
            if (distance < minDistance) {
                minDistance = distance;
                nearest = point;
            }
        });

        return nearest;
    };

    const scanNearbyDevices = async () => {
        // Auto-scan for devices and attempt connections
        try {
            const response = await fetch('/tactical/device_scan_auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    location: userLocation,
                    auto_connect: true,
                    save_credentials: true
                })
            });
            const data = await response.json();
            
            if (data.new_connections) {
                data.new_connections.forEach(saveConnection);
            }
        } catch (error) {
            console.error('Auto-scan error:', error);
        }
    };

    const saveConnection = async (connectionData) => {
        // Save connection details, credentials, images, and metadata
        try {
            const response = await fetch('/tactical/save_connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...connectionData,
                    location: userLocation,
                    timestamp: new Date().toISOString(),
                    walking_path: walkingPath.slice(-10) // Last 10 positions
                })
            });
            const data = await response.json();
            
            if (data.success) {
                setSavedConnections(prev => [...prev, data.connection]);
            }
        } catch (error) {
            console.error('Save connection error:', error);
        }
    };

    const loadSavedConnections = async () => {
        try {
            const response = await fetch('/tactical/saved_connections');
            const data = await response.json();
            setSavedConnections(data.connections || []);
        } catch (error) {
            console.error('Load connections error:', error);
        }
    };

    const controlCamera = async (cameraId, command) => {
        // PTZ controls, snapshot, recording
        try {
            const response = await fetch(`/vision/camera_control/${cameraId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });
            return await response.json();
        } catch (error) {
            console.error('Camera control error:', error);
        }
    };

    const tuneFrequency = async (frequency) => {
        setFrequencyScanner(prev => ({ ...prev, frequency }));
        
        try {
            const response = await fetch('/spectrum/tune', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ frequency, pet_id: 'dashboard' })
            });
            return await response.json();
        } catch (error) {
            console.error('Frequency tune error:', error);
        }
    };

    const scanFrequencies = async (startFreq, endFreq) => {
        setFrequencyScanner(prev => ({ ...prev, active: true, mode: 'scan' }));
        
        try {
            const response = await fetch('/spectrum/frequency_scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_freq: startFreq,
                    end_freq: endFreq,
                    pet_id: 'dashboard'
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Frequency scan error:', error);
        } finally {
            setFrequencyScanner(prev => ({ ...prev, active: false }));
        }
    };

    const toggleOverlay = (overlayName) => {
        setOverlays(prev => ({ ...prev, [overlayName]: !prev[overlayName] }));
    };

    const formatDistance = (meters) => {
        if (meters < 1000) return `${meters.toFixed(0)}m`;
        return `${(meters / 1000).toFixed(2)}km`;
    };

    return (
        <div className="advanced-map-container">
            {/* Map Controls */}
            <div className="map-controls-panel">
                <h3>🗺️ Map Controls</h3>
                
                <div className="control-section">
                    <label>Map Mode</label>
                    <select value={mapMode} onChange={(e) => setMapMode(e.target.value)}>
                        <option value="satellite">Satellite</option>
                        <option value="street">Street</option>
                        <option value="hybrid">Hybrid</option>
                        <option value="terrain">Terrain</option>
                    </select>
                </div>

                <div className="control-section">
                    <label>Imagery Date</label>
                    <select value={imageryDate} onChange={(e) => setImageryDate(e.target.value)}>
                        <option value="live">Live (1-5 days)</option>
                        <option value="recent">Recent (1-6 months)</option>
                    </select>
                </div>

                <div className="control-section">
                    <label>Overlays</label>
                    {Object.keys(overlays).map(overlay => (
                        <div key={overlay} className="overlay-toggle">
                            <input
                                type="checkbox"
                                checked={overlays[overlay]}
                                onChange={() => toggleOverlay(overlay)}
                                id={`overlay-${overlay}`}
                            />
                            <label htmlFor={`overlay-${overlay}`}>
                                {overlay.charAt(0).toUpperCase() + overlay.slice(1).replace(/([A-Z])/g, ' $1')}
                            </label>
                        </div>
                    ))}
                </div>

                <div className="control-section">
                    <label>Split Screen</label>
                    <button 
                        className={`fluent-button ${splitScreen ? 'active' : ''}`}
                        onClick={() => setSplitScreen(!splitScreen)}
                    >
                        {splitScreen ? '📺 Single View' : '🔲 Split Screen'}
                    </button>
                </div>

                <div className="control-section">
                    <label>Frequency Scanner</label>
                    <div className="frequency-controls">
                        <input
                            type="number"
                            value={frequencyScanner.frequency}
                            onChange={(e) => setFrequencyScanner(prev => ({ 
                                ...prev, 
                                frequency: parseInt(e.target.value) 
                            }))}
                            min="24"
                            max="6000"
                        />
                        <span className="frequency-unit">MHz</span>
                        <button 
                            className="fluent-button-small"
                            onClick={() => tuneFrequency(frequencyScanner.frequency)}
                        >
                            Tune
                        </button>
                        <button 
                            className="fluent-button-small"
                            onClick={() => scanFrequencies(2400, 2500)}
                        >
                            Scan 2.4GHz
                        </button>
                        <button 
                            className="fluent-button-small"
                            onClick={() => scanFrequencies(5150, 5850)}
                        >
                            Scan 5GHz
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Map Display */}
            <div className={`map-display ${splitScreen ? 'split' : 'full'}`}>
                <div className="map-canvas" ref={mapRef}>
                    {/* Leaflet map renders here */}
                    <div className="map-placeholder">
                        <p>🗺️ Interactive Map with Satellite Imagery</p>
                        <p className="map-coords">
                            📍 {userLocation.lat.toFixed(6)}, {userLocation.lon.toFixed(6)}
                        </p>
                    </div>

                    {/* Live Walking Path Overlay */}
                    {overlays.tracking && walkingPath.length > 0 && (
                        <svg className="walking-path-overlay">
                            <polyline
                                points={walkingPath.map(p => `${p.lon},${p.lat}`).join(' ')}
                                stroke="#00ff00"
                                strokeWidth="3"
                                fill="none"
                            />
                        </svg>
                    )}

                    {/* Cell Tower Overlays */}
                    {overlays.cellTowers && trackingData.cellTowers.map((tower, idx) => (
                        <div 
                            key={`tower-${idx}`} 
                            className="map-marker cell-tower"
                            style={{
                                left: `${tower.lon}px`,
                                top: `${tower.lat}px`
                            }}
                        >
                            <div className="tower-icon">📡</div>
                            <div className="tower-info">
                                <span>{tower.operator}</span>
                                <span>{formatDistance(tower.distance)}</span>
                                <span>{tower.coverage_radius}m radius</span>
                            </div>
                        </div>
                    ))}

                    {/* Wi-Fi Network Overlays */}
                    {overlays.wifi && trackingData.wifiNetworks.map((network, idx) => (
                        <div 
                            key={`wifi-${idx}`} 
                            className="map-marker wifi-network"
                            style={{
                                left: `${network.lon}px`,
                                top: `${network.lat}px`
                            }}
                        >
                            <div className="wifi-icon">📶</div>
                            <div className="wifi-info">
                                <span>{network.ssid}</span>
                                <span>{network.signal} dBm</span>
                            </div>
                        </div>
                    ))}

                    {/* Drone Overlays */}
                    {overlays.drones && trackingData.drones.map((drone, idx) => (
                        <div 
                            key={`drone-${idx}`} 
                            className="map-marker drone"
                            style={{
                                left: `${drone.lon}px`,
                                top: `${drone.lat}px`
                            }}
                        >
                            <div className="drone-icon">🚁</div>
                            <div className="drone-info">
                                <span>{drone.model || 'Unknown Drone'}</span>
                                <span>Alt: {drone.altitude}m</span>
                                <span>{formatDistance(drone.distance)}</span>
                            </div>
                        </div>
                    ))}

                    {/* Camera Overlays */}
                    {overlays.cameras && trackingData.cameras.map((camera, idx) => (
                        <div 
                            key={`camera-${idx}`} 
                            className="map-marker camera"
                            style={{
                                left: `${camera.lon}px`,
                                top: `${camera.lat}px`
                            }}
                            onClick={() => setSelectedCamera(camera)}
                        >
                            <div className="camera-icon">📹</div>
                            <div className="camera-info">
                                <span>{camera.title}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Split Screen Camera View */}
                {splitScreen && (
                    <div className="camera-view" ref={cameraStreamRef}>
                        {selectedCamera ? (
                            <>
                                <div className="camera-header">
                                    <h4>📹 {selectedCamera.title}</h4>
                                    <button onClick={() => setSelectedCamera(null)}>✕</button>
                                </div>
                                <iframe 
                                    src={selectedCamera.player}
                                    title={selectedCamera.title}
                                    className="camera-stream"
                                />
                                <div className="camera-controls">
                                    <button onClick={() => controlCamera(selectedCamera.id, 'up')}>⬆️</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'down')}>⬇️</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'left')}>⬅️</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'right')}>➡️</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'zoom_in')}>🔍+</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'zoom_out')}>🔍-</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'snapshot')}>📸</button>
                                    <button onClick={() => controlCamera(selectedCamera.id, 'record')}>⏺️</button>
                                </div>
                            </>
                        ) : (
                            <div className="no-camera-selected">
                                <p>📹 Select a camera from the map</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Live Distance Info Panel */}
            <div className="distance-info-panel">
                <h3>📏 Distance Information</h3>
                {distanceInfo && (
                    <>
                        {distanceInfo.nearestCellTower && (
                            <div className="distance-item">
                                <span className="distance-icon">📡</span>
                                <span className="distance-label">Nearest Cell Tower:</span>
                                <span className="distance-value">
                                    {formatDistance(distanceInfo.nearestCellTower.distance)}
                                </span>
                            </div>
                        )}
                        {distanceInfo.nearestWifi && (
                            <div className="distance-item">
                                <span className="distance-icon">📶</span>
                                <span className="distance-label">Nearest Wi-Fi:</span>
                                <span className="distance-value">
                                    {formatDistance(distanceInfo.nearestWifi.distance)}
                                </span>
                            </div>
                        )}
                        {distanceInfo.nearestCamera && (
                            <div className="distance-item">
                                <span className="distance-icon">📹</span>
                                <span className="distance-label">Nearest Camera:</span>
                                <span className="distance-value">
                                    {formatDistance(distanceInfo.nearestCamera.distance)}
                                </span>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Saved Connections Panel */}
            <div className="saved-connections-panel">
                <h3>💾 Saved Connections</h3>
                <div className="connections-list">
                    {savedConnections.map((conn, idx) => (
                        <div key={`conn-${idx}`} className="connection-item">
                            <div className="connection-header">
                                <span className="connection-type">{conn.type}</span>
                                <span className="connection-time">{new Date(conn.timestamp).toLocaleString()}</span>
                            </div>
                            <div className="connection-details">
                                <p><strong>SSID/Name:</strong> {conn.ssid || conn.name}</p>
                                <p><strong>Location:</strong> {conn.location.lat.toFixed(6)}, {conn.location.lon.toFixed(6)}</p>
                                {conn.credentials && <p><strong>✓</strong> Credentials saved</p>}
                                {conn.image && <img src={conn.image} alt="Connection capture" className="connection-image" />}
                                {conn.devices && <p><strong>Devices:</strong> {conn.devices.length}</p>}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AdvancedMap;
