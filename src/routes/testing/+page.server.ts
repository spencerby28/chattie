import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';

export const load: PageServerLoad = async ({ locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const adminClient = createAdminClient();

    try {
        const persona = await adminClient.databases.getDocument(
            'main',
            'ai_personas',
            '678816c30019011bc460'
        );
        return {
            persona
        };
    } catch (err) {
        console.error('Error fetching AI persona:', err);
        throw error(500, 'Failed to load AI persona');
    }
};