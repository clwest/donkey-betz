Below is a sample implementation of a `PokerMessageApp` component in a React application. This component provides a basic structure for a poker game tracking application, incorporating hooks, a component structure, basic styling, and responsiveness.

```javascript
import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setMessages([...messages, inputValue]);
      setInputValue('');
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Poker Message Tracker</h1>
      </header>
      <main className="app-main">
        <form onSubmit={handleSubmit} className="message-form">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Type your message here..."
            className="message-input"
          />
          <button type="submit" className="submit-button">Send</button>
        </form>
        
        <div className="message-list">
          {messages.length === 0 ? (
            <p>No messages yet!</p>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="message-item">
                {msg}
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
```

### Explanation:
- **State Management**: The component uses `useState` to manage the list of messages and the current input value.
- **Form Handling**: The `handleInputChange` function updates the input value, while `handleSubmit` handles the form submission, adding the message to the list if it's not empty.
- **Rendering Messages**: It conditionally renders a message if the list is empty or maps over the `messages` array to display each message.
- **Basic Styling**: Styling is referenced from `App.css`, which you can customize as needed.

### CSS (App.css):
Here’s a simple CSS to add basic styling and responsiveness:

```css
.app-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.app-header {
  text-align: center;
}

.message-form {
  display: flex;
  margin-bottom: 20px;
}

.message-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-right: 10px;
}

.submit-button {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}

.submit-button:hover {
  background-color: #0056b3;
}

.message-list {
  border-top: 1px solid #ccc;
  padding-top: 10px;
}

.message-item {
  padding: 8px;
  border-bottom: 1px solid #eee;
}
```

### Notes:
- This code is a basic starting point for a poker message application. You can extend it with additional features like user authentication, message timestamps, or even multiplayer support as needed.
- Make sure to run `npm install` to set up your React environment if you haven't done so already.