import { error, json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const searchQuery = url.searchParams.get('q');
    
    if (!searchQuery) {
        return json([]);
    }

    const { databases } = createAdminClient();
    
    try {
        const messages = await databases.listDocuments(
            'main',
            'messages',
            [
                Query.search('content', searchQuery),
                Query.limit(10)
            ]
        );
        
        return json(messages.documents);
    } catch (e) {
        console.error('Search error:', e);
        throw error(500, {
            message: 'Failed to search messages. Please try again.'
        });
    }
};
