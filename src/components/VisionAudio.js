import React, { useState, useRef } from 'react';
import './VisionAudio.css';

const VisionAudio = ({ socket, activeSentry, liveFeeds }) => {
  const [cameras, setCameras] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [speakersMuted, setSpeakersMuted] = useState(false);
  const videoRef = useRef(null);

  const discoverCameras = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'discover_cameras',
      parameters: {}
    });
  };

  const startStream = (cameraUrl) => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'stream_camera',
      parameters: { camera_url: cameraUrl }
    });
    setStreaming(true);
  };

  const muteSpeakers = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'mute_speakers',
      parameters: {}
    });
    setSpeakersMuted(true);
  };

  const unmuteSpeakers = () => {
    if (!socket || !activeSentry) return;
    socket.emit('command', {
      pet_id: activeSentry,
      command_type: 'unmute_speakers',
      parameters: {}
    });
    setSpeakersMuted(false);
  };

  return (
    <div className="vision-audio">
      <div className="fluent-card">
        <div className="card-header">
          <h2 className="card-title">📹 Vision & Audio - Multimedia Surveillance</h2>
          <div className="header-actions">
            {speakersMuted ? (
              <button className="fluent-button warning" onClick={unmuteSpeakers}>
                🔊 Unmute Speakers
              </button>
            ) : (
              <button className="fluent-button" onClick={muteSpeakers}>
                🔇 Mute Speakers
              </button>
            )}
          </div>
        </div>

        <div className="video-player-container">
          <div className="video-player">
            {streaming ? (
              <video 
                ref={videoRef}
                autoPlay
                className="live-video"
              >
                <p>Live feed from camera</p>
              </video>
            ) : (
              <div className="no-video">
                <p>No active video stream</p>
                <p className="hint">Discover cameras and start streaming</p>
              </div>
            )}
          </div>

          <div className="video-controls">
            <button className="fluent-button">⏺️ Record</button>
            <button className="fluent-button">📸 Snapshot</button>
            <button className="fluent-button">🎥 Motion Detection</button>
            <button className="fluent-button danger">⏹️ Stop Stream</button>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🎥 Camera Discovery</h3>
          </div>
          <button className="fluent-button" onClick={discoverCameras}>
            🔍 Discover IP Cameras
          </button>
          <button className="fluent-button">📹 RTSP Scanner</button>
          <button className="fluent-button">🌐 HTTP Camera Finder</button>

          <div className="camera-list">
            {cameras.length > 0 ? (
              cameras.map((cam, idx) => (
                <div key={idx} className="camera-item reveal-hover">
                  <div className="camera-info">
                    <span className="camera-name">📹 Camera {idx + 1}</span>
                    <span className="camera-ip">{cam.ip}</span>
                  </div>
                  <button 
                    className="fluent-button small"
                    onClick={() => startStream(cam.url)}
                  >
                    ▶️ Stream
                  </button>
                </div>
              ))
            ) : (
              <p className="empty-text">No cameras found</p>
            )}
          </div>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🤖 Computer Vision</h3>
          </div>
          <button className="fluent-button">👤 Face Recognition</button>
          <button className="fluent-button">🚗 License Plate Reader</button>
          <button className="fluent-button">🎯 Object Detection</button>
          <button className="fluent-button">🚶 Motion Tracking</button>
        </div>
      </div>

      <div className="grid-2">
        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">🎤 Audio Analysis</h3>
          </div>
          <button className="fluent-button">📊 Decibel Meter</button>
          <button className="fluent-button">🔉 Infrasound Detection</button>
          <button className="fluent-button">🦇 Ultrasound Analysis</button>
          <button className="fluent-button">🎵 Audio Spectrum</button>
        </div>

        <div className="fluent-card">
          <div className="card-header">
            <h3 className="card-title">📻 Audio Streaming</h3>
          </div>
          <button className="fluent-button">🚓 Police Radio</button>
          <button className="fluent-button">📡 Ham Radio</button>
          <button className="fluent-button">🚒 Fire/EMS Radio</button>
          <button className="fluent-button">✈️ Air Traffic Control</button>
        </div>
      </div>

      <div className="fluent-card">
        <div className="card-header">
          <h3 className="card-title">📹 Recording Management</h3>
        </div>
        <div className="grid-3">
          <button className="fluent-button">📂 View Recordings</button>
          <button className="fluent-button">⬇️ Download Latest</button>
          <button className="fluent-button danger">🗑️ Clear Storage</button>
        </div>
      </div>
    </div>
  );
};

export default VisionAudio;
