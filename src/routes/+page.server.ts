import { createSessionClient } from '$lib/appwrite/appwrite-client';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import type { Channel } from '$lib/types';
import type { PageServerLoad } from './$types';
import { error, redirect, type Actions } from '@sveltejs/kit';
import { Query, Permission, Role } from 'appwrite';

/*

export const load = (async ({ locals, ...event }) => {
	if (!locals.user) {
		return {
			workspaces: [],
			user: null
		};
	}

	try {
		const client = createSessionClient(event);
		const response = await client.databases.listDocuments(
			'main',
			'workspaces',
			[] // No query to get all workspaces
		);

		return {
			workspaces: response.documents,
			user: locals.user
		};
	} catch (e) {
		throw error(500, 'Failed to load workspaces');
	}
}) satisfies PageServerLoad;
*/
export const actions: Actions = {
	joinWorkspace: async ({ request, locals, ...event }) => {
		if (!locals.user) {
			throw error(401, 'Unauthorized');
		}

		const data = await request.formData();
		const workspaceId = data.get('workspaceId')?.toString();

		if (!workspaceId) {
			throw error(400, 'Workspace ID is required');
		}

		try {
			const adminClient = createAdminClient();

			// Get the current workspace
			const workspace = await adminClient.databases.getDocument('main', 'workspaces', workspaceId);

			await adminClient.databases.updateDocument('main', 'workspaces', workspaceId, {
				members: [...workspace.members, locals.user.$id]
			}, [
				...workspace.$permissions,
				Permission.update(Role.user(locals.user.$id))
			]);
			
			// Get channels for this workspace
			const channelsResponse = await adminClient.databases.listDocuments(
				'main',
				'channels',
				[Query.equal('workspace_id', workspaceId)]
			);

			// Start background processing for user labels
			updateUserLabels(locals.user.$id, channelsResponse.documents, workspaceId).catch(error => {
				console.error('Background label update error:', error);
			});
			
		} catch (e) {
			console.error('Failed to join workspace:', e);
			throw error(500, 'Failed to join workspace');
		}
        throw redirect(303, `/workspaces/${workspaceId}?reinitialize=true`);
	}
};

// Background function to handle user label updates
async function updateUserLabels(userId: string, channels: any[], workspaceId: string) {
    try {
        const appwrite = createAdminClient();
        
        // Get user's current labels
        console.log('Getting user account:', userId);
        const userAccount = await appwrite.users.get(userId);

        // Get public channel IDs and add workspace ID
        const channelIds = channels
            .filter(channel => channel.type === 'public')
            .map(channel => channel.$id);
        channelIds.push(workspaceId);

        // Update user's labels with channel IDs
        console.log('Updating user labels:', userId);
        await appwrite.users.updateLabels(
            userId,
            [...(userAccount.labels || []), ...channelIds]
        );

        console.log('Background user label updates complete for user:', userId);
    } catch (error) {
        console.error('Error in background user label updates:', error);
    }
}
