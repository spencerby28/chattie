<script lang="ts">
	import type { Message, SimpleMember } from '$lib/types';
	import * as Popover from "$lib/components/ui/popover";
	import * as ContextMenu from "$lib/components/ui/context-menu";
	import MessageActions from '../MessageActions.svelte';
	import { createEventDispatcher } from 'svelte';
	import { page } from '$app/stores';
	import { messageStore } from '$lib/stores/messages';

	export let message: Message;
	export let user: SimpleMember;
	export let memberData: SimpleMember[] = [];

	const dispatch = createEventDispatcher();

	let hoveredMessageId: string | null = null;
	let isDropdownOpen = false;
	let activeMessageId: string | null = null;

	// Helper function to get member name
	function getMemberName(userId: string): string {
		return memberData.find(m => m.id === userId)?.name || userId;
	}

	function getRelativeTime(timestamp: string): string {
		const messageTime = new Date(timestamp).getTime();
		const now = new Date().getTime();
		const diffSeconds = Math.floor((now - messageTime) / 1000);

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

	async function handleReactionClick(reaction: any) {
		if (reaction.userIds.includes(user.id)) {
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

	function handleDropdownOpenChange(open: boolean, messageId: string) {
		isDropdownOpen = open;
		activeMessageId = open ? messageId : null;
	}

	function handleMessageAction(event: CustomEvent) {
		dispatch('messageAction', {
			type: event.type,
			detail: event.detail
		});
	}
</script>

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
		{#if message.content.startsWith('<')}
			<div class="mt-1 prose prose-sm max-w-none [&_.mention]:text-blue-500 [&_.mention]:bg-blue-500/10 [&_.mention]:rounded [&_.mention]:px-1">{@html message.content}</div>
		{:else}
			<p class="mt-1">{message.content}</p>
		{/if}

		{#if message.reactions && message.reactions.length > 0}
			<div class="flex flex-wrap gap-1 mt-1">
				<ContextMenu.Root>
					<ContextMenu.Trigger>
						<div class="flex flex-wrap gap-1">
							{#each message.reactions as reaction}
								<button 
									class="px-2 py-0.5 bg-accent/50 rounded text-sm hover:bg-accent transition-colors cursor-pointer {reaction.userIds?.includes(user.id) ? 'bg-accent' : ''}"
									on:click={() => handleReactionClick(reaction)}
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
									{#if reaction.userIds?.includes(user.id)}
										<button 
											class="text-xs text-red-500 hover:text-red-700"
											on:click={() => handleReactionClick(reaction)}
										>
											Remove
										</button>
									{/if}
								</div>
								{#if reaction.userIds?.length}
									<div class="mt-1 text-sm text-accent-foreground">
										{#if reaction.userIds.includes(user.id)}
											You
											{#if reaction.userIds.length > 1}
												, {reaction.userIds.filter(id => id !== user.id).map(id => getMemberName(id)).join(', ')}
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

<style>
	:global(.prose .mention) {
		color: rgb(59 130 246);
		cursor: pointer;
		display: inline-block;
		background: rgba(59, 130, 246, 0.1);
		border-radius: 4px;
		padding: 0 4px;
	}
</style> 