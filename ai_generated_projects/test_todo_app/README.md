# test_todo_app

## Project Description

test_todo_app is a simple todo list application that allows users to create, complete, and delete tasks. It is built using a modern tech stack consisting of React for the frontend and Node.js for the ai_core. This app aims to provide a straightforward interface for managing daily tasks, enhancing productivity and organization.

## Tech Stack

- **Frontend**: React
- **Backend**: Node.js

## Features

- **Task Creation**: Users can add new tasks to their todo list.
- **Task Completion**: Users can mark tasks as completed.
- **Task Deletion**: Users can remove tasks from their list.

## Installation Instructions

To set up the project locally, follow these steps:

### Prerequisites

Ensure you have the following installed:

- Node.js (v14 or higher)
- npm (Node package manager)

### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/test_todo_app.git
   cd test_todo_app
   ```

2. **Install backend dependencies**:

   Navigate to the ai_core directory and install the necessary packages.

   ```bash
   cd backend
   npm install
   ```

3. **Install frontend dependencies**:

   Navigate to the frontend directory and install the necessary packages.

   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up the backend**:

   - Create a `.env` file in the `backend` directory and add your environment variables (if any).
   - You may also need to set up a database (MongoDB, PostgreSQL, etc.) and configure the connection.

5. **Run the backend server**:

   ```bash
   cd ../backend
   npm start
   ```

6. **Run the frontend app**:

   Open another terminal and run:

   ```bash
   cd ../frontend
   npm start
   ```

   The frontend should now be running at `http://localhost:3000`.

## Usage Examples

Once the application is running, you can interact with it as follows:

1. **Creating a Task**: Enter a task in the input field and click the "Add" button.
2. **Completing a Task**: Click the checkbox next to a task to mark it as completed.
3. **Deleting a Task**: Click the "Delete" button next to a task to remove it from the list.

## API Documentation

The backend provides a RESTful API for managing tasks. Below are the available endpoints:

### Endpoints

- **GET /api/tasks**
  - Retrieves all tasks.
  - **Response**: A JSON array of task objects.

- **POST /api/tasks**
  - Creates a new task.
  - **Request Body**: 
    ```json
    {
      "title": "Task Title",
      "completed": false
    }
    ```
  - **Response**: The created task object.

- **PUT /api/tasks/:id**
  - Updates an existing task.
  - **Request Body**: 
    ```json
    {
      "title": "Updated Task Title",
      "completed": true // or false
    }
    ```
  - **Response**: The updated task object.

- **DELETE /api/tasks/:id**
  - Deletes a specific task.
  - **Response**: A success message or confirmation.

## Contributing Guidelines

We welcome contributions to improve the test_todo_app! Please follow these guidelines:

1. **Fork the repository**.
2. **Create a new branch**: 
   ```bash
   git checkout -b feature/YourFeature
   ```
3. **Make your changes** and commit:
   ```bash
   git commit -m "Add your message here"
   ```
4. **Push to your branch**:
   ```bash
   git push origin feature/YourFeature
   ```
5. **Create a Pull Request** with a clear description of your changes.

## License Information

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

---

Thank you for checking out test_todo_app! We hope you find it useful. If you have any questions or feedback, please feel free to reach out. Happy coding!