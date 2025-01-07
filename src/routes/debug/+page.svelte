<script lang="ts">
	import { onMount } from 'svelte';

	let session: string | null = null;
	let error: string | null = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/session');
			const data = await response.json();
			session = data.session;
		} catch (e) {
			error = 'Failed to fetch session';
			console.error(e);
		}
	});
</script>

<div class="p-4">
	<h1 class="text-2xl font-bold mb-4">Debug Info</h1>

	{#if error}
		<p class="text-red-500">{error}</p>
	{:else if session === null}
		<p>No active session</p>
	{:else}
		<p>Current session: {session}</p>
	{/if}

	<form method="POST" class="mt-4" use:enhance>
		<button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
			Add Random String to Bruh Collection
		</button>
	</form>
</div>
