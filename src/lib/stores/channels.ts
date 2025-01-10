import { writable, derived } from 'svelte/store';
import type { Channel } from '$lib/types';
import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { Query } from 'appwrite';
import { browser } from '$app/environment';

interface ChannelState {
    channels: Channel[];
    loading: boolean;
    currentWorkspaceId: string | null;
    error: string | null;
}

const initialState: ChannelState = {
    channels: [],
    loading: false,
    currentWorkspaceId: null,
    error: null
};

function createChannelStore() {
    const store = writable<ChannelState>(initialState);
    let currentState = initialState;

    // Subscribe to store updates if in browser
    if (browser) {
        store.subscribe(value => {
            currentState = value;
        });
    }

    return {
        subscribe: store.subscribe,
        // Set initial channels
        setChannels: (channels: Channel[]) => {
            store.update(state => ({
                ...state,
                channels,
                loading: false,
                error: null
            }));
        },
        // Add a single channel
        addChannel: (channel: Channel) => {
            store.update(state => {
                const exists = state.channels.some(c => c.$id === channel.$id);
                if (!exists) {
                    return { ...state, channels: [...state.channels, channel] };
                }
                return state;
            });
        },
        // Update a channel
        updateChannel: (channelId: string, updatedChannel: Channel) => {
            store.update(state => ({
                ...state,
                channels: state.channels.map(channel => 
                    channel.$id === channelId ? { ...channel, ...updatedChannel } : channel
                )
            }));
        },
        // Delete a channel
        deleteChannel: (channelId: string) => {
            store.update(state => ({
                ...state,
                channels: state.channels.filter(channel => channel.$id !== channelId)
            }));
        },
        // Initialize store with workspace channels
        async initializeForWorkspace(workspaceId: string) {
            // Skip if not in browser
            if (!browser) return;
            
            // Skip if already initialized for this workspace
            if (workspaceId === currentState.currentWorkspaceId) {
                return;
            }

            store.update(state => ({ ...state, loading: true, error: null }));
            
            try {
                const { databases } = createBrowserClient();
                const response = await databases.listDocuments(
                    'main',
                    'channels',
                    [
                        Query.equal('workspace_id', workspaceId)
                    ]
                );
                const channels = response.documents as Channel[];
                store.update(() => ({
                    channels: channels.filter(channel => channel.workspace_id === workspaceId),
                    loading: false,
                    currentWorkspaceId: workspaceId,
                    error: null
                }));
            } catch (error) {
                console.error('[ChannelStore] Failed to initialize channels:', error);
                store.update(() => ({
                    channels: [],
                    loading: false,
                    currentWorkspaceId: workspaceId,
                    error: 'Failed to load channels'
                }));
            }
        },
        // Reset store
        reset: () => store.set(initialState)
    };
}

export const channelStore = createChannelStore();

// Derived stores for different channel types
export const publicChannels = derived(channelStore, $store => 
    $store.channels.filter(channel => channel.type === 'public')
);

export const privateChannels = derived(channelStore, $store => 
    $store.channels.filter(channel => channel.type === 'private')
);

export const directMessageChannels = derived(channelStore, $store => 
    $store.channels.filter(channel => channel.type === 'dm')
);

// Derived store for loading state
export const channelsLoading = derived(channelStore, $store => $store.loading); 