# Running the Eternia Server and UI

This document provides instructions on how to run the Eternia server and UI components.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Running the API Server

The Eternia API server provides the backend functionality for the UI. To start the server:

1. Make sure you're in the root directory of the project.
2. Run the following command:

```bash
./run_api.py
```

This will start the server on http://0.0.0.0:8000. The server provides API endpoints for the UI to interact with the Eternia simulation.

## Running the UI

The UI is a React application that provides a visual interface for interacting with the Eternia simulation. To start the UI:

1. Navigate to the ui directory:

```bash
cd ui
```

2. Install dependencies (if you haven't already):

```bash
npm install
# or
yarn
```

3. Start the development server:

```bash
npm run dev
# or
yarn dev
```

This will start the UI development server on http://localhost:5173.

### UI Environment Variables

The UI can be configured using environment variables. Create a `.env` file in the `ui` directory with the following variables:

```
# API Configuration
VITE_API_URL=http://localhost:8000  # URL of the API server
VITE_API_TIMEOUT=30000              # API request timeout in milliseconds

# Feature Flags
VITE_ENABLE_EXPERIMENTAL=false      # Enable experimental features
VITE_ENABLE_DEBUG_TOOLS=false       # Enable debug tools

# UI Configuration
VITE_DEFAULT_THEME=dark             # Default theme (light or dark)
VITE_AUTO_REFRESH_INTERVAL=5000     # Auto-refresh interval in milliseconds
```

You can also set these variables in your environment or in a `.env.local` file for local development.

## Accessing the UI

Once both the API server and UI are running, you can access the UI by opening http://localhost:5173 in your web browser.

## Troubleshooting

If you encounter any issues:

1. Make sure both the API server and UI are running.
2. Check the console output for any error messages.
3. If you see "connection refused" errors, make sure the API server is running on port 8000.
4. If the UI is not showing the list of files for rollback cycles, make sure the API server is running and accessible.

### Common UI Issues

#### UI Not Loading
- Check if the Vite development server is running (look for "Local: http://localhost:5173/" in the console)
- Clear your browser cache and reload the page
- Try a different browser to rule out browser-specific issues
- Check for JavaScript errors in the browser console (F12 or right-click > Inspect > Console)

#### UI Loading but Not Connecting to API
- Verify the API server is running on the correct port
- Check the VITE_API_URL environment variable in your .env file
- Look for CORS errors in the browser console (may need to enable CORS on the API server)
- Try accessing the API directly in the browser to verify it's responding

#### UI Components Not Rendering Correctly
- Check for React error boundaries in the console
- Verify that you're using a supported browser version
- Check if your CSS is loading correctly
- Try disabling browser extensions that might interfere with React

#### Performance Issues
- Check the browser's performance tab for bottlenecks
- Reduce the auto-refresh interval in the environment variables
- Close other resource-intensive applications
- If using the ZoneCanvas component with large zones, try reducing the zone size or detail level
