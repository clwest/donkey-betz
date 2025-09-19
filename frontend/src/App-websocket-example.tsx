// Example integration in your main React app
// Shows how to properly initialize WebSockets to avoid the hard refresh issue

import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { WebSocketInitializer, WebSocketStatusIndicator } from './components/WebSocketInitializer';
import { YourMainAppComponent } from './YourMainAppComponent'; // Your existing app

function App() {
  return (
    <BrowserRouter>
      {/* Wrap your entire app with WebSocketInitializer */}
      <WebSocketInitializer showStatus={true}>
        {/* Your existing app components go here */}
        <YourMainAppComponent />
        
        {/* Optional: Add status indicator in corner */}
        <WebSocketStatusIndicator />
      </WebSocketInitializer>
    </BrowserRouter>
  );
}

export default App;

// Alternative: If you don't want the loading screen, set showStatus={false}
// This will render your app immediately while WebSockets connect in background
function AppWithoutLoadingScreen() {
  return (
    <BrowserRouter>
      <WebSocketInitializer showStatus={false}>
        <YourMainAppComponent />
      </WebSocketInitializer>
    </BrowserRouter>
  );
}
