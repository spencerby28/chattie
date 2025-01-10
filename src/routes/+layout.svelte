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
	import { mode } from '$lib/stores/mode';
	import { browser } from '$app/environment';

	interface NotificationPreferences {
		[key: string]: boolean;
	}

	export const notificationPrefs = writable<NotificationPreferences>({});

	let cleanup: (() => void) | undefined;
	let previousPath: string | undefined;

	// Get realtime service instance
	const realtime = RealtimeService.getInstance();
	const connectionState = realtime.getConnectionState();

	$: nonAuthRoute = !$page.url.pathname.startsWith('/login') && !$page.url.pathname.startsWith('/register');
	$: currentChannel = browser ? $channelStore.channels.find(channel => channel.$id === $page.params.channelId) : null;

	// Watch for route changes and reinitialize on home page
	$: if (browser && $page.url.pathname !== previousPath) {
		previousPath = $page.url.pathname;
		if ($page.url.pathname === '/') {
			console.log('[Layout] Home page detected, checking realtime connection');
			if (nonAuthRoute && $connectionState === 'disconnected') {
				console.log('[Layout] Initializing realtime on home page');
				realtime.initialize().then(newCleanup => {
					if (cleanup) cleanup();
					cleanup = newCleanup;
				}).catch(error => {
					console.error('[Layout] Failed to initialize realtime:', error);
				});
			}
		}
	}

	$: pageTitle = !nonAuthRoute 
		? 'Chattie' 
		: currentChannel 
			? `#${currentChannel.name} | ${$workspace.currentWorkspace?.name || 'Chattie'}`
			: $workspace.currentWorkspace?.name 
				? `${$workspace.currentWorkspace.name} | Chattie` 
				: 'Chattie';

	onMount(async () => {
		if (!browser) return;
		
		// Only initialize if we're logged in and in the browser
		console.log('[Layout] Checking initialization conditions:', { nonAuthRoute, browser });
		if (nonAuthRoute) {
			try {
				console.log('[Layout] Initializing RealtimeService');
				cleanup = await realtime.initialize();
				console.log('[Layout] RealtimeService initialized successfully');
			} catch (error) {
				console.error('[Layout] Failed to initialize RealtimeService:', error);
			}
		} else {
			console.log('[Layout] Skipping RealtimeService initialization:', { 
				reason: 'Auth route'
			});
		}
	});

	onDestroy(() => {
		if (!browser) return;
		
		console.log('[Layout] Running cleanup');
		if (cleanup) {
			console.log('[Layout] Running cleanup function');
				cleanup();
				cleanup = undefined;
		}
		realtime.cleanup();
	});
	$: console.log('mode', $mode)
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



{#if nonAuthRoute}
	<AppShell>
		<slot />
	</AppShell>
	<Toaster position="bottom-right" theme={$mode} />
{:else}
	<slot />
{/if}
