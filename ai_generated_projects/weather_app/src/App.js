```javascript
import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [location, setLocation] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [error, setError] = useState(null);

  const apiKey = 'YOUR_API_KEY'; // Replace with your OpenWeatherMap API key

  const fetchWeatherData = async (city) => {
    try {
      const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`);
      if (!response.ok) throw new Error('City not found');
      const data = await response.json();
      setWeatherData(data);
      fetchForecastData(data.coord.lat, data.coord.lon);
      setError(null);
    } catch (err) {
      setError(err.message);
      setWeatherData(null);
      setForecastData(null);
    }
  };

  const fetchForecastData = async (lat, lon) => {
    try {
      const response = await fetch(`https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`);
      const data = await response.json();
      setForecastData(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (location.trim()) {
      fetchWeatherData(location.trim());
      setLocation('');
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Weather App</h1>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter city name"
            className="search-input"
          />
          <button type="submit" className="search-button">Search</button>
        </form>
      </header>
      <main className="app-main">
        {error && <p className="error">{error}</p>}
        {weatherData && (
          <div className="weather-card">
            <h2>{weatherData.name}</h2>
            <p>{Math.round(weatherData.main.temp)}°C</p>
            <p>{weatherData.weather[0].description}</p>
          </div>
        )}
        {forecastData && (
          <div className="forecast">
            <h3>5-Day Forecast</h3>
            <div className="forecast-list">
              {forecastData.list.slice(0, 5).map((item, index) => (
                <div key={index} className="forecast-item">
                  <p>{new Date(item.dt * 1000).toLocaleDateString()}</p>
                  <p>{Math.round(item.main.temp)}°C</p>
                  <p>{item.weather[0].description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
      <footer className="app-footer">
        <p>Weather data provided by OpenWeatherMap</p>
      </footer>
    </div>
  );
};

export default App;
```

### Notes:
- Make sure to replace `'YOUR_API_KEY'` with your actual OpenWeatherMap API key.
- The code uses modern React hooks (`useState`, `useEffect`) for state management.
- Basic styling is referenced from an external CSS file (`App.css`), which you should create for styling purposes.
- Component structure is organized for clarity, with separate sections for the header, main content, and footer.
- The design is responsive by default, but additional CSS may be needed for further enhancements.