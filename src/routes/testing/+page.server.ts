import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';

export const load: PageServerLoad = async ({ url, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const searchQuery = url.searchParams.get('q') || '';
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
        
        return {
            messages: messages.documents,
            searchQuery
        };
    } catch (e) {
        console.error('Search error:', e);
        throw error(500, {
            message: 'Failed to search messages. Please try again.'
        });
    }
};