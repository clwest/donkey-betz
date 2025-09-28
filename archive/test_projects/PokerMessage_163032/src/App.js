Here's a simple implementation of a Poker Message application using React. This example includes a component structure with modern React hooks, basic styling, and a responsive design.

```javascript
// App.js

import React, { useState } from 'react';
import './App.css'; // Importing the CSS for basic styling

const App = () => {
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');

  const handleInputChange = (e) => {
    setMessageInput(e.target.value);
  };

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      setMessages([...messages, messageInput.trim()]);
      setMessageInput('');
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Poker Game Messages</h1>
      </header>
      <main className="message-container">
        <div className="messages-list">
          {messages.length > 0 ? (
            messages.map((msg, index) => (
              <div key={index} className="message">
                {msg}
              </div>
            ))
          ) : (
            <div className="no-messages">No messages yet.</div>
          )}
        </div>
        <div className="message-input">
          <input
            type="text"
            value={messageInput}
            onChange={handleInputChange}
            placeholder="Type your message..."
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </main>
    </div>
  );
};

export default App;
```

### Additional CSS (App.css)

Here's an example of basic styling for the application. Make sure to create an `App.css` file in the same directory as `App.js`.

```css
/* App.css */

.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f5f5f5;
  font-family: Arial, sans-serif;
}

.app-header {
  background-color: #4caf50;
  color: white;
  padding: 20px;
  width: 100%;
  text-align: center;
}

.message-container {
  width: 90%;
  max-width: 600px;
  margin: 20px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: white;
  overflow-y: auto;
  height: 300px;
}

.messages-list {
  padding: 10px;
}

.message {
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.no-messages {
  padding: 10px;
  text-align: center;
  color: #999;
}

.message-input {
  display: flex;
  justify-content: space-between;
}

.message-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.message-input button {
  padding: 10px;
  margin-left: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.message-input button:hover {
  background-color: #45a049;
}
```

### Notes:
- You can further enhance the application by adding features such as user authentication, message deletion, or real-time messaging with a backend service.
- Ensure that you have installed React and created your project using `create-react-app` before implementing the above code.
- The styling can be expanded or customized based on design preferences to achieve a more professional UI.