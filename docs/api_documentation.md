# Eternia API Documentation

This document provides comprehensive documentation for the Eternia API, which enables communication between the backend simulation and frontend interfaces.

## Authentication

The API supports two authentication methods:

1. **Legacy Token Authentication**: Using a development token for backward compatibility
2. **JWT-based Authentication**: Modern authentication with role-based permissions

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

### Permissions

JWT-based authentication supports the following permissions:

- `READ`: Access to read-only endpoints
- `WRITE`: Ability to modify the simulation state
- `EXECUTE`: Ability to control the simulation (pause, resume, rollback)
- `ADMIN`: Administrative privileges (e.g., modifying laws)

## API Endpoints

### State Management

#### Get Current State

```
GET /state
```

Retrieves the current state of the simulation.

**Rate Limit**: 120 requests per minute

**Response**:
```json
{
  "cycle": 1234,
  "identity_score": 0.95,
  "emotion": "joy",
  "modifiers": {
    "companion_name": ["blessed", "enlightened"]
  },
  "current_zone": "forest_clearing"
}
```

#### Send Reward to Companion

```
POST /reward/{companion_name}
```

Sends a reward to a specific companion.

**Rate Limit**: 30 requests per minute

**Required Permission**: `WRITE`

**Path Parameters**:
- `companion_name`: Name of the companion to reward

**Request Body**:
```json
{
  "value": 1.0
}
```

**Response**:
```json
{
  "ok": true
}
```

### Command Execution

#### Execute Command

```
POST /command/{action}
```

Executes a command on the system.

**Rate Limit**: 20 requests per minute

**Required Permission**: `EXECUTE`

**Path Parameters**:
- `action`: The action to perform (pause, resume, shutdown)

**Response**:
```json
{
  "status": "paused",
  "detail": null
}
```

#### Rollback System State

```
POST /command/rollback
```

Rolls back the system state to a previous checkpoint.

**Rate Limit**: 10 requests per minute

**Required Permission**: `EXECUTE`

**Query Parameters**:
- `file` (optional): The checkpoint file to roll back to

**Response**:
```json
{
  "status": "rolled_back",
  "detail": "checkpoint_2023-06-15.json"
}
```

### Logging

#### Stream Logs

```
GET /log/stream
```

Streams log entries in real-time using Server-Sent Events (SSE).

**Rate Limit**: 30 requests per minute

**Response**: Server-sent events stream of log entries

### Checkpoints

#### List Checkpoints

```
GET /checkpoints
```

Lists the most recent checkpoints.

**Rate Limit**: 30 requests per minute

**Response**: Array of checkpoint filenames
```json
[
  "checkpoint_2023-06-15_12-30-00.json",
  "checkpoint_2023-06-15_12-00-00.json"
]
```

### Laws

#### List Laws

```
GET /laws
```

Lists all laws in the system.

**Rate Limit**: 30 requests per minute

**Response**: Dictionary of laws with their details
```json
{
  "law_name": {
    "name": "law_name",
    "description": "Description of the law",
    "enabled": true,
    "severity": "high"
  }
}
```

#### Toggle Law

```
POST /laws/{name}/toggle
```

Toggles a law on or off.

**Rate Limit**: 20 requests per minute

**Required Permission**: `ADMIN`

**Path Parameters**:
- `name`: The name of the law to toggle

**Request Body**:
```json
{
  "enabled": true
}
```

**Response**:
```json
{
  "enabled": true
}
```

### Agents

#### List Agents

```
GET /api/agents
```

Lists all agents in the system.

**Rate Limit**: 60 requests per minute

**Response**: Array of agent objects
```json
[
  {
    "name": "agent_name",
    "role": "explorer",
    "emotion": "happy",
    "zone": "forest_clearing",
    "memory": "..."
  }
]
```

#### Get Agent Details

```
GET /api/agent/{name}
```

Gets details of a specific agent.

**Rate Limit**: 60 requests per minute

**Path Parameters**:
- `name`: The name of the agent

**Response**: Agent object with detailed information
```json
{
  "name": "agent_name",
  "role": "explorer",
  "emotion": "happy",
  "zone": "forest_clearing",
  "memory": "...",
  "history": [...]
}
```

### Zones

#### List Zones

```
GET /api/zones
```

Lists all zones in the system.

**Rate Limit**: 60 requests per minute

**Response**: Array of zone objects
```json
[
  {
    "id": 0,
    "name": "forest_clearing",
    "origin": "natural",
    "complexity": 3,
    "explored": true,
    "emotion": "awe",
    "modifiers": ["blessed"]
  }
]
```

#### Get Zone Assets

```
GET /zone/assets
```

Gets assets for a specific zone.

**Rate Limit**: 60 requests per minute

**Query Parameters**:
- `name`: The name of the zone

**Response**: Zone assets object
```json
{
  "background": "forest_bg.png",
  "objects": [
    {
      "name": "tree",
      "image": "tree.png",
      "position": [100, 200]
    }
  ]
}
```

### Rituals

#### List Rituals

```
GET /api/rituals
```

Lists all rituals in the system.

**Rate Limit**: 60 requests per minute

**Response**: Array of ritual objects
```json
[
  {
    "id": 0,
    "name": "ritual_name",
    "purpose": "healing",
    "steps": ["step1", "step2"],
    "symbolic_elements": ["water", "fire"]
  }
]
```

#### Trigger Ritual

```
POST /api/rituals/trigger/{id}
```

Triggers a ritual by its ID.

**Rate Limit**: 20 requests per minute

**Path Parameters**:
- `id`: The ID of the ritual to trigger

**Response**:
```json
{
  "status": "success",
  "message": "Ritual 'ritual_name' triggered"
}
```

## WebSocket API

### Connect to WebSocket

```
WebSocket: /ws
```

Establishes a WebSocket connection for real-time event streaming.

**Authentication**: Send a JSON message with the token after connecting:
```json
{
  "token": "your_token"
}
```

**Events**: The server will send JSON events with the following structure:
```json
{
  "event": "event_type",
  "data": {},
  "t": 1623765432.123
}
```

Common event types include:
- `connected`: Connection established
- `state_change`: Simulation state has changed
- `agent_update`: Agent state has changed
- `zone_update`: Zone state has changed
- `ritual_performed`: A ritual has been performed

## Error Handling

All API endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error responses include a JSON body with details:
```json
{
  "detail": "Error message"
}
```

## Rate Limiting

All endpoints have rate limits to prevent abuse. When a rate limit is exceeded, the server returns a `429 Too Many Requests` status code with a `Retry-After` header indicating when the client can retry.