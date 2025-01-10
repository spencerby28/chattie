<script lang="ts">
	import { page } from '$app/stores';
	import type { Channel } from '$lib/types';
	import AddChannel from '$lib/components/features/AddChannel.svelte';
	import { channelStore } from '$lib/stores/channels';
	import * as ContextMenu from "$lib/components/ui/context-menu";
	import * as AlertDialog from "$lib/components/ui/alert-dialog";

	export let workspaceId: string;

	$: currentChannelId = $page.params.channelId;
	
	let channelToUpdate: Channel | null = null;
	let channelToDelete: Channel | null = null;
	let updatedName = '';
	let updatedType = '';

	async function handleUpdate(channel: Channel) {
		channelToUpdate = channel;
		updatedName = channel.name;
		updatedType = channel.type;
	}

	async function confirmUpdate() {
		if (!channelToUpdate) return;

		const element = document.querySelector(`a[href="/workspaces/${workspaceId}/channels/${channelToUpdate.$id}"]`);
		if (element) element.classList.add('animate-pulse', 'bg-gray-100', 'dark:bg-gray-800');

		try {
			const response = await fetch('/api/channel/update', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					channelId: channelToUpdate.$id,
					name: updatedName,
					type: updatedType
				})
			});

			if (!response.ok) {
				throw new Error('Failed to update channel');
			}

			// Update will happen through realtime
		} catch (err) {
			console.error('Error updating channel:', err);
		} finally {
			if (element) element.classList.remove('animate-pulse', 'bg-gray-100', 'dark:bg-gray-800');
			channelToUpdate = null;
		}
	}

	function handleDelete(channel: Channel) {
		channelToDelete = channel;
	}

	async function confirmDelete() {
		if (!channelToDelete) return;

		const element = document.querySelector(`a[href="/workspaces/${workspaceId}/channels/${channelToDelete.$id}"]`);
		if (element) element.classList.add('animate-pulse', 'bg-gray-100', 'dark:bg-gray-800');

		try {
			const response = await fetch('/api/channel/delete', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					channelId: channelToDelete.$id
				})
			});

			if (!response.ok) {
				throw new Error('Failed to delete channel');
			}

			// Delete will happen through realtime
		} catch (err) {
			console.error('Error deleting channel:', err);
		} finally {
			if (element) element.classList.remove('animate-pulse', 'bg-gray-100', 'dark:bg-gray-800');
			channelToDelete = null;
		}
	}
</script>

<div class="space-y-4">
	<!-- Public Channels -->
	<div class="mt-2">
		<div class="flex items-center justify-between mb-2">
			<h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Public</h3>
		</div>

		<div class="space-y-1">
			{#each $channelStore.channels.filter(c => c.workspace_id === workspaceId && c.type === 'public') as channel (channel.$id)}
				<ContextMenu.Root>
					<ContextMenu.Trigger>
						<a
							href="/workspaces/{workspaceId}/channels/{channel.$id}"
							class="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
							class:bg-accent={channel.$id === currentChannelId}
						>
							<span class="text-gray-500 dark:text-gray-400">#</span>
							<span class="text-sm">{channel.name}</span>
						</a>
					</ContextMenu.Trigger>
					<ContextMenu.Content>
						<ContextMenu.Item on:click={() => handleUpdate(channel)}>
							Update Channel
						</ContextMenu.Item>
						<ContextMenu.Separator />
						<ContextMenu.Item class="text-red-600 dark:text-red-400" on:click={() => handleDelete(channel)}>
							Delete Channel
						</ContextMenu.Item>
					</ContextMenu.Content>
				</ContextMenu.Root>
			{/each}
		</div>
	</div>

	<!-- Private Channels -->
	{#if $channelStore.channels.filter(c => c.workspace_id === workspaceId && c.type === 'private').length > 0}
		<div>
			<div class="flex items-center justify-between mb-2">
				<h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Private</h3>
			</div>

			<div class="space-y-1">
				{#each $channelStore.channels.filter(c => c.workspace_id === workspaceId && c.type === 'private') as channel (channel.$id)}
					<ContextMenu.Root>
						<ContextMenu.Trigger>
							<a
								href="/workspaces/{workspaceId}/channels/{channel.$id}"
								class="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
								class:bg-accent={channel.$id === currentChannelId}
							>
								<span class="text-gray-500 dark:text-gray-400">🔒</span>
								<span class="text-sm">{channel.name}</span>
							</a>
						</ContextMenu.Trigger>
						<ContextMenu.Content>
							<ContextMenu.Item on:click={() => handleUpdate(channel)}>
								Update Channel
							</ContextMenu.Item>
							<ContextMenu.Separator />
							<ContextMenu.Item class="text-red-600 dark:text-red-400" on:click={() => handleDelete(channel)}>
								Delete Channel
							</ContextMenu.Item>
						</ContextMenu.Content>
					</ContextMenu.Root>
				{/each}
			</div>
		</div>
	{/if}

	<div class="mt-4">
		<AddChannel {workspaceId} />
	</div>
</div>

<AlertDialog.Root open={!!channelToUpdate}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Update Channel</AlertDialog.Title>
			<AlertDialog.Description>
				Make changes to your channel here. Click save when you're done.
			</AlertDialog.Description>
		</AlertDialog.Header>

		<div class="grid gap-4 py-4">
			<div class="grid grid-cols-4 items-center gap-4">
				<label for="name" class="text-right">Name</label>
				<input
					id="name"
					bind:value={updatedName}
					class="col-span-3 flex h-10 rounded-md border border-input bg-transparent px-3 py-2 text-sm dark:border-gray-700"
				/>
			</div>
			<div class="grid grid-cols-4 items-center gap-4">
				<label for="type" class="text-right">Type</label>
				<select
					id="type"
					bind:value={updatedType}
					class="col-span-3 flex h-10 rounded-md border border-input bg-transparent px-3 py-2 text-sm dark:border-gray-700"
				>
					<option value="public">Public</option>
					<option value="private">Private</option>
				</select>
			</div>
		</div>

		<AlertDialog.Footer>
			<AlertDialog.Cancel on:click={() => channelToUpdate = null}>Cancel</AlertDialog.Cancel>
			<AlertDialog.Action on:click={confirmUpdate}>Save Changes</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>

<AlertDialog.Root open={!!channelToDelete}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Delete Channel</AlertDialog.Title>
			<AlertDialog.Description>
				Are you sure you want to delete this channel? This action cannot be undone.
			</AlertDialog.Description>
		</AlertDialog.Header>

		<AlertDialog.Footer>
			<AlertDialog.Cancel on:click={() => channelToDelete = null}>Cancel</AlertDialog.Cancel>
			<AlertDialog.Action class="bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800 text-white" on:click={confirmDelete}>Delete</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
