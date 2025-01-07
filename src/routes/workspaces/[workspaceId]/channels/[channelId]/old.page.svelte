<script lang="ts">
	import { page } from '$app/stores';
	import MessageList from '$lib/components/features/MessageList.svelte';
	import MessageComposer from '$lib/components/features/MessageComposer.svelte';
	import type { Message } from '$lib/types';
	import { Client } from 'appwrite';
	import { PUBLIC_APPWRITE_PROJECT, PUBLIC_APPWRITE_ENDPOINT } from '$env/static/public';
	import { onMount, onDestroy } from 'svelte';
	import { messageStore } from '$lib/stores/messages';
	import type { Channel } from '$lib/types';
	let realtimeClient: Client | null = null;
	let unsubscribe: (() => void) | undefined;

	// Reset message store when page data changes
	$: if ($page.data.messages) {
		messageStore.set($page.data.messages);
	}

	async function setupRealtimeForChannel(channelId: string) {
		if (!realtimeClient) {
			return;
		}

		// Cleanup previous subscription if it exists
		if (unsubscribe) {
			unsubscribe();
		}

		unsubscribe = realtimeClient.subscribe(
			[
				'databases.main.collections.messages.documents',
				'databases.main.collections.reactions.documents'
			],
			async (response) => {
				const payload = response.payload as Message;
				console.log('Realtime event received:', {
					events: response.events,
					channelId
				});

				// Only process events for current channel
				if (payload.channel_id === channelId) {
					// Handle message operations
					if (response.events.some((e) => e.includes('messages.documents'))) {
						if (response.events.includes('databases.*.collections.*.documents.*.create')) {
							console.log('Creating new message:', payload);
							messageStore.addMessage(payload);
						}

						if (response.events.includes('databases.*.collections.*.documents.*.update')) {
							console.log('Updating message:', payload);
							messageStore.updateMessage(payload.$id, payload);
						}

						if (response.events.includes('databases.*.collections.*.documents.*.delete')) {
							console.log('Deleting message:', payload);
							messageStore.deleteMessage(payload.$id);
						}
					}

					// Handle reaction operations
					if (response.events.some((e) => e.includes('reactions.documents'))) {
						const messageId = payload.message_id;
						console.log('Processing reaction for message:', messageId);
						
						if (
							response.events.includes('databases.*.collections.*.documents.*.create') ||
							response.events.includes('databases.*.collections.*.documents.*.update')
						) {
							console.log('Adding/Updating reaction:', payload);
							messageStore.updateMessage(messageId, payload);
						}
					}
				}
			}
		);
	}

	onMount(async () => {
		// Setup realtime client
		realtimeClient = new Client();
		realtimeClient
			.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
			.setProject(PUBLIC_APPWRITE_PROJECT);

		// Only setup channel subscription after client is initialized
		if ($page.params.channelId) {
			await setupRealtimeForChannel($page.params.channelId);
		}
	});

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});

	// Watch for channel ID changes
	$: if (realtimeClient && $page.params.channelId) {
		setupRealtimeForChannel($page.params.channelId);
	}

	$: currentChannel = $page.data.workspace?.channels?.find((c: Channel) => c.$id === $page.params.channelId);
</script>

<div class="flex flex-col h-full">
	<!-- Channel Header -->
	<div class="p-4 border-b bg-white">
		<h1 class="text-xl font-semibold">#{currentChannel?.name || ''}</h1>
	</div>

	<!-- Message List - Takes remaining height minus header and composer -->
	<div class="flex-1 min-h-0 overflow-hidden">
		<MessageList messages={$messageStore} user={$page.data.user} />
	</div>

	<!-- Message Composer - Fixed height at bottom -->
	<div class="p-4 border-t bg-white">
		<MessageComposer />
	</div>
</div>
