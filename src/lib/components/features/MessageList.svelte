<script lang="ts">
	import { onMount, afterUpdate, tick } from 'svelte';
	import type { Message, SimpleMember } from '$lib/types';
	import { messageStore, getChannelMessages } from '$lib/stores/messages';
	import { page } from '$app/stores';
	import { replyBoxStore } from '$lib/stores/threads';
	import MessageComponent from '$lib/components/features/messages/MessageComponent.svelte';
	import { memberStore } from '$lib/stores/members';
	import { reactionsStore } from '$lib/stores/reactions';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	export let messages: Message[] = [];
	export let user: SimpleMember;

	// Derived reactive values
	$: members = $memberStore;
	$: currentChannelId = $page.params.channelId;
	$: channelMessages = getChannelMessages(currentChannelId);

	let container: HTMLDivElement;
	let showScrollButton = false;
	let isNearBottom = true;
	let previousMessagesLength = 0;
	let isLoading = false;
	let scrollPosition = 0;
	let totalMessagesLoaded = 0;
	let hasMoreMessages = true;
	let isScrollingToMessage = false;
	let isMounted = false;
	let initialScrollComplete = false;
	let shouldAutoScroll = true;

	// The message ID we want to highlight/scroll to
	let targetMessageId: string | null = null;
	// A "highlight pass" counter that we increment whenever we want to trigger a new highlight
	let highlightPass = 0;

	/**
	 * Reactive block: watch the URL's messageId param. If it changes (or remains the same),
	 * we increment "highlightPass," which re-triggers highlight logic in the target message.
	 */
	$: {
		const params = new URLSearchParams($page.url.search);
		const newId = params.get('messageId') || null;

		// If the new ID is non-null and we're mounted
		if (newId && isMounted) {
			shouldAutoScroll = false;
			// If it's truly different from the last ID, or if it's the same but we want to
			// re-run highlight, either way we can increment the pass.
			if (newId !== targetMessageId) {
				targetMessageId = newId;
				highlightPass++;
			} else {
				// For repeated searches to the same ID, also increment so it triggers highlight again
				highlightPass++;
			}

			// Attempt to scroll, possibly re-fetch older messages
			scrollToMessage(newId);

			// Optionally remove the messageId from the URL after 2.5 seconds
			setTimeout(() => {
				const updated = new URL(window.location.href);
				updated.searchParams.delete('messageId');
				goto(updated.toString(), { replaceState: true });
			}, 2500);
		}
	}

	onMount(() => {
		// Initialize the store with the initial messages
		messageStore.initializeForWorkspace(messages, true);
		totalMessagesLoaded = messages.length;

		// Set up scroll handlers only after mount
		container?.addEventListener('scroll', handleScroll);
		
		// Mark as mounted to enable scroll-related features
		isMounted = true;

		// Handle initial scroll position after a short delay to ensure DOM is ready
		setTimeout(async () => {
			const params = new URLSearchParams($page.url.search);
			const messageId = params.get('messageId');
			
			if (messageId) {
				shouldAutoScroll = false;
				await scrollToMessage(messageId);
			} else if (shouldAutoScroll) {
				scrollToBottom('auto');
			}
			initialScrollComplete = true;
		}, 100);

		return () => {
			container?.removeEventListener('scroll', handleScroll);
		};
	});

	/**
	 * Scroll to a message by ID, loading older pages as needed.
	 */
	async function scrollToMessage(messageId: string) {
		if (!messageId || !browser || !isMounted) return;
		isScrollingToMessage = true;

		let attempts = 0;
		let messageElement = document.getElementById(`message-${messageId}`);

		// While element is not found and we still have older messages to load
		while (!messageElement && hasMoreMessages) {
			if (attempts > 30) break; // Avoid infinite loop
			attempts++;

			await loadMoreMessages();
			await tick();

			messageElement = document.getElementById(`message-${messageId}`);
		}

		// If message was found, scroll to it
		if (messageElement) {
			// First scroll without smooth behavior to get close
			messageElement.scrollIntoView({ behavior: 'auto', block: 'center' });
			await tick();
			// Then apply smooth scroll for the final adjustment
			messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
		}

		isScrollingToMessage = false;
	}

	/**
	 * After Svelte re-renders, check if new messages were appended and auto-scroll if user is near bottom.
	 */
	afterUpdate(() => {
		if (!isMounted || !initialScrollComplete) return;

		const currentLength = $channelMessages.length;
		if (currentLength > previousMessagesLength) {
			if (!isScrollingToMessage && shouldAutoScroll) {
				if (isNearBottom) {
					scrollToBottom();
				} else if (scrollPosition > 0) {
					// Maintain scroll offset after new messages
					requestAnimationFrame(() => {
						if (container) {
							container.scrollTop = container.scrollHeight - scrollPosition;
						}
					});
				}
			}
		}
		previousMessagesLength = currentLength;
	});

	function handleScroll() {
		if (!container || !isMounted) return;

		const scrollTop = container.scrollTop;
		const scrollHeight = container.scrollHeight;
		const clientHeight = container.clientHeight;
		const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

		isNearBottom = distanceFromBottom < 100;
		showScrollButton = !isNearBottom;

		// Re-enable auto-scroll when user manually scrolls to bottom
		if (isNearBottom) {
			shouldAutoScroll = true;
		}

		// Load older messages if near the top
		if (scrollTop < 1000 && !isLoading && hasMoreMessages) {
			scrollPosition = scrollHeight - scrollTop;
			loadMoreMessages();
		}
	}

	/**
	 * Load older messages from the server for the current channel.
	 */
	async function loadMoreMessages() {
		if (isLoading || !isMounted) return;
		isLoading = true;

		try {
			const resp = await fetch('/api/message/load', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					channelId: currentChannelId,
					offset: totalMessagesLoaded
				})
			});
			if (!resp.ok) throw new Error('Failed to load more messages');
			const data = await resp.json();
			if (data.error) throw new Error(data.error);

			if (data.messages.length < 50) {
				// If fewer than 50 loaded, assume no more messages
				hasMoreMessages = false;
			}

			messageStore.addMessages(data.messages);
			totalMessagesLoaded += data.messages.length;
		} catch (error) {
			console.error('Error loading more messages:', error);
		} finally {
			isLoading = false;
		}
	}

	function scrollToBottom(behavior: ScrollBehavior = 'smooth') {
		if (container && isMounted) {
			container.scrollTo({ top: container.scrollHeight, behavior });
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

<!-- Container for scrolling -->
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

		{#each $channelMessages?.filter((m) => m?.$id) || [] as msg (msg.$id)}
			<div
				id="message-{msg.$id}"
				class="relative overflow-visible"
			>
				<MessageComponent
					message={msg}
					user={user}
					memberData={members}
					reactions={$reactionsStore[msg.$id] || []}
					highlightVersion={msg.$id === targetMessageId ? highlightPass : undefined}
					on:messageAction={handleMessageAction}
				/>
			</div>
		{/each}
	</div>

	{#if showScrollButton}
		<div class="fixed bottom-48 right-8 z-50">
			<button
				class="bg-primary text-primary-foreground rounded-full p-2 shadow-lg hover:bg-primary/90 transition"
				on:click|stopPropagation={() => {
					shouldAutoScroll = true;
					scrollToBottom();
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 14l-7 7m0 0l-7-7m7 7V3"
					/>
				</svg>
			</button>
		</div>
	{/if}
</div>
