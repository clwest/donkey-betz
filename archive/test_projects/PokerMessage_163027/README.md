# Poker Message

## Project Description

Poker Message is a poker game tracking application designed for poker players to help them manage and analyze their gameplay. The app allows users to record their poker sessions, track their wins and losses, and gain insights into their performance over time. With an intuitive user interface and robust backend, Poker Message aims to enhance the poker playing experience by providing valuable data at the players' fingertips.

### Target Audience

This application is tailored for poker players of all levels, from recreational players to seasoned professionals, who want a better way to track their poker games and improve their strategies.

### Budget

The estimated budget for the project is **$2500**.

### Timeline

The project is expected to be completed within **2 weeks**.

## Tech Stack

- **Frontend**: React
- **Backend**: Node.js
- **Database**: PostgreSQL

## Features

- User authentication and authorization
- Session tracking (date, game type, buy-in, and results)
- Performance analytics (win rate, average buy-in, etc.)
- Export session data to CSV
- Responsive design for mobile and desktop
- User-friendly dashboard

## Installation Instructions

To set up the Poker Message application locally, follow these steps:

### Prerequisites

- Node.js (>= 14.x)
- PostgreSQL (>= 12.x)
- npm (Node Package Manager)

### Clone the Repository

```bash
git clone https://github.com/yourusername/poker-message.git
cd poker-message
```

### Install Backend Dependencies

Navigate to the ai_core directory and install the necessary packages:

```bash
cd backend
npm install
```

### Set Up the Database

1. Create a PostgreSQL database:
   ```bash
   createdb poker_message_db
   ```

2. Run migrations to set up the database schema:
   ```bash
   npm run migrate
   ```

### Install Frontend Dependencies

Navigate to the frontend directory and install the necessary packages:

```bash
cd ../frontend
npm install
```

### Start the Application

In the ai_core directory, start the server:

```bash
cd ../backend
npm start
```

In a new terminal, navigate to the frontend directory and start the client:

```bash
cd ../frontend
npm start
```

Your application should now be running at `http://localhost:3000`.

## Usage Examples

Once you have the application running, you can:

1. **Create an Account**: Use the signup feature to create a new account.
2. **Log In**: Use your credentials to log in and access your dashboard.
3. **Track a Game**: Navigate to the "Track Game" section to enter details of your poker session.
4. **View Analytics**: Check the "Analytics" section to view your performance over time.

## API Documentation

### Authentication

- **POST /api/auth/signup**
  - Request Body: `{ "username": "string", "password": "string" }`
  - Description: Registers a new user.

- **POST /api/auth/login**
  - Request Body: `{ "username": "string", "password": "string" }`
  - Description: Authenticates the user and returns a token.

### Game Sessions

- **POST /api/sessions**
  - Request Body: `{ "date": "YYYY-MM-DD", "gameType": "string", "buyIn": number, "result": number }`
  - Description: Adds a new game session.

- **GET /api/sessions**
  - Description: Retrieves all game sessions for the authenticated user.

## Contributing Guidelines

We welcome contributions to Poker Message! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear messages.
4. Push your branch to your forked repository.
5. Create a pull request explaining your changes.

Please ensure that your code adheres to the project's style guidelines and passes all tests.

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Thank you for your interest in Poker Message! We hope you find this application helpful in your poker endeavors. If you have any questions or suggestions, feel free to reach out. Happy playing!