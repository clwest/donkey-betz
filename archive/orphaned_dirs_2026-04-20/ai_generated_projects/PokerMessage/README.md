# Poker Message

## Project Description

Poker Message is a poker game tracking application designed for poker players to help them track their games, analyze their performance, and improve their strategies. The application allows users to log their games, view statistics, and gain insights into their playing styles. Built using a modern tech stack, Poker Message aims to provide a seamless experience for users looking to enhance their poker skills.

### Target Audience
- Poker players of all skill levels
- Poker enthusiasts looking to track their game history
- Players seeking to analyze and improve their strategies

### Budget
- $2500

### Timeline
- 2 weeks

## Tech Stack
- **Frontend:** React
- **Backend:** Node.js
- **Database:** PostgreSQL

## Features
- User authentication and account management
- Game logging with detailed statistics
- Performance analysis and insights
- Responsive design for mobile and desktop use
- Data visualization of game statistics

## Installation Instructions

To get started with Poker Message, follow these installation instructions:

### Prerequisites
- Node.js (v14 or higher)
- PostgreSQL (v12 or higher)
- Git (for version control)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/poker-message.git
   cd poker-message
   ```

2. **Setup the backend:**
   - Navigate to the ai_core directory:
     ```bash
     cd backend
     ```
   - Install dependencies:
     ```bash
     npm install
     ```
   - Create a `.env` file and configure your database connection:
     ```
     DATABASE_URL=postgres://username:password@localhost:5432/poker_message
     ```
   - Run database migrations:
     ```bash
     npx sequelize-cli db:migrate
     ```
   - Start the backend server:
     ```bash
     npm start
     ```

3. **Setup the frontend:**
   - Navigate to the frontend directory:
     ```bash
     cd ../frontend
     ```
   - Install dependencies:
     ```bash
     npm install
     ```
   - Start the frontend development server:
     ```bash
     npm start
     ```

Your application should now be running on `http://localhost:3000`.

## Usage Examples

1. **Logging a Game:**
   - Navigate to the game logging page.
   - Enter the details of the game including date, opponents, and results.
   - Click on "Save" to store the game information.

2. **Viewing Statistics:**
   - Navigate to the statistics page.
   - Select the desired date range and game type to view your performance metrics.

3. **Analyzing Performance:**
   - Access the performance analysis section to view graphs and insights on your playing style and results over time.

## API Documentation

### Authentication
- **POST /api/auth/login**
  - Login to your account.

- **POST /api/auth/register**
  - Create a new user account.

### Game Management
- **POST /api/games**
  - Create a new game entry.
  - **Request Body:**
    ```json
    {
      "date": "YYYY-MM-DD",
      "opponents": ["Opponent1", "Opponent2"],
      "result": "Win/Loss/Draw",
      "notes": "Any additional notes"
    }
    ```

- **GET /api/games**
  - Retrieve a list of all logged games.

- **GET /api/games/:id**
  - Retrieve a single game entry by ID.

### Statistics
- **GET /api/stats**
  - Get aggregated statistics for games logged.

## Contributing Guidelines

We welcome contributions to Poker Message! Here’s how you can help:

1. **Fork the repository.**
2. **Create a new branch:**
   ```bash
   git checkout -b feature/YourFeature
   ```
3. **Make your changes and commit:**
   ```bash
   git commit -m "Add some feature"
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature/YourFeature
   ```
5. **Submit a pull request.**

Please ensure your code adheres to the existing style and is well-tested.

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Thank you for checking out Poker Message! We hope you find it helpful in your poker journey. For any questions or feedback, please open an issue on GitHub. Happy playing!