<script lang="ts">
	import { page } from '$app/stores';
	import type { SimpleMember } from '$lib/types';
	import Avatar from '$lib/components/ui/avatar/Avatar.svelte';
	import { avatarStore } from '$lib/stores/avatars';
	import { presenceStore } from '$lib/stores/presence';
	import CreateDirectMessage from '$lib/modal/CreateDirectMessage.svelte';
	import { channelStore } from '$lib/stores/channels';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
    import {Query} from 'appwrite';

	export let workspaceId: string;
	export let members: SimpleMember[];

	let selectedUserId: string | null = null;
	let directMessageDialogOpen = false;

	$: if (members) {
		avatarStore.prewarm(members.map(m => m.avatarId));
	}

	$: otherMembers = members.filter(member => member.id !== $page.data.user?.$id);
	$: currentUserId = $page.data.user?.$id;

	async function fetchInitialPresence() {
		try {
			const client = createBrowserClient();
			const response = await client.databases.listDocuments(
				'main',
				'presence',
				[
					// Query for presence docs of workspace members
					Query.equal('workspaceId', workspaceId),
					Query.equal('userId', otherMembers.map(m => m.id))
				]
			);

			// Update presence store with fetched data
			response.documents.forEach(doc => {
				presenceStore.updateStatus(
					doc.userId,
					doc.baseStatus,
					doc.customStatus
				);
			});
		} catch (error) {
			console.error('Error fetching presence data:', error);
		}
	}

	onMount(() => {
		fetchInitialPresence();
	});

	function getStatusColor(userId: string) {
		const presence = $presenceStore[userId];
		if (!presence) return 'bg-gray-400'; // offline
		
		switch (presence.baseStatus) {
			case 'online':
				return 'bg-green-500';
			case 'away':
				return 'bg-yellow-500';
			case 'offline':
				return 'bg-gray-400';
			default:
				return 'bg-gray-400';
		}
	}

	function handleMemberClick(memberId: string) {
		if (!currentUserId) return;

		// Find DM channel that includes both the current user and selected member
		const existingChannel = $channelStore.channels.find(channel => 
			channel.type === 'dm' && 
			channel.members?.length === 2 &&
			channel.members.includes(memberId) && 
			channel.members.includes(currentUserId)
		);

		if (existingChannel) {
			// Navigate to existing channel
			goto(`/workspaces/${workspaceId}/channels/${existingChannel.$id}`);
			return;
		}

		// Only open modal if no existing channel found
		selectedUserId = memberId;
		directMessageDialogOpen = true;
	}
</script>

<div class="space-y-1">
	{#each otherMembers as member (member.id)}
		<button
			on:click={() => handleMemberClick(member.id)}
			class="flex items-center gap-2 w-full px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
		>
			<div class="relative">
				<Avatar
					src={member.avatarId ? avatarStore.getAvatarUrl(member.avatarId) : undefined}
					fallback={member.name?.[0]?.toUpperCase() || '?'}
					name={member.name}
					size="md"
					
				/>
				<div class={`absolute bottom-0 right-0 w-2 h-2 rounded-full ${getStatusColor(member.id)} ring-2 ring-white dark:ring-gray-950`} ></div>
			</div>
			<span class="text-sm ml-1">{member.name}</span>
		</button>
	{/each}
</div>

<CreateDirectMessage
	{workspaceId}
	{members}
	open={directMessageDialogOpen}
	onOpenChange={(open) => (directMessageDialogOpen = open)}
	{selectedUserId}
/>
