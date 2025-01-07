import { createSessionClient } from '$lib/appwrite/appwrite-client';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    try {
        // Use our helper function to create the Appwrite client.
        const { account } = createSessionClient(event);
        // Store the current logged in user in locals,
        // for easy access in our other routes.
        event.locals.user = await account.get();
        
    } catch (error) {
        // Clear the user if there's an error
        event.locals.user = undefined;
    }

    // Continue with the request.
    const response = await resolve(event);
    return response;
}; 