# UI Components Documentation

This document provides detailed information about the UI components used in the Eternia project.

## Overview

The Eternia UI is built using React and TypeScript, with Tailwind CSS for styling. The UI components are organized in a modular way to promote reusability and maintainability.

## Component List

The following components are available in the Eternia UI:

### AgentDashboard

**Purpose**: Displays information about agents in the simulation.

**Props**:
- `agents`: Array of agent objects
- `onSelectAgent`: Callback function when an agent is selected

**Usage Example**:
```tsx
<AgentDashboard 
  agents={agentList} 
  onSelectAgent={handleAgentSelect} 
/>
```

### CheckPointPanel

**Purpose**: Allows users to manage simulation checkpoints.

**Props**:
- `checkpoints`: Array of checkpoint objects
- `onLoadCheckpoint`: Callback function when a checkpoint is loaded
- `onSaveCheckpoint`: Callback function when a checkpoint is saved
- `onDeleteCheckpoint`: Callback function when a checkpoint is deleted

**Usage Example**:
```tsx
<CheckPointPanel 
  checkpoints={checkpointList} 
  onLoadCheckpoint={handleLoadCheckpoint}
  onSaveCheckpoint={handleSaveCheckpoint}
  onDeleteCheckpoint={handleDeleteCheckpoint}
/>
```

### ControlPanel

**Purpose**: Provides controls for managing the simulation.

**Props**:
- `isRunning`: Boolean indicating if the simulation is running
- `onStart`: Callback function to start the simulation
- `onPause`: Callback function to pause the simulation
- `onReset`: Callback function to reset the simulation
- `simulationSpeed`: Number indicating the simulation speed
- `onSpeedChange`: Callback function when the simulation speed changes

**Usage Example**:
```tsx
<ControlPanel 
  isRunning={simulationRunning}
  onStart={handleStart}
  onPause={handlePause}
  onReset={handleReset}
  simulationSpeed={speed}
  onSpeedChange={handleSpeedChange}
/>
```

### GlobalLoadingIndicator

**Purpose**: Displays a global loading indicator when the application is performing operations.

**Props**:
- `isLoading`: Boolean indicating if the application is loading

**Usage Example**:
```tsx
<GlobalLoadingIndicator isLoading={appIsLoading} />
```

### LoadingIndicator

**Purpose**: A reusable loading indicator component that can be used in different parts of the application.

**Props**:
- `size`: String indicating the size of the indicator ('small', 'medium', 'large')
- `color`: String indicating the color of the indicator
- `message`: Optional string message to display

**Usage Example**:
```tsx
<LoadingIndicator 
  size="medium" 
  color="blue" 
  message="Loading data..." 
/>
```

### LogConsole

**Purpose**: Displays log messages from the simulation.

**Props**:
- `logs`: Array of log message objects
- `onClear`: Callback function to clear the logs
- `maxEntries`: Maximum number of log entries to display

**Usage Example**:
```tsx
<LogConsole 
  logs={logMessages} 
  onClear={handleClearLogs}
  maxEntries={100}
/>
```

### NotificationContainer

**Purpose**: Displays notification messages to the user.

**Props**:
- `notifications`: Array of notification objects
- `onDismiss`: Callback function when a notification is dismissed

**Usage Example**:
```tsx
<NotificationContainer 
  notifications={notificationList} 
  onDismiss={handleDismissNotification} 
/>
```

### RitualPanel

**Purpose**: Allows users to manage and execute rituals in the simulation.

**Props**:
- `rituals`: Array of ritual objects
- `onExecuteRitual`: Callback function when a ritual is executed
- `selectedAgent`: The currently selected agent

**Usage Example**:
```tsx
<RitualPanel 
  rituals={ritualList} 
  onExecuteRitual={handleExecuteRitual}
  selectedAgent={currentAgent}
/>
```

### StatePanel

**Purpose**: Displays the current state of the simulation.

**Props**:
- `state`: Object containing the simulation state
- `onStateChange`: Callback function when the state is changed

**Usage Example**:
```tsx
<StatePanel 
  state={simulationState} 
  onStateChange={handleStateChange} 
/>
```

### ZoneCanvas

**Purpose**: Renders the simulation zone as a canvas.

**Props**:
- `zone`: Object containing zone data
- `width`: Number indicating the width of the canvas
- `height`: Number indicating the height of the canvas
- `onEntityClick`: Callback function when an entity is clicked

**Usage Example**:
```tsx
<ZoneCanvas 
  zone={currentZone} 
  width={800}
  height={600}
  onEntityClick={handleEntityClick}
/>
```

### ZoneViewer

**Purpose**: A higher-level component that includes ZoneCanvas and additional controls for viewing zones.

**Props**:
- `zones`: Array of zone objects
- `selectedZoneId`: ID of the currently selected zone
- `onZoneSelect`: Callback function when a zone is selected

**Usage Example**:
```tsx
<ZoneViewer 
  zones={zoneList} 
  selectedZoneId={currentZoneId}
  onZoneSelect={handleZoneSelect}
/>
```

## Component Hierarchy

The components are organized in the following hierarchy:

```
App
├── GlobalLoadingIndicator
├── NotificationContainer
├── ControlPanel
├── ZoneViewer
│   └── ZoneCanvas
├── AgentDashboard
├── StatePanel
├── CheckPointPanel
├── RitualPanel
└── LogConsole
```

## Best Practices

When using these components:

1. Always provide all required props
2. Handle errors gracefully
3. Use TypeScript interfaces for prop types
4. Follow the component hierarchy for proper rendering
5. Use the LoadingIndicator component for asynchronous operations
6. Implement proper error handling with the NotificationContainer

## Styling

All components use Tailwind CSS for styling. Custom styles can be applied by passing className props to the components.