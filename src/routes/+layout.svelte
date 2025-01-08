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

	$: isAuthRoute = $page.url.pathname === '/login' || $page.url.pathname === '/register' || $page.url.pathname === '/welcome';

	onMount(async () => {
		// Only initialize if we're logged in and in the browser
		if (typeof window !== 'undefined' && !isAuthRoute) {
			unsubscribe = RealtimeService.getInstance().initialize();

			// Load notification preferences
			const { account } = createBrowserClient();
			try {
				const prefs = await account.getPrefs();
				notificationPrefs.set(prefs || {});
			} catch (error) {
				console.error('Error loading notification preferences:', error);
			}
		}
	});

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});
</script>

<svelte:head>
	<title>Chattie</title>
	<link rel="manifest" href="/site.webmanifest">
	<link rel="apple-touch-icon" sizes="180x180" href="/favicon/apple-touch-icon.png">
	<link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png">
	<link rel="icon" type="image/png" sizes="16x16" href="/favicon/favicon-16x16.png">
	<script defer src="https://cloud.umami.is/script.js" data-website-id="e6467774-8839-424f-a021-0be22565ff94"></script>
</svelte:head>

<Toaster richColors closeButton position="top-right" />
{#if !isAuthRoute}
	<AppShell>
		<slot />
	</AppShell>
{:else}
	<slot />
{/if}
