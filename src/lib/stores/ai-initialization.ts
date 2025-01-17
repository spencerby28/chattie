// src/lib/stores/ai-initialization.ts
import { writable } from 'svelte/store';

interface AIInitState {
  isInitializing: boolean;
  currentStep: string;
}

const createAIInitStore = () => {
  const { subscribe, set } = writable<AIInitState>({
    isInitializing: false,
    currentStep: ''
  });

  return {
    subscribe,
    startInitialization: () => {
      set({ 
        isInitializing: true, 
        currentStep: "Creating AI workspace... This may take up to a minute."
      });
    },
    complete: () => {
      set({ 
        isInitializing: false, 
        currentStep: ''
      });
    },
    reset: () => {
      set({ 
        isInitializing: false, 
        currentStep: ''
      });
    }
  };
};

export const aiInitStore = createAIInitStore();