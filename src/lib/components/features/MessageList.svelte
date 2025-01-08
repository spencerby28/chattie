<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import type { Message, User } from '$lib/types';
	import * as Popover from "$lib/components/ui/popover";
	import * as ContextMenu from "$lib/components/ui/context-menu";
	import { writable } from 'svelte/store';
	import MessageActions from './MessageActions.svelte';
	import { messageStore } from '$lib/stores/messages';
	import { page } from '$app/stores';
	import { replyBoxStore } from '$lib/stores/threads';
	
	interface SimpleMember {
		id: string;
		name: string;
	}

	export let messages: Message[] = [];
	export let user: User;

	// Get workspace members from page data
	$: memberData = ($page.data.workspace?.memberData || []) as SimpleMember[];
	
	// Helper function to get member name
	function getMemberName(userId: string): string {
		return memberData.find(m => m.id === userId)?.name || userId;
	}

	let container: HTMLDivElement;
	let expandedMessages: Set<string> = new Set();
	let showScrollButton = false;
	let isNearBottom = true;
	let previousMessagesLength = 0;
	let hoveredMessageId: string | null = null;
	let isDropdownOpen = false;
	let activeMessageId: string | null = null;

	// Create a store that updates every second
	const currentTime = writable(new Date());
	const timeInterval = setInterval(() => {
		currentTime.set(new Date());
	}, 1000);

	onMount(() => {
		scrollToBottom('auto');
		console.log('Initial messages:', messages);
		
		// Add scroll listener
		container?.addEventListener('scroll', handleScroll);
		return () => {
			container?.removeEventListener('scroll', handleScroll);
			clearInterval(timeInterval);
		};
	});

	afterUpdate(() => {
		// If messages were added (not just updated or removed)
		if (messages.length > previousMessagesLength) {
			if (isNearBottom) {
				scrollToBottom();
			}
		}
		previousMessagesLength = messages.length;
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

	function toggleMessageDetails(messageId: string) {
		if (expandedMessages.has(messageId)) {
			expandedMessages.delete(messageId);
		} else {
			expandedMessages.add(messageId);
		}
		expandedMessages = expandedMessages;
	}

	function getRelativeTime(timestamp: string): string {
		const messageTime = new Date(timestamp).getTime();
		const diffSeconds = Math.floor(($currentTime.getTime() - messageTime) / 1000);

		if (diffSeconds < 30) {
			return 'now';
		} else if (diffSeconds < 60) {
			return `${diffSeconds}s`;
		} else if (diffSeconds < 600) { // 10 minutes
			return `${Math.floor(diffSeconds / 60)}m`;
		} else {
			return new Date(timestamp).toLocaleTimeString();
		}
	}

	async function handleEmojiSelect(messageId: string, emoji: string, channelId: string) {
		try {
			const response = await fetch(`/api/message/update`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ messageId, emoji, channelId })
			});
			
			if (response.ok) {
				const data = await response.json();
				if (data.message) {
					messageStore.updateMessage(messageId, data.message);
				}
			}
		} catch (error) {
			console.error('Error updating reaction:', error);
		}
	}

	async function handleReactionClick(reaction: any, message: Message) {
		if (reaction.userIds.includes(user.$id)) {
			// If user already reacted, remove the reaction
			try {
				const response = await fetch(`/api/message/update`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ 
						messageId: message.$id, 
						emoji: reaction.emoji, 
						channelId: message.channel_id,
						remove: true 
					})
				});
				
				if (response.ok) {
					const data = await response.json();
					if (data.message) {
						messageStore.updateMessage(message.$id, data.message);
					}
				}
			} catch (error) {
				console.error('Error removing reaction:', error);
			}
		} else {
			// If user hasn't reacted, add the reaction
			await handleEmojiSelect(message.$id, reaction.emoji, message.channel_id);
		}
	}

	function handleReply(messageId: string, channelId: string) {
		replyBoxStore.set({
			open: true,
			messageId,
			channelId
		});
	}

	function handleCopy(messageId: string) {
		console.log('Copy message', messageId);
	}

	function handleEdit(messageId: string) {
		console.log('Edit message', messageId);
	}

	function handleDelete(messageId: string) {
		console.log('Delete message', messageId);
	}

	function handleDropdownOpenChange(open: boolean, messageId: string) {
		isDropdownOpen = open;
		activeMessageId = open ? messageId : null;
	}

	function handleMessageAction(event: CustomEvent) {
		const { type, detail } = event;
		
		switch (type) {
			case 'emojiSelect':
				// Already handled in MessageActions
				break;
			case 'edit':
				// Will be implemented when we add edit functionality
				break;
			case 'delete':
				// Already handled in MessageActions
				break;
			case 'reply':
				handleReply(detail.messageId, detail.channelId);
				break;
			case 'copy':
				// Already handled in MessageActions
				break;
			case 'startChannel':
				// Will be implemented when we add start channel functionality
				break;
		}
		console.log(`Message action: ${type}`, detail);
	}

	$: if (messages.length) {
		// Comment out or remove this block since we handle it in afterUpdate
	}
