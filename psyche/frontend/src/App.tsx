import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [imageData, setImageData] = useState<string | null>(null);
  const [timestamp, setTimestamp] = useState<string | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('Connected to the server');
      // Keep connection alive
      setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setImageData(`data:image/jpeg;base64,${data.image}`);
      
      // Format timestamp for display
      const date = new Date(data.timestamp);
      setTimestamp(date.toLocaleTimeString() + '.' + 
                  date.getMilliseconds().toString().padStart(3, '0'));
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('Disconnected from the server');
    };
    
    setSocket(ws);
    
    // Cleanup on component unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="app-container">
      <div className="image-container">
        {imageData ? (
          <img 
            src={imageData} 
            alt="Streamed content" 
            className="streamed-image"
          />
        ) : (
          <div className="placeholder">Waiting for image stream...</div>
        )}
      </div>
      
      {timestamp && (
        <div className="timestamp">
          {timestamp}
        </div>
      )}
    </div>
  );
}

export default App;
