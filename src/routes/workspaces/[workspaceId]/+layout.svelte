<script lang="ts">
	import { page } from '$app/stores';
	import { channelStore } from '$lib/stores/channels';
	import { memberStore } from '$lib/stores/members';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import { onMount } from 'svelte';
	import { RealtimeService } from '$lib/services/realtime';
	import { browser } from '$app/environment';
	import { messageStore } from '$lib/stores/messages';
	import { presenceService } from '$lib/services/presence';
	import { presenceStore } from '$lib/stores/presence';

	onMount(() => {
		// Initialize member store with data from the server
		if ($page.data.memberData) {
			console.log('[WorkspaceLayout] memberData ran', $page.data.memberData);
			memberStore.updateMembers($page.data.memberData);
		}

		// Initialize message store with workspace messages 
		if ($page.data.messages) {
			messageStore.initializeForWorkspace($page.data.messages);
		}

		// Initialize channel store with workspace channels
		if ($page.data.channels && $page.params.workspaceId !== $channelStore.currentWorkspaceId) {
			channelStore.setChannels($page.data.channels);
		}
	});

	// Use the store value instead of direct page data
	$: members = $memberStore;
	$: console.log('[WorkspaceLayout] members', members);

	// Get realtime service instance
	const realtime = RealtimeService.getInstance();
	const connectionState = realtime.getConnectionState();

	// Handle workspace initialization and reinitialization
	$: if (browser && $page.url.searchParams.get('reinitialize') === 'true') {
		console.log('[WorkspaceLayout] Reinitialize flag detected, reinitializing realtime');
		realtime.reinitialize().then(() => {
			// Remove the flag from URL to prevent unnecessary reinitializations
			const newUrl = new URL(window.location.href);
			newUrl.searchParams.delete('reinitialize');
			window.history.replaceState({}, '', newUrl);
		}).catch(error => {
			console.error('[WorkspaceLayout] Failed to reinitialize realtime:', error);
		});
	}

	// Handle initial connection
	onMount(async () => {
		if (!browser) return;

		// Check connection state and initialize if needed
		if ($connectionState === 'disconnected') {
			console.log('[WorkspaceLayout] Initializing realtime connection');
			try {
				await realtime.initialize();
				console.log('[WorkspaceLayout] Realtime connection initialized');
			} catch (error) {
				console.error('[WorkspaceLayout] Failed to initialize realtime:', error);
			}
		}

		if ($page.data.user) {
			
			presenceService.initialize($page.data.user.$id);
			presenceStore.setInitialState($page.data.members);
		}

		return () => {
			presenceService.cleanup();
			presenceStore.reset();
		};
	});
</script>

<div class="flex h-full">
	<Sidebar {members} />
	<main class="flex-1">
		<slot /> 
	</main>
</div> 