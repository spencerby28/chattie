import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';


export const load: LayoutServerLoad = async ({ params, locals }) => {
	if (!locals.user) {
		throw error(401, 'Unauthorized');
	}
	const { databases, users } = createAdminClient();
	try {
		const workspace = await databases.getDocument('main', 'workspaces', params.workspaceId) ;

		// Fetch user data for all members
		const memberPromises = workspace.members.map(async (memberId: string) => {
			try {
				const user = await users.get(memberId);
				return {
					id: user.$id,
					name: user.name || user.email
				};
			} catch (e) {
				console.error(`Error fetching user ${memberId}:`, e);
				return { id: memberId, name: 'Unknown User' };
			}
		});

		const memberData = await Promise.all(memberPromises);

		// Filter channels based on type and membership
		const filteredChannels = workspace.channels?.filter((channel: any) => {
			if (channel.type === 'public') return true;
			return channel.members.includes(locals.user!.$id);
		}) || [];

		return {
			workspace: {
				...workspace,
				channels: filteredChannels,
				memberData // Add the simplified member data
			}
		};
	} catch (e) {
		console.error('Error loading workspace:', e);
		throw error(404, {
			message: 'The requested workspace could not be found or there was an error loading it. Please try again.'
		});
	}
};
