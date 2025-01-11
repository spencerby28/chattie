import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { reactionId } = await request.json();
        console.log('[api/reactions/update] reactionId:', reactionId);

        if (!reactionId) {
            throw error(400, 'ReactionId is required');
        }

        const appwrite = createAdminClient();

        // Delete reaction
        await appwrite.databases.deleteDocument('main', 'reactions', reactionId);

        return json({ success: true });

    } catch (e) {
        console.error('Error deleting reaction:', e);
        throw error(500, 'Failed to delete reaction');
    }
};
