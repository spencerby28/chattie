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
	let isLoading = false;
	let scrollPosition = 0;
	let totalMessagesLoaded = 0;

	$: messageReactions = $reactionsStore;

	onMount(() => {
		// Initialize the store with the initial messages
		messageStore.initializeForWorkspace(messages, true);
		totalMessagesLoaded = messages.length;
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
			console.log('Messages updated:', {
				previous: previousMessagesLength,
				current: $channelMessages.length,
				total: totalMessagesLoaded,
				isNearBottom,
				scrollPosition
			});

			if (isNearBottom) {
				scrollToBottom();
			} else if (scrollPosition > 0) {
				// Restore scroll position after loading more messages
				requestAnimationFrame(() => {
					if (container) {
						console.log('Restoring scroll position:', {
							scrollPosition,
							scrollHeight: container.scrollHeight
						});
						container.scrollTop = container.scrollHeight - scrollPosition;
					}
				});
			}
		}
		previousMessagesLength = $channelMessages.length;
	});

	function handleScroll() {
		if (!container) return;
		
		const scrollTop = container.scrollTop;
		const scrollHeight = container.scrollHeight;
		const clientHeight = container.clientHeight;
		const position = scrollHeight - scrollTop - clientHeight;



		isNearBottom = position < 100;
		showScrollButton = !isNearBottom;

		// Load more messages when scrolling near top (within 1000px of top)
		if (scrollTop < 1000 && !isLoading) {
			console.log('Triggering load more messages - near top');
			// Save current scroll position
			scrollPosition = scrollHeight - scrollTop;
			loadMoreMessages();
		}
	}

	async function loadMoreMessages() {
		if (isLoading) {
			console.log('Load more messages blocked - already loading');
			return;
		}
		
		console.log('Loading more messages:', {
			offset: totalMessagesLoaded,
			currentLength: $channelMessages.length,
			scrollPosition
		});
		
		isLoading = true;
		
		try {
			const response = await fetch('/api/message/load', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					channelId: currentChannelId,
					offset: totalMessagesLoaded
				})
			});

			if (!response.ok) {
				throw new Error('Failed to load messages');
			}

			const data = await response.json();
			
			if (data.error) {
				throw new Error(data.error);
			}

			// If no messages returned, we've reached the end
			if (!data.messages.length) {
				console.log('No more messages to load');
				return;
			}

			messageStore.addMessages(data.messages);
			totalMessagesLoaded += data.messages.length;
			
			console.log('Messages loaded:', {
				newMessages: data.messages.length,
				totalLoaded: totalMessagesLoaded,
					total: data.total
			});
			
		} catch (error) {
			console.error('Error loading more messages:', error);
		} finally {
			isLoading = false;
		}
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
	{#if isLoading}
		<div class="flex justify-center py-4">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
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
</div>
