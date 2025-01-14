<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { onMount } from 'svelte';

	let loading = false;
	let firstResponse: string | null = null;
	let status: string | null = null;
	let error: string | null = null;

	async function fetchDelayedResponses() {
		loading = true;
		error = null;
		firstResponse = null;
		status = null;

		try {
			const response = await fetch('/api/delay');
			const data = await response.json();
			
			firstResponse = data.firstResponse.message;
			status = data.status;
		} catch (e) {
			error = 'Failed to fetch responses';
			console.error(e);
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex flex-col items-center gap-8 p-8">
	<Button 
		on:click={fetchDelayedResponses}
		disabled={loading}
		variant="default"
		class="w-48"
	>
		{#if loading}
			Loading...
		{:else}
			Start Delayed Request
		{/if}
	</Button>

	{#if error}
		<p class="text-destructive">{error}</p>
	{/if}

	<div class="space-y-4">
		{#if firstResponse}
			<p class="text-foreground">{firstResponse}</p>
		{/if}

		{#if status}
			<p class="text-muted-foreground">Status: {status}</p>
			<p class="text-sm text-muted-foreground">Check the browser console to see when background work completes!</p>
		{/if}
	</div>
</div>
