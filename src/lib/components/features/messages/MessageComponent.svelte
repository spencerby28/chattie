<script lang="ts">
	import type { Message, SimpleMember, Reaction } from '$lib/types';
	import * as Popover from "$lib/components/ui/popover";
	import * as ContextMenu from "$lib/components/ui/context-menu";
	import MessageActions from '../MessageActions.svelte';
	import { createEventDispatcher } from 'svelte';
	import { page } from '$app/stores';
	import { messageStore } from '$lib/stores/messages';
	import Avatar from '$lib/components/ui/avatar/Avatar.svelte';
	import { avatarStore } from '$lib/stores/avatars';
	import { reactionsStore } from '$lib/stores/reactions';
	import { MessageSquare, Download } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
	import { Client, Storage } from 'appwrite';
	import { PUBLIC_APPWRITE_ENDPOINT, PUBLIC_APPWRITE_PROJECT } from '$env/static/public';
	export let message: Message;
	export let user: SimpleMember;
	export let memberData: SimpleMember[] = [];
	export let reactions: Reaction[] = [];

	const dispatch = createEventDispatcher();

	let hoveredMessageId: string | null = null;
	let isDropdownOpen = false;
	let activeMessageId: string | null = null;

	// Get workspace ID from page params
	const workspaceId = message.workspace_id;

	// Initialize Appwrite client based on message type
	const appwrite = message.type === 'dm' ? 
		createBrowserClient() :
		(() => {
			const client = new Client()
				.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
				.setProject(PUBLIC_APPWRITE_PROJECT);
			return {
				storage: new Storage(client)
			};
		})();

	// Subscribe to reactions store for this message
	$: messageReactions = $reactionsStore[message.$id] || [];
	$: currentReactions = messageReactions.length > 0 ? messageReactions : reactions;

	// Helper function to get member name
	function getMemberName(userId: string): string {
		return memberData.find(m => m.id === userId)?.name || userId;
	}

	function getRelativeTime(timestamp: string): string {
		const messageTime = new Date(timestamp);
		const now = new Date();
		const diffSeconds = Math.floor((now.getTime() - messageTime.getTime()) / 1000);
		const diffDays = Math.floor(diffSeconds / (24 * 60 * 60));
		const isToday = messageTime.toDateString() === now.toDateString();
		const isYesterday = new Date(now.setDate(now.getDate() - 1)).toDateString() === messageTime.toDateString();

		if (diffSeconds < 30) {
			return 'now';
		} else if (diffSeconds < 60) {
			return `${diffSeconds}s`;
		} else if (diffSeconds < 600) { // 10 minutes
			return `${Math.floor(diffSeconds / 60)}m`;
		} else if (isToday) {
			return messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		} else if (isYesterday) {
			return 'Yesterday';
		} else if (diffDays < 7) {
			return messageTime.toLocaleDateString([], { weekday: 'long' });
		} else {
			return messageTime.toLocaleDateString([], { month: 'numeric', day: 'numeric', year: '2-digit' });
		}
	}

	async function handleReactionClick(reaction: any) {
		if (!reaction.$id || !reaction.userIds?.includes(user.id)) return;
		
		try {
			await fetch(`/api/reactions/update`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ reactionId: reaction.$id })
			});
		} catch (error) {
			console.error('Error removing reaction:', error);
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

	async function downloadFile() {
		if (message.sender_type === 'file') {
			const fileId = message.$id;
			const downloadUrl = appwrite.storage.getFileDownload(workspaceId, fileId);
			window.open(downloadUrl.toString(), '_blank');
		}
	}

	// Find the message sender's data from memberData
	$: messageSender = memberData.find(m => m.id === message.sender_id);

	$: filePreviewUrl = message.sender_type === 'file' ? 
		appwrite.storage.getFileView(workspaceId, message.$id).toString() : null;
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div 
	class="flex gap-3 group relative p-2 rounded-lg transition-colors duration-200"
	on:mouseenter={() => hoveredMessageId = message.$id}
	on:mouseleave={() => hoveredMessageId = null}
>
	<div class="absolute inset-0 group-hover:bg-gradient-to-r group-hover:from-blue-400 group-hover:to-purple-600 opacity-0 group-hover:opacity-40 rounded-lg transition-opacity duration-200"></div>
	<div class="flex-shrink-0 pt-0.5 relative z-[1]">
		<Avatar
			src={messageSender?.avatarId ? avatarStore.getAvatarUrl(messageSender.avatarId) : undefined}
			fallback={message.sender_name?.[0]?.toUpperCase() || '?'}
			name={message.sender_name || 'Unknown'}
			size="lg"
		/>
	</div>
	<div class="flex-1 relative z-[1]">
		<div class="flex flex-col">
			<span class="font-semibold">{message.sender_name}</span>
		</div>
		{#if message.sender_type === 'file'}
			<div class="mt-2">
				<img src={filePreviewUrl} alt="File preview" class="max-w-[300px] rounded-lg shadow-md" />
				<div class="mt-4">
					<button 
						on:click={downloadFile}
						class="flex items-center text-sm gap-2 px-2 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors w-fit"
					>
						<Download class="w-3 h-3" />
						<span>Download</span>
					</button>
				</div>
			</div>
		{:else if message.content.startsWith('<')}
			<div class="mt-1 prose prose-sm max-w-none [&_.mention]:text-blue-500 [&_.mention]:bg-blue-500/10 [&_.mention]:rounded [&_.mention]:px-1">{@html message.content}</div>
		{:else}
			<p class="mt-1">{message.content}</p>
		{/if}

		{#if currentReactions.length > 0}
			<div class="flex flex-wrap gap-1 mt-1">
				<ContextMenu.Root>
					<ContextMenu.Trigger>
						<div class="flex flex-wrap gap-1">
							{#each currentReactions as reaction}
								{#if reaction.userIds?.length > 0}
									<button 
										class={`px-2 py-0.5 bg-accent/50 rounded text-sm hover:bg-accent transition-colors cursor-pointer ${reaction.userIds?.includes(user.id) ? 'bg-accent' : ''}`}
										on:click={() => handleReactionClick(reaction)}
									>
										<span class="inline-flex items-center gap-1">
											{reaction.emoji}
											{#if reaction.userIds?.length > 1}
												<span class="font-medium text-accent-foreground">{reaction.userIds?.length}</span>
											{/if}
										</span>
									</button>
								{/if}
							{/each}
						</div>
					</ContextMenu.Trigger>
					<ContextMenu.Content class="w-48">
						{#each currentReactions as reaction}
							<div class="p-2 border-b border-accent last:border-0">
								<div class="flex items-center justify-between">
									<div class="flex items-center gap-2">
										<span class="text-lg">{reaction.emoji}</span>
										<span class="text-sm text-accent-foreground">{reaction.userIds?.length}</span>
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
												, {reaction.userIds.filter((id: string) => id !== user.id).map((id: string) => getMemberName(id)).join(', ')}
											{/if}
										{:else}
											{reaction.userIds.map((id: string) => getMemberName(id)).join(', ')}
										{/if}
									</div>
								{/if}
							</div>
						{/each}
					</ContextMenu.Content>
				</ContextMenu.Root>
			</div>
		{/if}

		{#if message.thread_id && message.thread_count !== undefined && message.thread_count > 0}
		
			<button 
				on:click={() => goto(`/workspaces/${message.workspace_id}/channels/${message.thread_id}?thread=true`)}
				class="inline-flex items-center gap-2 mt-2 px-2 py-1 text-sm text-blue-500 hover:text-foreground hover:bg-accent rounded-md transition-colors"
			>
				<MessageSquare class="w-4 h-4" />
				<span class= ''>
					{message.thread_count} {message.thread_count === 1 ? 'reply' : 'replies'}
				</span>
			</button>
		
		{/if}
	</div>

	<div class="absolute right-2 top-2 flex flex-col items-end gap-1 z-[1]">
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
			{#if getRelativeTime(message.$createdAt) === new Date(message.$createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
				<span class="w-[90px] text-right inline-block">
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