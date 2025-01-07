import { error } from '@sveltejs/kit';
import type { Actions } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID } from 'appwrite';

export const actions = {
    default: async () => {
        try {
            const appwrite = createAdminClient();
            const randomString = Math.random().toString(36).substring(7);
            
            const document = await appwrite.databases.createDocument(
                'bruh',
                'bruh',
                ID.unique(),
                {
                    data: randomString,
                }
                
            );
            
            return { success: true, data: randomString };
        } catch (e) {
            console.error('Error creating document:', e);
            throw error(500, 'Failed to insert data');
        }
    }
} satisfies Actions;
