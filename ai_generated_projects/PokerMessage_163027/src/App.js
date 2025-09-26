Sure! Below is a sample implementation of a React `App.js` component for a Poker Message application. This code will include basic structure, component organization, styling, and responsiveness using CSS-in-JS.

```javascript
import React, { useState } from 'react';
import './App.css';

// Message component to display individual messages
const Message = ({ message }) => (
  <div className="message">
    <p>{message}</p>
  </div>
);

// MessageInput component to handle message input
const MessageInput = ({ onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Type your message..."
      />
      <button type="submit">Send</button>
    </form>
  );
};

// Main App component
const App = () => {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = (message) => {
    setMessages([...messages, message]);
  };

  return (
    <div className="app">
      <h1>Poker Game Messages</h1>
      <div className="messages-list">
        {messages.map((msg, index) => (
          <Message key={index} message={msg} />
        ))}
      </div>
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default App;
```

### Basic CSS (App.css)

```css
* {
  box-sizing: border-box;
}

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
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
}

.messages-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: #fafafa;
}

.message {
  padding: 8px;
  margin: 5px 0;
  border-radius: 5px;
  background-color: #e7f3fe;
  color: #31708f;
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
  padding: 10px 15px;
  margin-left: 10px;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}

.message-input button:hover {
  background-color: #0056b3;
}

/* Responsive Design */
@media (max-width: 600px) {
  .app {
    padding: 10px;
  }

  .message-input {
    flex-direction: column;
  }

  .message-input input {
    margin-bottom: 10px;
  }
}
```

### Explanation:
- The `App` component manages the state of messages and renders the message list and input form.
- The `Message` component is responsible for displaying individual messages.
- The `MessageInput` component handles user input and submits messages.
- Basic styling is provided to create a clean, modern UI, and responsiveness is achieved using media queries.

This setup can be further expanded based on additional features you might want to implement (like user authentication, message timestamps, etc.).