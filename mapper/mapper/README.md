# Project Overview

This project is a web application that consists of a FastAPI backend and a React frontend. The backend is responsible for handling API requests and managing data, while the frontend provides a user interface for interacting with the application.

## Project Structure

The project is organized into two main directories: `backend` and `frontend`.

### Backend

- **Directory:** `backend/src`
  - **main.py:** Entry point of the FastAPI application.
  - **config.py:** Configuration settings for the application.
  - **models:** Contains data models for the application.
  - **routes:** Defines API routes and their corresponding handler functions.
  - **schemas:** Contains Pydantic models for data validation and serialization.
  - **utils:** Includes utility functions for the backend.

- **File:** `backend/requirements.txt`
  - Lists the Python dependencies required for the backend application.

- **File:** `backend/README.md`
  - Documentation specific to the backend application, including setup instructions and usage.

### Frontend

- **Directory:** `frontend/src`
  - **components:** Reusable React components.
  - **pages:** Main pages of the React application.
  - **services:** Service files for API calls and business logic.
  - **App.tsx:** Main component of the React application.
  - **index.tsx:** Entry point for the React application.

- **Directory:** `frontend/public`
  - Contains static assets like images and the HTML file.

- **File:** `frontend/package.json`
  - Configuration file for npm, listing dependencies and scripts.

- **File:** `frontend/tsconfig.json`
  - Configuration file for TypeScript.

- **File:** `frontend/README.md`
  - Documentation specific to the frontend application, including setup instructions and usage.

## Getting Started

To get started with the project, follow these steps:

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd mapper
   ```

2. **Set up the backend:**
   - Navigate to the `backend` directory.
   - Install the required Python packages:
     ```
     pip install -r requirements.txt
     ```
   - Run the FastAPI application:
     ```
     uvicorn src.main:app --reload
     ```

3. **Set up the frontend:**
   - Navigate to the `frontend` directory.
   - Install the required npm packages:
     ```
     npm install
     ```
   - Start the React application:
     ```
     npm start
     ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.