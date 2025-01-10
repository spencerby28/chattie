import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Permission, Role } from 'appwrite';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { messageId, emoji, channelId, remove } = await request.json();

        if (!messageId) {
            throw error(400, 'MessageId is required');
        }

        if (!emoji) {
            throw error(400, 'Emoji is required');
        }

        const appwrite = createAdminClient();

        // Get existing message to check reactions
        const existingMessage = await appwrite.databases.getDocument('main', 'messages', messageId);
        
        let reactions = existingMessage.reactions || [];
        const existingReactionIndex = reactions.findIndex((r: any) => r.emoji === emoji);

        if (existingReactionIndex >= 0) {
            if (remove) {
                // Remove user from reaction
                const userIds = reactions[existingReactionIndex].userIds.filter((id: string) => id !== locals.user?.$id);
                
                if (userIds.length === 0) {
                    // If no users left, remove the entire reaction
                    reactions.splice(existingReactionIndex, 1);
                } else {
                    // Update with remaining users
                    reactions[existingReactionIndex].userIds = userIds;
                }
            } else {
                // Add user to existing reaction if not already reacted
                const userIds = reactions[existingReactionIndex].userIds || [];
                if (!userIds.includes(locals.user.$id)) {
                    reactions[existingReactionIndex].userIds = [...userIds, locals.user.$id];
                }
            }
        } else if (!remove) {
            // Create new reaction with emoji and userId
            reactions.push({
                emoji,
                userIds: [locals.user.$id]
            });
        }

        // Update message with modified reactions
        await appwrite.databases.updateDocument(
            'main',
            'messages',
            messageId,
            {
                reactions,
            },
            [
                Permission.read(Role.label(channelId)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        return json({ messageId, emoji });

    } catch (e) {
        console.error('Error updating message reaction:', e);
        throw error(500, 'Failed to update message reaction');
    }
};

export const DELETE: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { messageId } = await request.json();

        if (!messageId) {
            throw error(400, 'MessageId is required');
        }

        const appwrite = createAdminClient();

        // Delete the message
        await appwrite.databases.deleteDocument('main', 'messages', messageId);

        return json({ success: true });

    } catch (e) {
        console.error('Error deleting message:', e);
        throw error(500, 'Failed to delete message');
    }
};
