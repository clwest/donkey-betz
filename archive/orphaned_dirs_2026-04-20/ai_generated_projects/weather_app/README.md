# Weather App

## Project Description

The Weather App is a simple web application that provides users with up-to-date weather information. It allows users to search for weather data based on location and view a five-day weather forecast. The app is built using a modern tech stack, ensuring a smooth user experience and efficient data handling.

### Tech Stack
- **Frontend:** React
- **Backend:** Node.js
- **Database:** PostgreSQL

## Installation Instructions

To get started with the Weather App, follow the steps below to set up the project on your local machine.

### Prerequisites
- Node.js (v14 or higher)
- PostgreSQL (v12 or higher)
- npm (comes with Node.js)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/weather_app.git
   cd weather_app
   ```

2. **Set up the backend:**
   - Navigate to the ai_core directory:
     ```bash
     cd backend
     ```
   - Install the necessary dependencies:
     ```bash
     npm install
     ```
   - Create a `.env` file in the ai_core directory and configure your PostgreSQL connection settings:
     ```plaintext
     DATABASE_URL=postgres://user:password@localhost:5432/weather_db
     ```
   - Run the migrations to set up the database:
     ```bash
     npm run migrate
     ```
   - Start the backend server:
     ```bash
     npm start
     ```

3. **Set up the frontend:**
   - Open a new terminal and navigate to the frontend directory:
     ```bash
     cd frontend
     ```
   - Install the necessary dependencies:
     ```bash
     npm install
     ```
   - Start the frontend application:
     ```bash
     npm start
     ```

4. **Access the application:**
   - Open your web browser and go to `http://localhost:3000` to view the Weather App.

## Usage Examples

- **Search for weather by location:**
  Enter a city name in the search bar and hit 'Enter' to fetch the current weather for that location.

- **View the forecast:**
  After searching for a location, the app will display the current weather details along with a five-day forecast.

## API Documentation

### Backend API Endpoints

1. **Get Current Weather**
   - **Endpoint:** `GET /api/weather/current`
   - **Query Parameters:**
     - `location`: The name of the city (e.g., `London`).
   - **Response:**
     ```json
     {
       "location": "London",
       "temperature": 20,
       "condition": "Sunny"
     }
     ```

2. **Get Weather Forecast**
   - **Endpoint:** `GET /api/weather/forecast`
   - **Query Parameters:**
     - `location`: The name of the city (e.g., `London`).
   - **Response:**
     ```json
     [
       {
         "date": "2023-10-01",
         "temperature": 19,
         "condition": "Partly Cloudy"
       },
       {
         "date": "2023-10-02",
         "temperature": 21,
         "condition": "Sunny"
       }
       // More days...
     ]
     ```

## Contributing Guidelines

We welcome contributions to the Weather App! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add some feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a Pull Request with a description of your changes.

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Thank you for checking out the Weather App! We hope you find it useful and enjoy using it. If you have any questions or feedback, feel free to reach out!