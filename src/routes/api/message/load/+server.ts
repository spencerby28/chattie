import { json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        return new Response('Unauthorized', { status: 401 });
    }

    try {
        const { channelId, offset = 0 } = await request.json();
        
        if (!channelId) {
            return json({ 
                error: 'Channel ID is required' 
            }, { status: 400 });
        }

        const client = createAdminClient();
        const limit = 50;

        const messagesResponse = await client.databases.listDocuments(
            'main',
            'messages',
            [
                Query.equal('channel_id', channelId),
                Query.orderDesc('$createdAt'),
                Query.limit(limit),
                Query.offset(offset)
            ]
        );

        return json({
            messages: messagesResponse.documents,
            total: messagesResponse.total
        });

    } catch (error) {
        console.error('Error loading messages:', error);
        return json({ 
            error: 'Failed to load messages' 
        }, { status: 500 });
    }
};
