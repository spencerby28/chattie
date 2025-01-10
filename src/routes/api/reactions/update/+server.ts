import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Permission, Role } from 'appwrite';

export const PUT: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { reactionId, emoji, channelId } = await request.json();

        if (!reactionId || !emoji || !channelId) {
            throw error(400, 'ReactionId, emoji and channelId are required');
        }

        const appwrite = createAdminClient();

        const reaction = await appwrite.databases.updateDocument(
            'main',
            'reactions',
            reactionId,
            {
                emoji
            },
            [
                Permission.read(Role.label(channelId)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        return json({ reaction });

    } catch (e) {
        console.error('Error updating reaction:', e);
        throw error(500, 'Failed to update reaction');
    }
};

export const DELETE: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { reactionId } = await request.json();

        if (!reactionId) {
            throw error(400, 'ReactionId is required');
        }

        const appwrite = createAdminClient();

        await appwrite.databases.deleteDocument('main', 'reactions', reactionId);

        return json({ success: true });

    } catch (e) {
        console.error('Error deleting reaction:', e);
        throw error(500, 'Failed to delete reaction');
    }
};
