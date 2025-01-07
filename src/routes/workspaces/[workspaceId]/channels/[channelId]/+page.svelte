<script lang="ts">
	import { page } from '$app/stores';
	import MessageList from '$lib/components/features/MessageList.svelte';
	import MessageComposer from '$lib/components/features/MessageComposer.svelte';
	import type { Message } from '$lib/types';
	import { messageStore } from '$lib/stores/messages';
	import type { Channel } from '$lib/types';
	import { channelStore } from '$lib/stores/channels';
	import ReplyBox from '$lib/components/features/ReplyBox.svelte';

	// Reset message store when page data changes
	$: if ($page.data.messages) {
		messageStore.set($page.data.messages);
	}

	$: currentChannel = $channelStore.find(channel => channel.$id === $page.params.channelId);
</script>

<div class="flex flex-col h-full">
	<!-- Channel Header -->
	<div class="p-4 border-b bg-white">
		<h1 class="text-xl font-semibold">#{currentChannel?.name || ''}</h1>
	</div>

	<!-- Message List - Takes remaining height minus header and composer -->
	<div class="flex-1 min-h-0 overflow-hidden">
		<MessageList messages={$messageStore} user={$page.data.user} />
	</div>

	<!-- Message Composer - Fixed height at bottom -->
	<div class="p-4 border-t bg-white">
		<MessageComposer />
		<ReplyBox />
	</div>
	
</div> 