<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import type { Message, SimpleMember } from '$lib/types';
	import { messageStore, getChannelMessages } from '$lib/stores/messages';
	import { page } from '$app/stores';
	import { replyBoxStore } from '$lib/stores/threads';
	import MessageComponent from '$lib/components/features/messages/MessageComponent.svelte';
	import { memberStore } from '$lib/stores/members';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
	import { Query } from 'appwrite';
	import { reactionsStore } from '$lib/stores/reactions';

	export let messages: Message[] = [];
	export let user: SimpleMember;

	// Get workspace members from page data
	$: members = $memberStore;

	// Create derived store for current channel's messages
	$: currentChannelId = $page.params.channelId;
	$: channelMessages = getChannelMessages(currentChannelId);

	let container: HTMLDivElement;
	let showScrollButton = false;
	let isNearBottom = true;
	let previousMessagesLength = 0;

	$: messageReactions = $reactionsStore;

	onMount(async () => {
		scrollToBottom('auto');
		
		// Add scroll listener
		container?.addEventListener('scroll', handleScroll);

		return () => {
			container?.removeEventListener('scroll', handleScroll);
		};
	});

	afterUpdate(() => {
		// If messages were added (not just updated or removed)
		if ($channelMessages.length > previousMessagesLength) {
			if (isNearBottom) {
				scrollToBottom();
			}
		}
		previousMessagesLength = $channelMessages.length;
	});

	function handleScroll() {
		if (!container) return;
		
		const threshold = 100; // pixels from bottom
		const position = container.scrollHeight - container.scrollTop - container.clientHeight;
		isNearBottom = position < threshold;
		showScrollButton = !isNearBottom;
	}

	function scrollToBottom(behavior: ScrollBehavior = 'smooth') {
		if (container) {
			const targetScroll = container.scrollHeight;
			container.scrollTo({
				top: targetScroll,
				behavior
			});
		}
	}

	function handleMessageAction(event: CustomEvent) {
		const { type, detail } = event.detail;
		
		switch (type) {
			case 'reply':
				replyBoxStore.set({
					open: true,
					messageId: detail.messageId,
					channelId: detail.channelId
				});
				break;
			default:
				console.log(`Message action: ${type}`, detail);
		}
	}
</script>

<div bind:this={container} class="h-full overflow-y-auto px-4">
	{#if showScrollButton}
		<!-- svelte-ignore a11y_consider_explicit_label -->
		<div class="fixed bottom-48 right-8 z-50">
			<button
				class="bg-primary text-primary-foreground rounded-full p-2 shadow-lg hover:bg-primary/90 transition-all"
				on:click|stopPropagation={() => scrollToBottom()}
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
				</svg>
			</button>
		</div>
	{/if}

	<div class="space-y-4 py-4 scrollbar-none">
		{#if !$channelMessages?.length}
			<div class="text-center text-gray-500 space-y-2 pt-12">
				<div class="text-6xl">😴</div>
				<div class="text-2xl">It's awfully quiet...</div>
			</div>
		{/if}

		{#each $channelMessages?.filter((m) => m?.$id) || [] as message (message.$id)}
			<div class="relative">
				<MessageComponent
					{message}
					{user}
					memberData={members}
					reactions={messageReactions[message.$id] || []}
					on:messageAction={handleMessageAction}
				/>
			</div>
		{/each}
	</div>
</div>
