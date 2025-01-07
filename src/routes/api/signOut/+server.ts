import { createSessionClient } from '$lib/appwrite/appwrite-client';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ cookies }) => {
    try {
        const { account } = createSessionClient({ cookies });
        
        // Delete the current session
        await account.deleteSession('current');
        
        // Remove the session cookies
        cookies.delete('sessionId', { path: '/' });
        cookies.delete('a_session_chattie', { path: '/' });
        
        return new Response(null, {
            status: 303,
            headers: {
                Location: '/'
            }
        });
    } catch (error) {
        console.error('Sign out error:', error);
        return new Response(JSON.stringify({ error: 'Failed to sign out' }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
};
