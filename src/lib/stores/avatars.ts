import { writable, get } from 'svelte/store';
import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { ImageGravity, ImageFormat } from 'appwrite';

type AvatarCache = {
    [avatarId: string]: {
        url: string;
        timestamp: number;
    };
};

function createAvatarStore() {
    const store = writable<AvatarCache>({});
    const CACHE_DURATION = 1000 * 60 * 30; // 30 minutes

    const generateUrl = (avatarId: string): string => {
        const { storage } = createBrowserClient();
        return storage.getFileView(
            'avatars',
            avatarId,
        );
    };

    return {
        subscribe: store.subscribe,
        
        prewarm: (avatarIds: (string | null)[]) => {
            const now = Date.now();
            const validIds = avatarIds.filter((id): id is string => !!id);
            
            store.update(cache => {
                const updates: AvatarCache = {};
                
                validIds.forEach(id => {
                    if (cache[id] && (now - cache[id].timestamp) < CACHE_DURATION) {
                        updates[id] = cache[id];
                        return;
                    }
                    
                    updates[id] = {
                        url: generateUrl(id),
                        timestamp: now
                    };
                });
                
                return { ...cache, ...updates };
            });
        },

        getAvatarUrl: (avatarId: string | null): string | null => {
            if (!avatarId) return null;
            
            const cache = get(store);
            const now = Date.now();
            
            if (cache[avatarId] && (now - cache[avatarId].timestamp) < CACHE_DURATION) {
                return cache[avatarId].url;
            }
            
            const url = generateUrl(avatarId);
            store.update(cache => ({
                ...cache,
                [avatarId]: { url, timestamp: now }
            }));
            
            return url;
        }
    };
}

export const avatarStore = createAvatarStore(); 