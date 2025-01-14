<script lang="ts">
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import * as RadioGroup from '$lib/components/ui/radio-group';
	import { goto } from '$app/navigation';
	import { channelStore } from '$lib/stores/channels';
	import { toast } from 'svelte-sonner';
	import { RealtimeService } from '$lib/services/realtime';

	export let workspaceId: string;
	let channelName = '';
	let loading = false;
	let isPrivate = false;
	let error = '';
	let dialogOpen = false;

	// Get realtime service instance
	const realtime = RealtimeService.getInstance();

	// Subscribe to channelStore to check for duplicates and limits
	$: workspaceChannels = $channelStore.channels.filter((channel) => channel.workspace_id === workspaceId);
	$: channelExists = !loading && workspaceChannels.some(
		(channel) => channel.name.toLowerCase() === channelName.toLowerCase()
	);
	$: atChannelLimit = workspaceChannels.length >= 50;

	function validateChannelName(name: string): boolean {
		if (!name) {
			error = 'Channel name is required';
			return false;
		}
		if (name.length < 2) {
			error = 'Channel name must be at least 2 characters';
			return false;
		}
		if (name.length > 30) {
			error = 'Channel name must be less than 30 characters';
			return false;
		}
		if (!/^[a-z0-9-]+$/.test(name)) {
			error = 'Channel name can only contain lowercase letters, numbers, and hyphens';
			return false;
		}
		if (channelExists) {
			error = 'A channel with this name already exists';
			return false;
		}
		if (atChannelLimit) {
			error = 'Workspace has reached the maximum limit of 50 channels';
			return false;
		}
		error = '';
		return true;
	}

	async function handleCreateChannel() {
		if (loading) return;

		if (!validateChannelName(channelName)) {
			toast.error(error);
			return;
		}

		try {
			loading = true;
			const channelType = isPrivate ? 'private' : 'public';
			
			const response = await fetch('/api/channel/create', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					name: channelName,
					type: channelType,
					workspace_id: workspaceId
				})
			});

			const data = await response.json();
			
			if (!response.ok) {
				throw new Error(data.message || 'Failed to create channel');
			}

			// Reset form first
			channelName = '';
			isPrivate = false;
			dialogOpen = false;
			
			// Reinitialize realtime to get new permissions
		//	console.log('[AddChannel] Reinitializing realtime after channel creation');
		//	await realtime.reinitialize();
		//	console.log('[AddChannel] Realtime reinitialized');

			// Navigate to the new channel
			await goto(`/workspaces/${workspaceId}/channels/${data.channel.$id}`);
		} catch (error) {
			console.error('Error creating channel:', error);
			toast.error(error instanceof Error ? error.message : 'Failed to create channel');
		} finally {
			loading = false;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !loading && !error && channelName) {
			handleCreateChannel();
		}
	}
</script>

<AlertDialog.Root bind:open={dialogOpen}>
	<AlertDialog.Trigger asChild let:builder>
		<Button
			builders={[builder]}
			variant="ghost"
			class="flex items-center gap-2 px-2 py-1 text-gray-500 hover:text-gray-700 w-full justify-start"
			disabled={atChannelLimit}
		>
			<span class="text-lg">+</span>
			<span class="text-sm">Add a channel</span>
		</Button>
	</AlertDialog.Trigger>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Create New Channel</AlertDialog.Title>
			<AlertDialog.Description>
				Add a new channel to your workspace. Channel names must be lowercase, without spaces.
				{#if atChannelLimit}
					<p class="text-red-500 mt-2">
						This workspace has reached the maximum limit of 50 channels.
					</p>
				{/if}
			</AlertDialog.Description>
		</AlertDialog.Header>

		<div class="grid gap-4 pt-4 pb-2">
			<div class="grid grid-cols-4 items-center gap-4">
				<Label for="name" class="text-right">Name</Label>
				<div class="col-span-3">
					<Input
						id="name"
						bind:value={channelName}
						placeholder="new-channel"
						class="col-span-3"
						disabled={loading || atChannelLimit}
						on:keydown={handleKeydown}
					/>
				</div>
			</div>
			<div class="grid grid-cols-4 items-center gap-4">
				<Label class="text-right">Visibility</Label>
				<div class="col-span-3">
					<RadioGroup.Root
						value={isPrivate ? 'private' : 'public'}
						onValueChange={(value) => (isPrivate = value === 'private')}
						class="flex space-x-4"
					>
						<div class="flex items-center space-x-2">
							<RadioGroup.Item value="public" id="public" disabled={loading || atChannelLimit} />
							<Label for="public">Public</Label>
						</div>
						<div class="flex items-center space-x-2">
							<RadioGroup.Item value="private" id="private" disabled={loading || atChannelLimit} />
							<Label for="private">Private</Label>
						</div>
					</RadioGroup.Root>
				</div>
			</div>
		</div>
		{#if error || channelExists}
			<div class="text-sm text-red-500  text-center">
				{#if error}
					{error}
				{:else if channelExists}
					A channel with this name already exists
				{/if}
			</div>
		{/if}

		<AlertDialog.Footer>
			<AlertDialog.Cancel>Cancel</AlertDialog.Cancel>
			<AlertDialog.Action
				on:click={handleCreateChannel}
				disabled={loading || channelExists || atChannelLimit || !channelName}
			>
				{#if loading}
					<div
						class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"
					></div>
				{/if}
				Create Channel
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
