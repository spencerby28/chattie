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
		messageStore.initializeForWorkspace(data.messages);
	}

	$: currentChannel = $channelStore.channels.find(channel => channel.$id === $page.params.channelId);
	$: members = $memberStore;

	$: channelTitle = (() => {
		if (!currentChannel) return '';
		if (currentChannel.type === 'thread') {
			return data.messages?.[0]?.content || currentChannel.name;
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
	$: console.log( 'channelTitle', currentChannel)
</script>

<div class="flex flex-col h-full bg-white dark:bg-gray-950">
	<!-- Channel Header -->
	<div class="p-4 border-b bg-white dark:bg-gray-950">
		<h1 class="text-xl font-semibold">
			{#if currentChannel?.type === 'dm'}
				{channelTitle}
			{:else}
				#{channelTitle}
			{/if}
		</h1>
	</div>

	<!-- Message List - Takes remaining height minus header and composer -->
	<div class="flex-1 min-h-0 overflow-hidden">
		<MessageList messages={data.messages} user={$page.data.user} />
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