</script>

<div bind:this={container} class="h-full overflow-y-auto px-4">
	{#if showScrollButton}
		<!-- svelte-ignore a11y_consider_explicit_label -->
		<div class="fixed bottom-24 right-8 z-50">
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

	<div class="space-y-4 py-4">
		{#if !messages?.length}
			<div class="text-center text-gray-500 space-y-2 pt-12">
				<div class="text-6xl">😴</div>
				<div class="text-2xl">It's awfully quiet...</div>
			</div>
		{/if}

		{#each messages?.filter((m) => m?.$id) || [] as message (message.$id)}
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div 
				class="flex gap-3 group relative p-2 rounded-lg transition-colors duration-200"
				on:mouseenter={() => hoveredMessageId = message.$id}
				on:mouseleave={() => hoveredMessageId = null}
			>
				<div class="flex items-center">
					<img
						src={message.user?.avatar || '/images/avatar.png'}
						alt=""
						class="w-10 h-10 rounded-lg object-cover"
					/>
				</div>
				<div class="flex-1">
					<div class="flex flex-col">
						<span class="font-semibold">{message.sender_name}</span>
					</div>
					<p class="mt-1">{message.content}</p>

					{#if message.reactions && message.reactions.length > 0}
						<div class="flex flex-wrap gap-1 mt-1">
							<ContextMenu.Root>
								<ContextMenu.Trigger>
									<div class="flex flex-wrap gap-1">
										{#each message.reactions as reaction}
											<button 
												class="px-2 py-0.5 bg-accent/50 rounded text-sm hover:bg-accent transition-colors cursor-pointer {reaction.userIds?.includes(user.$id) ? 'bg-accent' : ''}"
												on:click={() => handleReactionClick(reaction, message)}
											>
												<span class="inline-flex items-center gap-1">
													{reaction.emoji}
													<span class="font-medium text-accent-foreground">{reaction.userIds?.length || 1}</span>
												</span>
											</button>
										{/each}
									</div>
								</ContextMenu.Trigger>
								<ContextMenu.Content class="w-48">
									{#each message.reactions as reaction}
										<div class="p-2 border-b border-accent last:border-0">
											<div class="flex items-center justify-between">
												<div class="flex items-center gap-2">
													<span class="text-lg">{reaction.emoji}</span>
													<span class="text-sm text-accent-foreground">{reaction.userIds?.length || 1}</span>
												</div>
												{#if reaction.userIds?.includes(user.$id)}
													<button 
														class="text-xs text-red-500 hover:text-red-700"
														on:click={() => handleReactionClick(reaction, message)}
													>
														Remove
													</button>
												{/if}
											</div>
											{#if reaction.userIds?.length}
												<div class="mt-1 text-sm text-accent-foreground">
													{#if reaction.userIds.includes(user.$id)}
														You
														{#if reaction.userIds.length > 1}
															, {reaction.userIds.filter(id => id !== user.$id).map(id => getMemberName(id)).join(', ')}
														{/if}
													{:else}
														{reaction.userIds.map(id => getMemberName(id)).join(', ')}
													{/if}
												</div>
											{/if}
										</div>
									{/each}
								</ContextMenu.Content>
							</ContextMenu.Root>
						</div>
					{/if}

					<!--DEBUG MESSAGE DETAILS
					<button
						class="text-sm text-accent-foreground mt-1 hover:text-accent"
						on:click={() => toggleMessageDetails(message.$id)}
					>
						{expandedMessages.has(message.$id) ? 'Hide Details' : 'Show Details'}
					</button>

					{#if expandedMessages.has(message.$id)}
						<pre class="mt-2 p-2 bg-accent rounded text-xs overflow-x-auto">
							{JSON.stringify(message, null, 2)}
						</pre>
					{/if}
					-->
				</div>

				<div class="absolute right-2 top-2 flex flex-col items-end gap-1">
					<div class="{isDropdownOpen && activeMessageId === message.$id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity hover:bg-accent rounded-lg">
						<MessageActions
							{message}
							{user}
							onDropdownOpenChange={(open) => handleDropdownOpenChange(open, message.$id)}
							on:emojiSelect={handleMessageAction}
							on:reply={handleMessageAction}
							on:copy={handleMessageAction}
							on:edit={handleMessageAction}
							on:delete={handleMessageAction}
							on:startChannel={handleMessageAction}
						/>
					</div>
					<div class="text-sm text-accent-foreground pr-2">
						{#if getRelativeTime(message.$createdAt) === new Date(message.$createdAt).toLocaleTimeString()}
							<span class="w-[80px] text-right inline-block">
								{getRelativeTime(message.$createdAt)}
							</span>
						{:else}
							<Popover.Root>
								<Popover.Trigger>
									<span class="w-[80px] text-right inline-block">
										{getRelativeTime(message.$createdAt)}
									</span>
								</Popover.Trigger>
								<Popover.Content class="p-2">
									{new Date(message.$createdAt).toLocaleString()}
								</Popover.Content>
							</Popover.Root>
						{/if}
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>
