import { writable, derived } from 'svelte/store';
import type { Message, Reaction } from '$lib/types';

function createMessageStore() {
    const { subscribe, set, update } = writable<Message[]>([]);

    return {
        subscribe,
        set,
        
        // Initialize messages for a workspace with pagination support
        initializeForWorkspace: (messages: Message[], reset: boolean = false) => {
            update(existingMessages => {
                if (reset) {
                    return messages;
                }

                // Create a map of existing messages for quick lookup
                const messageMap = new Map([
                    ...existingMessages.map(m => [m.$id, m]),
                    ...messages.map(m => [m.$id, m])
                ]);
                
                // Convert back to array and sort by creation time
                return Array.from(messageMap.values())
                    .sort((a, b) => new Date(a.$createdAt).getTime() - new Date(b.$createdAt).getTime());
            });
        },
        
        // Add messages from pagination
        addMessages: (messages: Message[]) => {
            update(existingMessages => {
                // Create a map of all messages
                const messageMap = new Map([
                    ...existingMessages.map(m => [m.$id, m]),
                    ...messages.map(m => [m.$id, m])
                ]);
                
                // Convert back to array and sort by creation time
                return Array.from(messageMap.values())
                    .sort((a, b) => new Date(a.$createdAt).getTime() - new Date(b.$createdAt).getTime());
            });
        },
        
        // Add a new message
        addMessage: async (message: Message) => {
            update(messages => {
                // Check if message already exists to prevent duplicates
                if (messages.some(m => m.$id === message.$id)) {
                    return messages;
                }
                return [...messages, message];
            });
        },

        // Update an existing message
        updateMessage: async (messageId: string, updatedMessage: Message) => {
            update(messages => {
                const index = messages.findIndex(m => m.$id === messageId);
                if (index === -1) return messages;
                
                const newMessages = [...messages];
                newMessages[index] = { ...newMessages[index], ...updatedMessage };
                return newMessages;
            });
        },

        // Delete a message
        deleteMessage: async (messageId: string) => {
            update(messages => messages.filter(m => m.$id !== messageId));
        },

        // Add or update a reaction
        updateReaction: (messageId: string, reaction: Reaction) => {
            update(messages => 
                messages.map(msg => {
                    if (msg.$id === messageId) {
                        const reactions = msg.reactions || [];
                        const existingReactionIndex = reactions.findIndex(
                            r => r?.emoji === reaction.emoji && r?.user_id === reaction.user_id
                        );

                        let updatedReactions;
                        if (existingReactionIndex >= 0) {
                            // Update existing reaction
                            updatedReactions = [...reactions];
                            updatedReactions[existingReactionIndex] = reaction;
                        } else {
                            // Add new reaction
                            updatedReactions = [...reactions, reaction];
                        }

                        return {
                            ...msg,
                            reactions: updatedReactions,
                            $updatedAt: new Date().toISOString()
                        };
                    }
                    return msg;
                })
            );
        },

        // Clear all messages (only on workspace/channel change)
        clearAll: () => {
            set([]);
        },

        // Batch operations for better performance
        batchUpdate: async (operations: Array<{type: 'add' | 'update' | 'delete', message: Message}>) => {
            update(messages => {
                const newMessages = [...messages];
                
                operations.forEach(op => {
                    switch (op.type) {
                        case 'add':
                            if (!newMessages.some(m => m.$id === op.message.$id)) {
                                newMessages.push(op.message);
                            }
                            break;
                        case 'update':
                            const index = newMessages.findIndex(m => m.$id === op.message.$id);
                            if (index !== -1) {
                                newMessages[index] = { ...newMessages[index], ...op.message };
                            }
                            break;
                        case 'delete':
                            const deleteIndex = newMessages.findIndex(m => m.$id === op.message.$id);
                            if (deleteIndex !== -1) {
                                newMessages.splice(deleteIndex, 1);
                            }
                            break;
                    }
                });
                
                return newMessages;
            });
        },
        
        reset: () => set([])
    };
}

export const messageStore = createMessageStore();

// Helper function to create a derived store for a specific channel
export function getChannelMessages(channelId: string) {
    return derived(messageStore, $messages => {
        // Use a Set for faster lookups when filtering
        const channelMessages = $messages.filter(msg => msg.channel_id === channelId);
        
        // Use native sort for better performance
        channelMessages.sort((a, b) => {
            const aTime = new Date(a.$createdAt).getTime();
            const bTime = new Date(b.$createdAt).getTime();
            return aTime - bTime;
        });
        
        return channelMessages;
    });
} 