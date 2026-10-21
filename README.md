# Travel Concierge Agent

![Travel Concierge Demo](demo.gif)

A conversational AI agent built with the Google Agent Development Kit (ADK) that helps travelers plan trips. The agent features a catalog of destinations and activities, and can help you look up live information and manage your trip.

## Features & Capabilities

The following capabilities are fully implemented in this repository:

*   **Database (Firestore)**:
    *   **Hotels Lookup**: Query available accommodations from the `hotels` Firestore collection.
    *   **Save Itinerary**: Finalize and save trip itineraries to the `itineraries` Firestore collection.
*   **Live External APIs**:
    *   **Weather**: Live weather lookups for destinations using `wttr.in`.
    *   **Currency Conversion**: Live exchange rates via the Open Exchange Rates API.
    *   **Destination Guides**: Overview and history information via the Wikipedia API.
*   **Media & Image Generation**:
    *   **Mood Boards**: Generates destination mood boards and images using the `gemini-3.1-flash-lite-image` model.
    *   **Cloud Storage**: Uploads generated images directly to a public Google Cloud Storage bucket (`travel-concierge-assets`) and returns the public URLs.
*   **Code Sandbox**:
    *   Equipped with an `AgentEngineSandboxCodeExecutor` to calculate total budgets, format data, and do dynamic currency calculations in a secure Python sandbox.
*   **Rich UI (A2UI)**:
    *   Enabled via `A2uiSchemaManager` to render structured cards, columns, and images in the user interface rather than returning raw text or JSON.

### Planned (Not Yet Implemented)

The following features were planned in the original project brief but are **not yet implemented**:
*   *Memory / Preferences*: Remembering user preferences across sessions (e.g., window seat preference, dietary restrictions like peanut allergies, budget constraints).
*   *Flight Lookups*: Fetching flight times or displaying flight options.

## Project Structure

*   `app/agent.py`: The core ADK agent implementation containing the system prompt, tool functions, sandbox configuration, and A2UI callback.
*   `app/a2ui_utils.py`: The callback utility that translates the model's A2UI JSON into the format expected by the frontend.
*   `frontend/`: A custom FastAPI proxy and static HTML chat UI that communicates with the deployed A2A agent securely.
*   `agents-cli-manifest.yaml`: Configuration for deploying the agent to Google Cloud Agent Engine.

## Running Locally

### 1. Test the Agent in ADK Web
You can run the agent in the local ADK developer playground to test its logic and rich UI cards (ensure Token Streaming is OFF in the settings gear to see the A2UI cards):

```bash
uv run adk web --port 8081 --allow_origins "*" --reload_agents
```
Then navigate to `http://localhost:8081` in your browser.

### 2. Run the Custom Frontend Proxy
To run the custom "Travel Concierge" branded chat frontend, navigate to the `frontend/` directory and start the `uvicorn` server. You will need to supply your deployed Agent Engine resource name.

```bash
cd frontend

# Set your deployed Agent Engine resource name and directory
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<REGION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"

# Start the proxy server
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```
Then navigate to `http://localhost:8080` in your browser.
