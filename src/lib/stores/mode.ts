import { writable } from 'svelte/store';

type Mode = 'dark' | 'light';

// Initialize from localStorage if available, default to light
const getInitialMode = (): Mode => {
  if (typeof window !== 'undefined') {
    const savedMode = window.localStorage.getItem('theme');
    if (savedMode === 'dark' || savedMode === 'light') {
      return savedMode;
    }
  }
  return 'light';
};

// Create the store
export const mode = writable<Mode>(getInitialMode());

// Subscribe to changes and update localStorage
if (typeof window !== 'undefined') {
  mode.subscribe((value) => {
    window.localStorage.setItem('mode', value);
  });
}
