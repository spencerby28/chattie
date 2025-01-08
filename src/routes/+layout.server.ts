import { createSessionClient } from '$lib/appwrite/appwrite-client';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load = (async ({ locals, ...event }) => {
	if (!locals.user) {
		
		return {
			workspaces: []

		};
	}

	try {
		const client = createSessionClient(event);
		const response = await client.databases.listDocuments(
			'main',
			'workspaces',
			[] // No query to get all workspaces
		);

        //console.log(response.documents);

		return {
			workspaces: response.documents.map(workspace => ({
				$id: workspace.$id,
				name: workspace.name,
				members: workspace.members
			})),
            user: locals.user
		};
	} catch (e) {
		throw error(500, 'Failed to load workspaces');
	}
}) satisfies LayoutServerLoad;
