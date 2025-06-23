# VectorShift Integrations System

This project is a web application that allows users to connect to various third-party services (Airtable, Notion, HubSpot) and view their data. It consists of a React frontend and a Python (FastAPI) backend.

## Project Structure

- `frontend/`: Contains the React application.
- `backend/`: Contains the FastAPI application.
- `redis.conf`: Configuration file for Redis.
- `dump.rdb`: Redis database dump file.

## Features

- **Integration with Third-Party Services**: The application supports integrations with Airtable, Notion, and HubSpot.
- **OAuth 2.0 Authorization**: It uses the OAuth 2.0 protocol to securely connect to the third-party services.
- **Data Fetching**: Once authorized, the application can fetch and display data from the integrated services.

## Getting Started

### Prerequisites

- Node.js and npm (for the frontend)
- Python 3 and pip (for the backend)
- Redis

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```

The backend server will be running at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required npm packages:**
    ```bash
    npm install
    ```

3.  **Start the React development server:**
    ```bash
    npm start
    ```

The frontend application will be running at `http://localhost:3000`.

## Environment Variables

To run this project, you will need to add the following environment variables to a `.env` file in the `backend` directory:

`AIRTABLE_CLIENT_ID`
`AIRTABLE_CLIENT_SECRET`
`AIRTABLE_REDIRECT_URI`

`NOTION_CLIENT_ID`
`NOTION_CLIENT_SECRET`
`NOTION_REDIRECT_URI`

`HUBSPOT_CLIENT_ID`
`HUBSPOT_CLIENT_SECRET`
`HUBSPOT_REDIRECT_URI`

You will need to create a developer account with each of these services to get your client ID and secret. The redirect URIs should be `http://localhost:8000/integrations/airtable/oauth2callback`, `http://localhost:8000/integrations/notion/oauth2callback`, and `http://localhost:8000/integrations/hubspot/oauth2callback` respectively.

## How to Use

1.  Open your web browser and navigate to `http://localhost:3000`.
2.  Enter a username and organization name.
3.  Select an integration from the dropdown menu (Airtable, Notion, or HubSpot).
4.  Click the "Authorize" button to initiate the OAuth 2.0 flow.
5.  Follow the on-screen instructions from the third-party service to grant access.
6.  Once authorized, the application will fetch and display your data from the selected service. 
