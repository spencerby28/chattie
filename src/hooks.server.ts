import { createSessionClient } from '$lib/appwrite/appwrite-client';
import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

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

    // Protected routes - only allow access to / if logged in
    const publicPaths = ['/login', '/register'];
    const isPublicPath = publicPaths.some(path => event.url.pathname.startsWith(path));

    if (!event.locals.user && !isPublicPath && event.url.pathname !== '/') {
        throw redirect(303, '/login');
    }

    // Continue with the request.
    const response = await resolve(event);
    return response;
}; 