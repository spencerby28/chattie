<script lang="ts">
	import { page } from '$app/stores';
	import MessageList from '$lib/components/features/MessageList.svelte';
	import MessageComposer from '$lib/components/features/MessageComposer.svelte';
	import type { Message } from '$lib/types';
	import { messageStore } from '$lib/stores/messages';
	import type { Channel } from '$lib/types';
	import { channelStore } from '$lib/stores/channels';
	import ReplyBox from '$lib/components/features/ReplyBox.svelte';
	import RichMessageComposer from '$lib/components/features/messages/RichMessageComposer.svelte';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser.js';
	import { onMount } from 'svelte';
	import { memberStore } from '$lib/stores/members';
	
	onMount(() => {
		const { account } = createBrowserClient();
		account.get();
	});

	export let data;

	// Initialize or update messages from server data
	$: if (data.messages?.length) {
		messageStore.initializeForWorkspace(data.messages as Message[]);
	}

	$: currentChannel = $channelStore.channels.find(channel => channel.$id === $page.params.channelId);
	$: console.log('channelstore', $channelStore.channels)
	$: members = $memberStore;

	$: channelTitle = (() => {
		if (!currentChannel) return '';
		if (currentChannel.type === 'thread') {
			return `Reply to: ${data.messages?.[0]?.content}` || currentChannel.name;
		}
		if (currentChannel.type === 'dm' && currentChannel.members.length === 2) {
			const otherMember = members?.find(m => 
				m.id !== $page.data.user?.$id && 
				currentChannel.members.includes(m.id)
			);
			return otherMember ? `Chat with ${otherMember.name}` : currentChannel.name;
		}
		return currentChannel.name;
	})();
	$: console.log('channelTitle', currentChannel)

	function handleBackToChannel() {
		window.history.back();
	}
</script>

<div class="flex flex-col h-full bg-white dark:bg-gray-950">
	<!-- Channel Header -->
	<div class="p-4 border-b bg-white dark:bg-gray-950">
		<div class="flex items-center gap-4">
			{#if currentChannel?.type === 'thread'}
				<button 
					on:click={handleBackToChannel}
					class="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
				</button>
			{/if}
			<h1 class="text-xl font-semibold">
				{#if currentChannel?.type === 'dm'}
					{channelTitle}
				{:else}
					#{channelTitle}
				{/if}
			</h1>
		</div>
	</div>

	<!-- Message List - Takes remaining height minus header and composer -->
	<div class="flex-1 min-h-0 overflow-hidden">
		<MessageList messages={data.messages as Message[]} user={$page.data.user} hasMore={true} />
	</div>

	<!-- Message Composer - Fixed height at bottom -->
	<div class="bg-background dark:bg-background">
		<RichMessageComposer  />
		<!--
		<MessageComposer />
		<ReplyBox />
		-->
	</div>
	
</div> 