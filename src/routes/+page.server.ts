import { createSessionClient } from '$lib/appwrite/appwrite-client';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import type { Channel } from '$lib/types';
import type { PageServerLoad } from './$types';
import { error, redirect, type Actions } from '@sveltejs/kit';
import { Query, Permission, Role } from 'appwrite';

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

			const account = await adminClient.users.get(locals.user.$id);
			const channelIds = channelsResponse.documents.map((channel) => channel.$id);
			console.log('updating labels with channels:', channelIds);
			await adminClient.users.updateLabels(
				account.$id,
				[...(account.labels || []), ...channelIds]
			);
			console.log('joined workspace:', workspaceId);
			console.log('labels:', account.labels);
			
		} catch (e) {
			console.error('Failed to join workspace:', e);
			throw error(500, 'Failed to join workspace');
		}
        throw redirect(303, `/workspaces/${workspaceId}?reinitialize=true`);
	}
};
