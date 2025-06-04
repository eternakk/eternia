import React, {createContext, useContext, useReducer, ReactNode, useEffect, useRef} from 'react';
import { getState, State } from '../api';
import { useErrorHandler } from '../utils/errorHandling';

// Define the shape of our application state
export interface AppState {
  worldState: State | null;
  isLoading: boolean;
  error: Error | null;
  lastUpdated: number | null;
}

// Define the initial state
const initialState: AppState = {
  worldState: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

// Define action types
type ActionType =
  | { type: 'FETCH_STATE_START' }
  | { type: 'FETCH_STATE_SUCCESS'; payload: State }
  | { type: 'FETCH_STATE_ERROR'; payload: Error }
  | { type: 'SET_LOADING'; payload: boolean };

// Create the reducer function
const appStateReducer = (state: AppState, action: ActionType): AppState => {
  switch (action.type) {
    case 'FETCH_STATE_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'FETCH_STATE_SUCCESS':
      return {
        ...state,
        worldState: action.payload,
        isLoading: false,
        error: null,
        lastUpdated: Date.now(),
      };
    case 'FETCH_STATE_ERROR':
      return {
        ...state,
        isLoading: false,
        error: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

// Create the context
interface AppStateContextType {
  state: AppState;
  dispatch: React.Dispatch<ActionType>;
  refreshState: () => Promise<void>;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

// Create a provider component
interface AppStateProviderProps {
  children: ReactNode;
  refreshInterval?: number;
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({
  children,
  refreshInterval = 1000,
}) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState);
  const { handleApiError } = useErrorHandler();

  // Keep track of the previous state to avoid unnecessary updates
  const prevStateRef = useRef<State | null>(null);

  const refreshState = async () => {
    dispatch({ type: 'FETCH_STATE_START' });
    try {
      const data = await getState();
      if (data) {
        // Check if the state has actually changed
        if (!prevStateRef.current || 
            JSON.stringify(data) !== JSON.stringify(prevStateRef.current)) {
          console.log("AppStateContext: State has changed, updating...");
          prevStateRef.current = data;
          dispatch({ type: 'FETCH_STATE_SUCCESS', payload: data });
        } else {
          // State hasn't changed, just update the loading state
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } else {
        throw new Error('Failed to fetch state data');
      }
    } catch (error) {
      handleApiError(error, 'Failed to fetch world state');
      dispatch({ type: 'FETCH_STATE_ERROR', payload: error as Error });
    }
  };

  // Set up polling for state updates
  useEffect(() => {
    refreshState();

    const intervalId = setInterval(() => {
      refreshState();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [refreshInterval]);

  return (
    <AppStateContext.Provider value={{ state, dispatch, refreshState }}>
      {children}
    </AppStateContext.Provider>
  );
};

// Create a hook to use the app state context
export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};
