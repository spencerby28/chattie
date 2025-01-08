<script lang="ts">
	import { page } from '$app/stores';
	import { channelStore } from '$lib/stores/channels';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import { onMount } from 'svelte';
	import { RealtimeService } from '$lib/services/realtime';

	// Only initialize channel store once when the workspace first loads
	onMount(() => {

		// Check if we need to reinitialize the realtime connection
		const searchParams = new URLSearchParams($page.url.search);
		if (searchParams.get('reinitialize') === 'true') {
			const realtime = RealtimeService.getInstance();
			realtime.reinitialize();
			// Remove the flag from URL to prevent unnecessary reinitializations
			const newUrl = new URL(window.location.href);
			newUrl.searchParams.delete('reinitialize');
			window.history.replaceState({}, '', newUrl);
		}
	});
</script>

<div class="flex h-full">
	<Sidebar />
	<main class="flex-1">
		<slot /> 
	</main>
</div> 