import React, { useRef, useEffect } from 'react';
import './LiveFeedPanel.css';

const LiveFeedPanel = ({ activeModule, liveFeeds, socket }) => {
  const feedRef = useRef(null);

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = 0;
    }
  }, [liveFeeds]);

  const getFeedData = () => {
    switch (activeModule) {
      case 'tactical':
        return liveFeeds.tactical;
      case 'spectrum':
        return liveFeeds.spectrum;
      case 'vision':
        return liveFeeds.video;
      default:
        return [];
    }
  };

  const renderFeedItem = (item, index) => {
    const timestamp = new Date(item.timestamp || Date.now()).toLocaleTimeString();

    if (activeModule === 'tactical') {
      return (
        <div key={index} className="feed-item tactical-feed">
          <div className="feed-timestamp">{timestamp}</div>
          <div className="feed-content">
            {item.ssid && (
              <div className="feed-row">
                <span className="feed-label">SSID:</span>
                <span className="feed-value">{item.ssid}</span>
              </div>
            )}
            {item.bssid && (
              <div className="feed-row">
                <span className="feed-label">BSSID:</span>
                <span className="feed-value mono">{item.bssid}</span>
              </div>
            )}
            {item.signal && (
              <div className="feed-row">
                <span className="feed-label">Signal:</span>
                <span className={`feed-value signal-${item.signal > -50 ? 'strong' : item.signal > -70 ? 'medium' : 'weak'}`}>
                  {item.signal} dBm
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }

    if (activeModule === 'spectrum') {
      return (
        <div key={index} className="feed-item spectrum-feed">
          <div className="feed-timestamp">{timestamp}</div>
          <div className="spectrum-bar-container">
            {item.fft && item.fft.map((value, i) => (
              <div 
                key={i}
                className="spectrum-bar"
                style={{ 
                  height: `${Math.max(value * 100, 2)}%`,
                  background: `hsl(${240 - (value * 120)}, 80%, 50%)`
                }}
              />
            ))}
          </div>
        </div>
      );
    }

    if (activeModule === 'vision') {
      return (
        <div key={index} className="feed-item video-feed">
          <div className="feed-timestamp">{timestamp}</div>
          {item.frame && (
            <img 
              src={`data:image/jpeg;base64,${item.frame}`}
              alt="Video Frame"
              className="video-thumbnail"
            />
          )}
        </div>
      );
    }

    return null;
  };

  const feedData = getFeedData();

  return (
    <div className="live-feed-panel acrylic">
      <div className="feed-header">
        <h3>Live Feed</h3>
        <div className="feed-stats">
          <span className="pulse indicator active"></span>
          <span>{feedData.length} items</span>
        </div>
      </div>

      <div className="feed-container" ref={feedRef}>
        {feedData.length === 0 ? (
          <div className="feed-empty">
            <div className="loading-spinner"></div>
            <p>Waiting for live data...</p>
          </div>
        ) : (
          feedData.map((item, index) => renderFeedItem(item, index))
        )}
      </div>
    </div>
  );
};

export default LiveFeedPanel;
