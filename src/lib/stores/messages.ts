import { writable } from 'svelte/store';
import type { Message, Reaction } from '$lib/types';

function createMessageStore() {
    const { subscribe, set, update } = writable<Message[]>([]);

    return {
        subscribe,
        set,
        
        // Add a new message
        addMessage: (message: Message) => {
            update(messages => [...messages, message]);
        },

        // Update an existing message
        updateMessage: (messageId: string, updates: Partial<Message>) => {
            update(messages => 
                messages.map(msg => 
                    msg.$id === messageId 
                        ? { ...msg, ...updates }
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
                            reactions: updatedReactions
                        };
                    }
                    return msg;
                })
            );
        }
    };
}

export const messageStore = createMessageStore(); 