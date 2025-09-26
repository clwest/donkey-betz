# Poker Message

## Project Description

Poker Message is a poker game tracking application designed for poker players to log and analyze their poker sessions. The app allows users to track their wins, losses, and overall performance statistics over time. With a user-friendly interface, players can easily enter game details, view their progress, and gain insights into their gameplay.

### Target Audience
This application is aimed at poker players of all skill levels who want to keep track of their games, improve their strategies, and analyze their performance.

### Budget
The budget for this project is $2500.

### Timeline
The expected timeline for the completion of this project is 2 weeks.

## Tech Stack
- **Frontend**: React
- **Backend**: Node.js
- **Database**: PostgreSQL

## Features
- User authentication (sign up, login, logout)
- Session tracking (date, game type, buy-in, winnings/losses)
- Performance statistics (graphs and charts)
- Session history and filtering options
- Responsive design for mobile and desktop use

## Installation Instructions

To set up the Poker Message application locally, follow these instructions:

### Prerequisites
- Node.js (version 14 or higher)
- PostgreSQL (version 12 or higher)
- npm (Node Package Manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/poker-message.git
cd poker-message
```

### Step 2: Set Up the Database
1. Create a new PostgreSQL database:
   ```sql
   CREATE DATABASE poker_message;
   ```
2. Run the SQL scripts located in the `db` folder to set up your tables.

### Step 3: Install Backend Dependencies
Navigate to the backend directory and install the necessary packages:
```bash
cd backend
npm install
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the `backend` directory and add the following variables:
```
DATABASE_URL=postgres://username:password@localhost:5432/poker_message
JWT_SECRET=your_jwt_secret_key
```

### Step 5: Start the Backend Server
```bash
npm start
```

### Step 6: Install Frontend Dependencies
Navigate to the frontend directory and install the required packages:
```bash
cd ../frontend
npm install
```

### Step 7: Start the Frontend Server
```bash
npm start
```

Now, you should be able to access the application at `http://localhost:3000`.

## Usage Examples

1. **Register a New User**: 
   - Navigate to the registration page and fill out the form.
  
2. **Log a Poker Session**: 
   - After logging in, go to the "Log Session" page, enter the game details, and submit.

3. **View Statistics**: 
   - Use the "Statistics" section to view performance graphs and insights.

## API Documentation

### Authentication
- **POST /api/auth/register**
  - Request Body: `{ username, password }`
  - Response: `{ message: "User registered successfully" }`

- **POST /api/auth/login**
  - Request Body: `{ username, password }`
  - Response: `{ token: "jwt_token" }`

### Sessions
- **GET /api/sessions**
  - Headers: `Authorization: Bearer <token>`
  - Response: `[{ sessionId, date, gameType, buyIn, winnings, losses }]`

- **POST /api/sessions**
  - Headers: `Authorization: Bearer <token>`
  - Request Body: `{ date, gameType, buyIn, winnings, losses }`
  - Response: `{ message: "Session logged successfully" }`

## Contributing Guidelines

We welcome contributions to the Poker Message project! Here’s how you can help:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear messages.
4. Submit a pull request for review.

Please ensure to follow coding standards and write tests for your contributions.

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Thank you for your interest in Poker Message! We hope you find the application useful for tracking and improving your poker game. If you have any questions or feedback, please reach out!