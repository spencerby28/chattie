import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';

export const load: PageServerLoad = async ({ locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const adminClient = createAdminClient();

    try {
        const messages = await adminClient.databases.listDocuments(
            'main',
            'messages',
            [Query.equal('channel_id', '6789a708000e2f7eaa7a')]
        );
        const ai_personas = await adminClient.databases.listDocuments(
            'main',
            'ai_personas',
            [Query.equal('workspace_id', '6789aa3a002443227373')]
        );

        return {
            messages: messages.documents,
            ai_personas: ai_personas.documents
        };
    } catch (err) {
        console.error('Error fetching AI persona:', err);
        throw error(500, 'Failed to load AI persona');
    }
};