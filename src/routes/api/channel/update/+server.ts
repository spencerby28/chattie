import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { channelId, name, type } = await request.json();

        if (!channelId || !name || !type) {
            throw error(400, 'Channel ID, name and type are required');
        }

        const appwrite = createAdminClient();

        // Add 2 second timeout
        

        // Update the channel document
        const channel = await appwrite.databases.updateDocument(
            'main',
            'channels',
            channelId,
            {
                name,
                type
            }
        );
        console.log('Channel updated:', channel);

        return json({ channel });

    } catch (e) {
        console.error('Error updating channel:', e);
        throw error(500, 'Failed to update channel');
    }
};

export const DELETE: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { channelId } = await request.json();

        if (!channelId) {
            throw error(400, 'Channel ID is required');
        }

        const appwrite = createAdminClient();

        // Delete the channel document
        await appwrite.databases.deleteDocument(
            'main',
            'channels',
            channelId
        );
        console.log('Channel deleted:', channelId);

        return json({ success: true });

    } catch (e) {
        console.error('Error deleting channel:', e);
        throw error(500, 'Failed to delete channel');
    }
};
