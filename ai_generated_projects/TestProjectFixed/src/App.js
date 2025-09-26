```javascript
import React from 'react';
import './App.css'; // Basic styling for the application
import Dashboard from './components/Dashboard';
import Analytics from './components/Analytics';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Test Project Fixed</h1>
      </header>
      <main>
        <Dashboard />
        <Analytics />
      </main>
    </div>
  );
};

export default App;
```

```javascript
// components/Dashboard.js
import React from 'react';
import './Dashboard.css'; // Styling for Dashboard component

const Dashboard = () => {
  return (
    <section className="Dashboard">
      <h2>Dashboard</h2>
      <p>Welcome to the dashboard! Here you can find an overview of your project.</p>
      {/* Add more dashboard content here */}
    </section>
  );
};

export default Dashboard;
```

```javascript
// components/Analytics.js
import React from 'react';
import './Analytics.css'; // Styling for Analytics component

const Analytics = () => {
  return (
    <section className="Analytics">
      <h2>Analytics</h2>
      <p>Here are your analytics data. Visualize your progress and metrics.</p>
      {/* Add more analytics content here */}
    </section>
  );
};

export default Analytics;
```

```css
/* App.css */
.App {
  text-align: center;
  font-family: Arial, sans-serif;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

/* Dashboard.css */
.Dashboard {
  padding: 20px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  margin: 20px;
  border-radius: 8px;
}

/* Analytics.css */
.Analytics {
  padding: 20px;
  background-color: #e9ecef;
  border: 1px solid #ddd;
  margin: 20px;
  border-radius: 8px;
}

/* Responsive design */
@media (max-width: 600px) {
  .Dashboard, .Analytics {
    margin: 10px;
    padding: 10px;
  }
}
```

### Explanation:
1. **Component Structure**: The application is structured with a main `App` component that renders two child components: `Dashboard` and `Analytics`.
2. **Modern React with Hooks**: The components are functional components, leveraging modern React practices.
3. **Basic Styling**: Basic styling is applied through CSS files associated with each component.
4. **Responsive Design**: Media queries are included to ensure the components are responsive on smaller screens.
5. **Professional UI**: Simple and clean design to maintain a professional appearance. You can enhance this further with libraries like Material-UI or Bootstrap if needed.