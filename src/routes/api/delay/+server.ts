import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Helper function to simulate background work
async function backgroundWork() {
    try {
        // Second response after additional 3 seconds
        await new Promise(resolve => setTimeout(resolve, 3000));
        console.log('Background work completed after 3 seconds');
    } catch (error) {
        console.error('Background work failed:', error);
    }
}

export const GET: RequestHandler = async ({ platform }) => {
    // First response after 1 second

    const firstResponse = { message: 'First response after 1 second' };
    
    // Start the background work without awaiting it
    backgroundWork().catch(console.error);

    // Return immediately with just the first response
    return json({
        firstResponse,
        message: 'Background work started',
        status: 'processing'
    });
};
