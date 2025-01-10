import { json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
    try {
        // Get user ID from request body
        const { userId } = await request.json();

        if (!userId) {
            return json({ error: 'User ID is required' }, { status: 400 });
        }

        // Create admin client
        const client = createAdminClient();
        
        // Fetch user document
        const user = await client.users.get(userId);

        return json(user);
    } catch (error) {
        console.error('Error fetching user:', error);
        return json({ error: 'Internal server error' }, { status: 500 });
    }
};
