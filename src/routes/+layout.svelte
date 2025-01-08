<script lang="ts">
	import '../app.css';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import { Toaster } from 'svelte-sonner';
	import { onMount, onDestroy } from 'svelte';
	import { RealtimeService } from '$lib/services/realtime';
	import { page } from '$app/stores';
	import { writable } from 'svelte/store';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
	import { channelStore } from '$lib/stores/channels';
	import { workspace } from '$lib/stores/workspace';

	interface NotificationPreferences {
		[key: string]: boolean;
	}

	export const notificationPrefs = writable<NotificationPreferences>({});
	let unsubscribe: (() => void) | undefined;

	$: isAuthRoute = $page.url.pathname === '/login' || $page.url.pathname === '/register' || $page.url.pathname === '/welcome';
	$: currentChannel = $channelStore.find(channel => channel.$id === $page.params.channelId);
	$: pageTitle = isAuthRoute 
		? 'Chattie' 
		: currentChannel 
			? `#${currentChannel.name} | ${$workspace.currentWorkspace?.name || 'Chattie'}`
			: $workspace.currentWorkspace?.name 
				? `${$workspace.currentWorkspace.name} | Chattie`
				: 'Chattie';

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
	<title>{pageTitle}</title>
	<meta name="description" content="Chattie - A modern real-time chat application for teams and communities" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="theme-color" content="#ffffff" />
	<meta name="application-name" content="Chattie" />
	<meta name="apple-mobile-web-app-title" content="Chattie" />
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-status-bar-style" content="default" />
	<meta name="format-detection" content="telephone=no" />
	<meta name="mobile-web-app-capable" content="yes" />
	<meta name="msapplication-TileColor" content="#ffffff" />
	<meta name="msapplication-tap-highlight" content="no" />
	<meta property="og:title" content={pageTitle} />
	<meta property="og:description" content="Chattie - A modern real-time chat application for teams and communities" />
	<meta property="og:type" content="website" />
	<meta property="og:site_name" content="Chattie" />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content={pageTitle} />
	<meta name="twitter:description" content="Chattie - A modern real-time chat application for teams and communities" />
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
