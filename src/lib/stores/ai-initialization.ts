// src/lib/stores/ai-initialization.ts
import { writable } from 'svelte/store';

interface AIInitState {
  isInitializing: boolean;
  currentStep: string;
  workspaceId: string | null;
  isComplete: boolean;
}

const createAIInitStore = () => {
  const { subscribe, set, update } = writable<AIInitState>({
    isInitializing: false,
    currentStep: '',
    workspaceId: null,
    isComplete: false
  });

  const steps = [
    "Creating workspace...",
    "Generating AI personas...",
    "Creating avatars...",
    "Initializing personalities...",
    "Setting up channels..."
  ];

  let stepInterval: NodeJS.Timeout;

  return {
    subscribe,
    startInitialization: (workspaceId: string) => {
      set({ 
        isInitializing: true, 
        currentStep: steps[0], 
        workspaceId,
        isComplete: false 
      });
      let currentStepIndex = 0;
      
      stepInterval = setInterval(() => {
        currentStepIndex = (currentStepIndex + 1) % steps.length;
        update(state => ({ ...state, currentStep: steps[currentStepIndex] }));
      }, 8000);
    },
    complete: (workspaceId: string) => {
      clearInterval(stepInterval);
      set({ 
        isInitializing: false, 
        currentStep: '', 
        workspaceId, 
        isComplete: true 
      });
    },
    reset: () => {
      clearInterval(stepInterval);
      set({ 
        isInitializing: false, 
        currentStep: '', 
        workspaceId: null, 
        isComplete: false 
      });
    }
  };
};

export const aiInitStore = createAIInitStore();