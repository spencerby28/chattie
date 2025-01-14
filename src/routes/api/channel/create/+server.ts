import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';

// Background function to handle workspace member updates
async function updateWorkspaceMembers(workspaceId: string, channelId: string) {
    try {
        const appwrite = createAdminClient();
        
        // Update workspace to include new channel
        console.log('Getting workspace:', workspaceId);
        const workspace = await appwrite.databases.getDocument('main', 'workspaces', workspaceId);

        // Update labels for all workspace members
        console.log('Updating labels for workspace members:', workspace.members);
        const memberPromises = workspace.members.map(async (memberId: string) => {
            console.log('Getting member account:', memberId);
            const memberAccount = await appwrite.users.get(memberId);
            console.log('Updating member labels:', memberId);
            await appwrite.users.updateLabels(
                memberId,
                [...(memberAccount.labels || []), channelId]
            );
        });
        await Promise.all(memberPromises);
        console.log('Background workspace member updates complete for channel:', channelId);
    } catch (error) {
        console.error('Error in background workspace member updates:', error);
    }
}

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { name, type, workspace_id } = await request.json();

        if (!name || !type || !workspace_id) {
            throw error(400, 'Name, type and workspace_id are required');
        }

        console.log('[Channel Create] Starting channel creation:', { name, type, workspace_id });
        const appwrite = createAdminClient();

        // Create the channel document
        const channel = await appwrite.databases.createDocument(
            'main',
            'channels',
            ID.unique(),
            {
                name,
                type,
                workspace_id,
                members: [locals.user.$id]
            },
            type === 'private' ? [
                Permission.read(Role.user(locals.user.$id)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ] : [
                Permission.read(Role.users()),
                Permission.write(Role.users()),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        console.log('[Channel Create] Channel document created:', channel.$id);

        // Update current user's labels to include new channel
        console.log('[Channel Create] Updating user labels:', locals.user.$id);
        const account = await appwrite.users.get(locals.user.$id);
        await appwrite.users.updateLabels(
            account.$id,
            [...(account.labels || []), channel.$id]
        );
        console.log('[Channel Create] User labels updated');

        // Start background processing for other workspace members
        console.log('[Channel Create] Starting background member updates');
        updateWorkspaceMembers(workspace_id, channel.$id).catch(error => {
            console.error('[Channel Create] Background update error:', error);
        });

        // Return immediately with channel data and metadata
        console.log('[Channel Create] Returning response');
        return json({ 
            channel,
            status: 'processing',
            message: 'Channel created. Workspace member updates in progress.',
            metadata: {
                creator: locals.user.$id,
                workspace_id,
                timestamp: new Date().toISOString()
            }
        });

    } catch (e) {
        console.error('[Channel Create] Error:', e);
        throw error(500, 'Failed to create channel');
    }
};
