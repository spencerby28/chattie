import { writable, derived } from 'svelte/store';
import type { Reaction } from '$lib/types';

interface StandardizedReaction {
    emoji: string;
    userIds: string[];
    reactionIds: { [userId: string]: string };  // Map of user IDs to their reaction document IDs
}

// Helper to transform raw reaction to standardized format
function standardizeReaction(reaction: any): StandardizedReaction {
    console.log('Standardizing reaction:', reaction);
    
    // If it's a raw Appwrite document
    if (reaction.$id && reaction.user_id) {
        return {
            emoji: reaction.emoji,
            userIds: [reaction.user_id],
            reactionIds: { [reaction.user_id]: reaction.$id }
        };
    }

    console.error('Unknown reaction format:', reaction);
    throw new Error('Invalid reaction format');
}

// Helper to merge reactions with same emoji
function mergeReactions(reactions: any[]): StandardizedReaction[] {
    const merged = new Map<string, StandardizedReaction>();
    
    reactions.forEach(reaction => {
        const standardized = standardizeReaction(reaction);
        const key = standardized.emoji;
        const existing = merged.get(key);
        
        if (existing) {
            // Merge userIds and reactionIds
            existing.userIds = [...new Set([...existing.userIds, ...standardized.userIds])];
            existing.reactionIds = { ...existing.reactionIds, ...standardized.reactionIds };
        } else {
            merged.set(key, standardized);
        }
    });
    
    return Array.from(merged.values());
}

function createReactionsStore() {
    const { subscribe, update, set } = writable<{ [messageId: string]: StandardizedReaction[] }>({});

    return {
        subscribe,
        
        // Initialize reactions for a message
        setMessageReactions: (messageId: string, reactions: any[]) => {
            console.log('Setting reactions for message:', messageId, reactions);
            const standardized = mergeReactions(reactions);
            console.log('Standardized reactions:', standardized);
            
            update(store => ({
                ...store,
                [messageId]: standardized
            }));
        },

        // Update a single reaction
        updateReaction: (messageId: string, reaction: any) => {
            console.log('Updating reaction:', messageId, reaction);
            update(store => {
                const messageReactions = store[messageId] || [];
                const standardized = standardizeReaction(reaction);
                
                const existingIndex = messageReactions.findIndex(r => r.emoji === standardized.emoji);
                if (existingIndex >= 0) {
                    // Merge userIds and reactionIds for existing reaction
                    messageReactions[existingIndex].userIds = [
                        ...new Set([...messageReactions[existingIndex].userIds, ...standardized.userIds])
                    ];
                    messageReactions[existingIndex].reactionIds = {
                        ...messageReactions[existingIndex].reactionIds,
                        ...standardized.reactionIds
                    };
                } else {
                    // Add new reaction
                    messageReactions.push(standardized);
                }

                return {
                    ...store,
                    [messageId]: messageReactions
                };
            });
        },

        // Remove a reaction
        removeReaction: (messageId: string, emoji: string, userId?: string) => {
            console.log('Removing reaction:', messageId, emoji, userId);
            update(store => {
                const messageReactions = store[messageId] || [];
                if (userId) {
                    // Find the specific reaction
                    const reaction = messageReactions.find(r => r.emoji === emoji);
                    if (reaction) {
                        // Remove this user's ID from the reaction
                        reaction.userIds = reaction.userIds.filter(id => id !== userId);
                        // Remove the reaction ID for this user
                        delete reaction.reactionIds[userId];
                        
                        // If no users left for this emoji, remove the reaction entirely
                        return {
                            ...store,
                            [messageId]: messageReactions.filter(r => r.userIds.length > 0)
                        };
                    }
                    return store; // No matching reaction found
                }
                
                // If no userId specified, remove all reactions with this emoji
                return {
                    ...store,
                    [messageId]: messageReactions.filter(r => r.emoji !== emoji)
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