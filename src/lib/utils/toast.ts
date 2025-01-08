import { toast } from 'svelte-sonner';
import { mode } from 'mode-watcher';

export const announceFeature = (name: string) => {
    toast(`✨ New Feature On The Way: ${name}`);
}; 