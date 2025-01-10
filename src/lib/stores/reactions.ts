import { writable, derived } from 'svelte/store';
import type { Reaction } from '$lib/types';

function createReactionsStore() {
    const { subscribe, update, set } = writable<{ [messageId: string]: Reaction[] }>({});

    return {
        subscribe,
        
        // Initialize reactions for a message
        setMessageReactions: (messageId: string, reactions: Reaction[]) => {
            update(store => ({
                ...store,
                [messageId]: reactions
            }));
        },

        // Update a single reaction
        updateReaction: (messageId: string, reaction: Reaction) => {
            update(store => {
                const messageReactions = store[messageId] || [];
                const existingIndex = messageReactions.findIndex(r => r.emoji === reaction.emoji);

                if (existingIndex >= 0) {
                    // Update existing reaction
                    messageReactions[existingIndex] = reaction;
                } else {
                    // Add new reaction
                    messageReactions.push(reaction);
                }

                return {
                    ...store,
                    [messageId]: messageReactions
                };
            });
        },

        // Remove a reaction
        removeReaction: (messageId: string, emoji: string) => {
            update(store => {
                const messageReactions = store[messageId] || [];
                const filteredReactions = messageReactions.filter(r => r.emoji !== emoji);
                
                return {
                    ...store,
                    [messageId]: filteredReactions
                };
            });
        },

        // Clear all reactions for a message
        clearMessageReactions: (messageId: string) => {
            update(store => {
                const newStore = { ...store };
                delete newStore[messageId];
                return newStore;
            });
        },

        // Clear all reactions
        clearAll: () => {
            set({});
        }
    };
}

export const reactionsStore = createReactionsStore(); 