import { writable } from 'svelte/store';
import { toast } from 'svelte-sonner';
import { browser } from '$app/environment';

// Load initial state from localStorage
const storedFeatures = browser ? 
    new Set(JSON.parse(localStorage.getItem('seen_features') || '[]')) : 
    new Set<string>();

// Store to track which features have been announced
const seenFeatures = writable<Set<string>>(storedFeatures);

// Subscribe to changes and update localStorage
if (browser) {
    seenFeatures.subscribe(features => {
        localStorage.setItem('seen_features', JSON.stringify([...features]));
    });
}

// Helper function to show a feature announcement toast
export function announceFeature(featureName: string, description?: string) {
    seenFeatures.update(features => {
        // If feature has already been announced, don't show again
        if (features.has(featureName)) {
            return features;
        }

        // Show the feature announcement toast
        toast(`✨ New Feature: ${featureName}`, {
            description: description || 'Check out this new feature we just added!',
            duration: 6000,
        });

        // Mark feature as seen
        features.add(featureName);
        return features;
    });
}

// Export the store for persistence if needed
export { seenFeatures }; 