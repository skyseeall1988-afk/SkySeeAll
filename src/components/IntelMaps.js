import React, { useState } from 'react';
import './IntelMaps.css';

const IntelMaps = ({ socket, activeSentry }) => {
  const [searchResults, setSearchResults] = useState(null);
  const [mapView, setMapView] = useState('2d');

  const geolocateIP = () => {
    const ip = prompt('Enter IP address to geolocate:');
    if (!ip || !socket || !activeSentry) return;
    
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'geolocate_ip',
      parameters: { ip }
    });
  };

  const phoneLookup = () => {
    const phone = prompt('Enter phone number:');
    if (!phone || !socket || !activeSentry) return;
    
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'phone_lookup',
      parameters: { phone }
    });
  };

  const shodanSearch = () => {
    const query = prompt('Enter Shodan search query:');
    if (!query || !socket || !activeSentry) return;
    
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'shodan_search',
      parameters: { query }
    });
  };

  return (
    <div className="intel-maps">
      <div className="fluent-card">
        <div className="card-header">
          <h2 className="card-title">🗺️ Intel & Maps - OSINT & Geospatial</h2>
          <div className="map-toggle">
            <button 
              className={`fluent-button small ${mapView === '2d' ? 'active' : ''}`}
              onClick={() => setMapView('2d')}
            >
              🗺️ 2D
            </button>
            <button 
              className={`fluent-button small ${mapView === '3d' ? 'active' : ''}`}
              onClick={() => setMapView('3d')}
            >
              🌍 3D
            </button>
          </div>
        </div>

        <div className="map-container">
          <div className={`map-view ${mapView}`}>
            {mapView === '2d' ? (
              <div className="map-2d">
                <p>🗺️ 2D Map View (Leaflet Integration)</p>
                <p className="hint">Displays target locations, heatmaps, and routes</p>
              </div>
            ) : (
              <div className="map-3d">
                <p>🌍 3D Terrain View (Cesium Integration)</p>
                <p className="hint">Interactive globe with elevation data and overlays</p>
              </div>
            )}
          </div>
        </div>

        <div className="map-controls">
          <button className="fluent-button">📍 Add Marker</button>
          <button className="fluent-button">🔥 Heatmap Overlay</button>
          <button className="fluent-button">📏 Measure Distance</button>
          <button className="fluent-button">🛰️ Satellite View</button>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🔍 OSINT Tools</h3>
          </div>
          <button className="fluent-button" onClick={geolocateIP}>
            🌐 IP Geolocation
          </button>
          <button className="fluent-button" onClick={phoneLookup}>
            📞 Phone Number Lookup
          </button>
          <button className="fluent-button">👤 Username Search</button>
          <button className="fluent-button">✉️ Email Lookup</button>
          <button className="fluent-button">🔗 MAC Address Vendor</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🔐 Security Intelligence</h3>
          </div>
          <button className="fluent-button" onClick={shodanSearch}>
            🔎 Shodan Search
          </button>
          <button className="fluent-button">🔒 SSL Certificate Check</button>
          <button className="fluent-button">🔑 Leaked Credentials</button>
          <button className="fluent-button">🛡️ Vulnerability Check</button>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🌐 Domain Intelligence</h3>
          </div>
          <button className="fluent-button">🔗 Subdomain Enumeration</button>
          <button className="fluent-button">📋 WHOIS Lookup</button>
          <button className="fluent-button">📧 Email Harvester</button>
          <button className="fluent-button">🔍 DNS Records</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🛰️ Satellite & Weather</h3>
          </div>
          <button className="fluent-button">🌤️ NOAA Overlay</button>
          <button className="fluent-button">☄️ Meteor Tracking</button>
          <button className="fluent-button">🛰️ Satellite Passes</button>
          <button className="fluent-button">🌊 Weather Radar</button>
        </div>
      </div>

      {searchResults && (
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">📊 Search Results</h3>
          </div>
          <div className="results-container">
            <pre className="results-data">
              {JSON.stringify(searchResults, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelMaps;
