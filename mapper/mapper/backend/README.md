# FastAPI and React Application

This project is a web application that consists of a FastAPI backend and a React frontend. Below are the details for setting up and running both parts of the application.

## Backend (FastAPI)

### Directory Structure
- `src/`: Contains the source code for the FastAPI application.
  - `main.py`: Entry point of the FastAPI application.
  - `config.py`: Configuration settings for the application.
  - `models/`: Contains data models for the application.
  - `routes/`: Defines the API routes.
  - `schemas/`: Contains Pydantic models for data validation and serialization.
  - `utils/`: Utility functions for the application.

### Setup Instructions
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the FastAPI application:
   ```bash
   uvicorn src.main:app --reload
   ```

### Usage
Once the backend is running, you can access the API documentation at `http://localhost:8000/docs`.

## Frontend (React)

### Directory Structure
- `src/`: Contains the source code for the React application.
  - `components/`: Reusable React components.
  - `pages/`: Main pages of the application.
  - `services/`: Service files for API calls.
  - `App.tsx`: Main component of the React application.
  - `index.tsx`: Entry point for the React application.

### Setup Instructions
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install the required dependencies:
   ```bash
   npm install
   ```

3. Start the React application:
   ```bash
   npm start
   ```

### Usage
Once the frontend is running, you can access the application at `http://localhost:3000`.

## Project Overview
This project combines a FastAPI backend with a React frontend, providing a full-stack web application. The backend handles API requests and data management, while the frontend provides a user interface for interaction.