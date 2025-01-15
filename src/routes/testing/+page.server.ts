import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';

export const load: PageServerLoad = async ({ locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const messageId = '6787e1cf002688bd761c';
    const { databases } = createAdminClient();
    
    try {
        const message = await databases.getDocument(
            'main',
            'messages',
            messageId
        );
        
        return {
            message
        };
    } catch (e) {
        console.error('Failed to load message:', e);
        throw error(500, {
            message: 'Failed to load message. Please try again.'
        });
    }
};