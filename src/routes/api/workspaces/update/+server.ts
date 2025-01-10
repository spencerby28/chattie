import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';

export const DELETE: RequestHandler = async ({ request, locals, fetch }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { workspaceId } = await request.json();

        if (!workspaceId) {
            throw error(400, 'Workspace ID is required');
        }

        const appwrite = createAdminClient();


        // Find all channels in the workspace
        const channels = await appwrite.databases.listDocuments(
            'main',
            'channels',
            [
                Query.equal('workspace_id', workspaceId)
            ]
        );

        // Delete all channels in the workspace
        if (channels.documents.length > 0) {
            await Promise.all(
                channels.documents.map(async (channel) => {
                    // Call channel delete endpoint for each channel using event.fetch
                    await fetch('/api/channel/update', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            channelId: channel.$id
                        })
                    });
                })
            );
        }

        // Finally delete the workspace itself
        await appwrite.databases.deleteDocument(
            'main',
            'workspaces',
            workspaceId
        );

        return json({ success: true });

    } catch (e) {
        console.error('Error deleting workspace:', e);
        throw error(500, 'Failed to delete workspace');
    }
};
