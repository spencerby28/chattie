<script lang="ts">
	import '../app.css';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import { Toaster } from 'svelte-sonner';
	import { onMount, onDestroy } from 'svelte';
	import { RealtimeService } from '$lib/services/realtime';
	import { page } from '$app/stores';
	import { writable } from 'svelte/store';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser';

	interface NotificationPreferences {
		[key: string]: boolean;
	}

	export const notificationPrefs = writable<NotificationPreferences>({});
	let unsubscribe: (() => void) | undefined;

	onMount(async () => {
		// Initialize global realtime connection
		if (typeof window !== 'undefined') {
			unsubscribe = RealtimeService.getInstance().initialize();
		}

		// Load notification preferences
		const { account } = createBrowserClient();
		try {
			const prefs = await account.getPrefs();
			notificationPrefs.set(prefs || {});
		} catch (error) {
			console.error('Error loading notification preferences:', error);
		}
	});

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});
</script>

<Toaster richColors closeButton position="top-right" />
<AppShell>
	<slot />
</AppShell>
