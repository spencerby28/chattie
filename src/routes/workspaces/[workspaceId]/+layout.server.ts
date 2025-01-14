import { createSessionClient } from '$lib/appwrite/appwrite-client';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Message } from '$lib/types';

export const load = (async ({ locals, params, ...event }) => {
	if (!locals.user) {
		return {
			messages: [],
			channels: [],
			workspace: null,
			memberData: []
		};
	}

	try {
		const client = createSessionClient(event);
		const { databases, users } = createAdminClient();

		// Get workspace document
		const workspace = await databases.getDocument('main', 'workspaces', params.workspaceId);
		console.log('Loaded workspace:', workspace);
		console.log('Workspace members:', workspace.members);
		// Fetch member data
		const memberPromises = workspace.members.map(async (memberId: string) => {
			try {
				console.log('Fetching user data for:', memberId);
				const user = await users.get(memberId);
				const prefs = user.prefs || {};
				console.log('User data fetched:', user);
				return {
					id: user.$id,
					name: user.name || user.email,
					avatarId: prefs.avatarId || null,
					bot: user.email?.endsWith('@chattie.local') || false
				};
			} catch (e) {
				console.error(`Error fetching user ${memberId}:`, e);
				return { id: memberId, name: 'Unknown User', avatarId: null, bot: false };
			}
		});

		const memberData = await Promise.all(memberPromises);
		console.log('Final memberData:', memberData);

		// Get all messages for this workspace
		/*
		const messagesResponse = await client.databases.listDocuments(
			'main', 
			'messages',
			[
				Query.equal('workspace_id', params.workspaceId),
				Query.orderDesc('$createdAt'),
				Query.limit(100)
			]
		);
		*/

		// Filter channels based on type and membership
		const filteredChannels = workspace.channels?.filter((channel: any) => {
			if (channel.type === 'public') return true;
			return channel.members.includes(locals.user!.$id);
		}) || [];

		return {
			//messages: messagesResponse.documents as Message[],
			channels: filteredChannels,
			workspace,
			memberData
		};

	} catch (e) {
		console.error('Error loading workspace data:', e);
		throw error(500, 'Failed to load workspace data');
	}
}) satisfies LayoutServerLoad;
