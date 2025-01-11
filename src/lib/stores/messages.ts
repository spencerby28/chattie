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
        addMessage: (message: Message) => {
            update(messages => {
                // Check if message already exists
                const exists = messages.some(m => m.$id === message.$id);
                if (exists) {
                    // If it exists, update it if the new message is newer
                    return messages.map(m => 
                        m.$id === message.$id && new Date(message.$updatedAt) > new Date(m.$updatedAt)
                            ? message 
                            : m
                    );
                }
                // If it doesn't exist, add it and sort
                const updatedMessages = [...messages, message];
                return updatedMessages.sort((a, b) => 
                    new Date(a.$createdAt).getTime() - new Date(b.$createdAt).getTime()
                );
            });
        },

        // Update an existing message
        updateMessage: (messageId: string, updates: Partial<Message>) => {
            update(messages => 
                messages.map(msg => 
                    msg.$id === messageId 
                        ? { ...msg, ...updates, $updatedAt: new Date().toISOString() }
                        : msg
                )
            );
        },

        // Delete a message
        deleteMessage: (messageId: string) => {
            update(messages => messages.filter(msg => msg.$id !== messageId));
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
        }
    };
}

export const messageStore = createMessageStore();

// Helper function to create a derived store for a specific channel
export function getChannelMessages(channelId: string) {
    return derived(messageStore, $messages => 
        $messages
            .filter(msg => msg.channel_id === channelId)
            .sort((a, b) => new Date(a.$createdAt).getTime() - new Date(b.$createdAt).getTime())
    );
} 