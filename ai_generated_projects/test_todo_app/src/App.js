```javascript
import React, { useState } from 'react';
import './App.css'; // Importing the CSS for basic styling

const App = () => {
  const [tasks, setTasks] = useState([]);
  const [taskInput, setTaskInput] = useState('');

  const handleInputChange = (e) => {
    setTaskInput(e.target.value);
  };

  const handleAddTask = () => {
    if (taskInput.trim()) {
      setTasks([...tasks, { text: taskInput, completed: false }]);
      setTaskInput('');
    }
  };

  const handleToggleTask = (index) => {
    const updatedTasks = tasks.map((task, i) => 
      i === index ? { ...task, completed: !task.completed } : task
    );
    setTasks(updatedTasks);
  };

  const handleDeleteTask = (index) => {
    const updatedTasks = tasks.filter((_, i) => i !== index);
    setTasks(updatedTasks);
  };

  return (
    <div className="app">
      <h1 className="app-title">Todo List</h1>
      <div className="input-container">
        <input
          type="text"
          value={taskInput}
          onChange={handleInputChange}
          placeholder="Add a new task..."
          className="task-input"
        />
        <button onClick={handleAddTask} className="add-task-button">Add Task</button>
      </div>
      <ul className="task-list">
        {tasks.map((task, index) => (
          <li key={index} className={`task-item ${task.completed ? 'completed' : ''}`}>
            <span onClick={() => handleToggleTask(index)} className="task-text">{task.text}</span>
            <button onClick={() => handleDeleteTask(index)} className="delete-task-button">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default App;
```

### CSS (App.css)
Here’s a simple CSS for basic styling and responsive design:

```css
body {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  margin: 0;
  padding: 0;
}

.app {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-title {
  text-align: center;
  color: #333;
}

.input-container {
  display: flex;
  justify-content: space-between;
}

.task-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.add-task-button {
  padding: 10px 15px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-task-button:hover {
  background-color: #218838;
}

.task-list {
  list-style-type: none;
  padding: 0;
}

.task-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.task-text {
  cursor: pointer;
}

.completed {
  text-decoration: line-through;
  color: #888;
}

.delete-task-button {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
}

.delete-task-button:hover {
  background-color: #c82333;
}
```

This code provides a simple yet functional todo list application with modern React hooks, basic styling, and a professional UI.