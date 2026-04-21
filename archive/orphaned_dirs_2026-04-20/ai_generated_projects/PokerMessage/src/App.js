Certainly! Below is a simple implementation of a Poker Message application using React. This code includes hooks, a basic component structure, and basic styling. The app will allow users to send messages during a poker game.

```javascript
// App.js
import React, { useState } from 'react';
import './App.css';

// Message Component
const Message = ({ text }) => {
  return (
    <div className="message">
      {text}
    </div>
  );
};

// MessageInput Component
const MessageInput = ({ onSend }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <div className="message-input">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};

// App Component
const App = () => {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = (message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  return (
    <div className="app">
      <h1>Poker Game Messages</h1>
      <div className="messages-list">
        {messages.map((msg, index) => (
          <Message key={index} text={msg} />
        ))}
      </div>
      <MessageInput onSend={handleSendMessage} />
    </div>
  );
};

export default App;
```

### App.css
Here’s a basic CSS file to style the components:

```css
/* App.css */
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
}

.app {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
}

.messages-list {
  margin-bottom: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.message {
  padding: 10px;
  margin: 5px 0;
  background-color: #e1f5fe;
  border-radius: 4px;
}

.message-input {
  display: flex;
}

.message-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.message-input button {
  padding: 10px;
  margin-left: 5px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.message-input button:hover {
  background-color: #0056b3;
}
```

### Explanation:
1. **Message Component**: Displays individual messages.
2. **MessageInput Component**: Contains an input field and a button to send messages.
3. **App Component**: Manages the state of the messages and renders the components.
4. **Styling**: Basic styles for layout, responsive design, and a professional appearance.

This setup provides a good starting point for a poker game messaging application. You can further enhance it by adding features like user authentication, message timestamps, or even real-time messaging with WebSocket.