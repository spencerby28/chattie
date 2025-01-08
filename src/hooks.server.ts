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

    // Protected routes - redirect to login if not authenticated
    const publicPaths = ['/login', '/register', '/welcome'];
    const isPublicPath = publicPaths.some(path => event.url.pathname.startsWith(path));

    // If user is logged in and trying to access login/register, redirect to workspaces
    if (event.locals.user && isPublicPath) {
        throw redirect(303, '/');
    }

    // If user is not logged in and trying to access protected routes, redirect to login
    if (!event.locals.user && !isPublicPath) {
        throw redirect(303, '/login');
    }

    // Continue with the request.
    const response = await resolve(event);
    return response;
}; 