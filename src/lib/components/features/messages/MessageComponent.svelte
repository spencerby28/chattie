<script lang="ts">
	import type { Message, SimpleMember, StandardizedReaction } from '$lib/types';
	import * as Popover from "$lib/components/ui/popover";
	import * as ContextMenu from "$lib/components/ui/context-menu";
	import MessageActions from '../MessageActions.svelte';
	import Avatar from '$lib/components/ui/avatar/Avatar.svelte';

	import { createEventDispatcher } from 'svelte';
	import { page } from '$app/stores';
	import { avatarStore } from '$lib/stores/avatars';
	import { reactionsStore } from '$lib/stores/reactions';
	import { MessageSquare, Download } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
	import { Client, Storage } from 'appwrite';
	import { PUBLIC_APPWRITE_ENDPOINT, PUBLIC_APPWRITE_PROJECT } from '$env/static/public';

	import markdownit from 'markdown-it';

	export let message: Message;
	export let user: SimpleMember;
	export let memberData: SimpleMember[] = [];
	export let reactions: StandardizedReaction[] = [];
	
	// highlightVersion: a numeric counter that increments each time
	// the parent wants to highlight this message again.
	export let highlightVersion: number | undefined;

	let isHighlighted = false;
	let hoveredMessageId: string | null = null;
	let isDropdownOpen = false;
	let activeMessageId: string | null = null;

	const dispatch = createEventDispatcher();

	// For the reaction store
	$: messageReactions = $reactionsStore[message.$id] || [];
	$: currentReactions = messageReactions.length > 0 ? messageReactions : reactions;

	// Setup Appwrite client if needed
	const workspaceId = message.workspace_id;
	const appwrite = message.type === 'dm'
		? createBrowserClient()
		: (() => {
			const client = new Client()
				.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
				.setProject(PUBLIC_APPWRITE_PROJECT);
			return { storage: new Storage(client) };
		})();

	// If the message is a file, create preview/download URLs
	$: messageSender = memberData.find((m) => m.id === message.sender_id);
	$: filePreviewUrl =
		message.sender_type === 'file'
			? appwrite.storage.getFileView(workspaceId, message.$id).toString()
			: null;

	/**
	 * When highlightVersion changes (even if it's the same messageId),
	 * we trigger the highlight again for a fresh glow animation.
	 */
	$: if (highlightVersion !== undefined) {
		// Each time highlightVersion is updated, set isHighlighted = true
		isHighlighted = true;
		// Then fade highlight after a short delay
		setTimeout(() => {
			isHighlighted = false;
		}, 2000);
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

	function getMemberName(userId: string): string {
		return memberData.find((m) => m.id === userId)?.name || userId;
	}

	function getRelativeTime(timestamp: string): string {
		const messageTime = new Date(timestamp);
		const now = new Date();
		const diffSeconds = Math.floor((now.getTime() - messageTime.getTime()) / 1000);
		const diffDays = Math.floor(diffSeconds / (24 * 60 * 60));

		const isToday = messageTime.toDateString() === now.toDateString();
		const isYesterday =
			new Date(now.setDate(now.getDate() - 1)).toDateString() ===
			messageTime.toDateString();

		if (diffSeconds < 30) return 'now';
		if (diffSeconds < 60) return `${diffSeconds}s`;
		if (diffSeconds < 600) return `${Math.floor(diffSeconds / 60)}m`;
		if (isToday) {
			return messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		} else if (isYesterday) {
			return 'Yesterday';
		} else if (diffDays < 7) {
			return messageTime.toLocaleDateString([], { weekday: 'long' });
		} else {
			return messageTime.toLocaleDateString([], {
				month: 'numeric',
				day: 'numeric',
				year: '2-digit'
			});
		}
	}

	const md = markdownit({
		html: true,
		linkify: true,
		typographer: false,
		breaks: true
	}).enable(['list'])

	function processContent(content: string) {
		// Ensure proper list formatting by adding newlines before lists if needed
		return content.replace(/^(\d+\.)/gm, '\n$1')
					 .replace(/\*\*/g, '_'); // Convert ** to _ for emphasis
	}

	// Function to determine if content is HTML
	function isHTML(str: string) {
		const doc = new DOMParser().parseFromString(str, 'text/html');
		return Array.from(doc.body.childNodes).some(node => node.nodeType === 1);
	}

	// Function to render content based on type
	function renderContent(content: string) {
		if (!content) return '';
		
		if (isHTML(content)) {
			return content;
		} else {
			return md.render(processContent(content));
		}
	}
</script>
<!-- Markup -->
 <!--svelte-ignore a11y-no-static-element-interactions-->
 
<div
	class="flex gap-3 group relative p-2 rounded-lg transition-colors duration-200 overflow-visible {isHighlighted ? 'highlight-message' : ''}"
	on:mouseenter={() => (hoveredMessageId = message.$id)}
	on:mouseleave={() => (hoveredMessageId = null)}
>
	<div class="absolute inset-0 group-hover:bg-gradient-to-r group-hover:from-blue-400 group-hover:to-purple-600 opacity-0 group-hover:opacity-40 rounded-lg transition-opacity duration-200"></div>
	
	<!-- Avatar -->
	<div class="flex-shrink-0 pt-0.5 relative z-[1]">
		<Avatar
			src={messageSender?.avatarId ? avatarStore.getAvatarUrl(messageSender.avatarId) : undefined}
			fallback={message.sender_name?.[0]?.toUpperCase() || '?'}
			name={message.sender_name || 'Unknown'}
			size="lg"
		/>
	</div>

	<!-- Content -->
	<div class="flex-1 relative z-[1] pr-[100px]">
		<div class="flex flex-col">
			<span class="font-semibold">{message.sender_name}</span>
		</div>
		<!-- If file -->
		{#if message.sender_type === 'file'}
			<div class="mt-2">
				<img
					src={filePreviewUrl}
					alt="File preview"
					class="max-w-[300px] rounded-lg shadow-md"
				/>
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
		{:else if isHTML(message.content)}
			<div class="mt-1 prose prose-sm max-w-none [&_.mention]:text-blue-500 [&_.mention]:bg-blue-500/10 [&_.mention]:rounded [&_.mention]:px-1">{@html message.content}</div>
		{:else}
			<div class="mt-1  rendered-content">
				{@html renderContent(message.content)}
			</div>
		{/if}

		<!-- Reactions -->
		{#if currentReactions.length > 0}
			<div class="flex flex-wrap gap-1 mt-1">
				<ContextMenu.Root>
					<ContextMenu.Trigger>
						<div class="flex flex-wrap gap-1">
							{#each currentReactions as reaction}
								{#if reaction.userIds?.length > 0}
									<button
										class="px-2 py-0.5 bg-accent/50 rounded text-sm hover:bg-accent transition-colors cursor-pointer {reaction.userIds?.includes(user.id) ? 'bg-accent' : ''}"
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

		<!-- Thread replies -->
		{#if message.thread_id && message.thread_count !== undefined && message.thread_count > 0}
			<button
				on:click={() => goto(`/workspaces/${message.workspace_id}/channels/${message.thread_id}?thread=true`)}
				class="inline-flex items-center gap-2 mt-2 px-2 py-1 text-sm text-blue-500 hover:text-foreground hover:bg-accent rounded-md transition-colors"
			>
				<MessageSquare class="w-4 h-4" />
				<span>
					{message.thread_count} {message.thread_count === 1 ? 'reply' : 'replies'}
				</span>
			</button>
		{/if}
	</div>

	<!-- Right-side actions -->
	<div class="absolute right-2 top-2 flex flex-col items-end gap-1 z-[1]">
		<!-- Message actions dropdown -->
		<div
			class="{isDropdownOpen && activeMessageId === message.$id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity hover:bg-accent rounded-lg"
		>
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

		<!-- Timestamp -->
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
	/* Highlight animation */
	.highlight-message {
		position: relative;
		z-index: 0;
		overflow: visible;
	}

	.highlight-message::before {
		content: '';
		position: absolute;
		inset: -2px;
		background: linear-gradient(to right, rgb(96, 165, 250), rgb(192, 132, 252));
		opacity: 0;
		border-radius: 8px;
		z-index: -1;
		animation: glow 2s ease-out;
		pointer-events: none;
	}

	@keyframes glow {
		0%, 50% {
			opacity: 0.5;
			box-shadow: 0 0 20px rgba(96, 165, 250, 0.5),
			            0 0 40px rgba(192, 132, 252, 0.3);
		}
		100% {
			opacity: 0;
			box-shadow: none;
		}
	}

	/* Mentions inside rendered HTML */
	:global(.prose .mention) {
		color: rgb(59 130 246);
		cursor: pointer;
		display: inline-block;
		background: rgba(59, 130, 246, 0.1);
		border-radius: 4px;
		padding: 0 4px;
	}

	/* Add styles for markdown content */
	:global(.prose) {
		@apply text-foreground;
	}
	:global(.prose a) {
		@apply text-blue-500 hover:text-blue-600 no-underline;
	}
	:global(.prose code) {
		@apply bg-accent/50 px-1 py-0.5 rounded text-sm;
	}
	:global(.prose pre) {
		@apply bg-accent/50 p-3 rounded-lg;
	}
	:global(.prose blockquote) {
		@apply border-l-4 border-accent pl-4 italic;
	}
	:global(.prose ul) {
		@apply list-disc list-inside;
	}
	:global(.prose ol) {
		@apply list-decimal list-inside;
	}



    /* Add proper list styling */
    :global(.rendered-content ol) {
        list-style-type: decimal !important;
        padding-left: 2rem !important;
        margin: 0.5rem 0 !important;
    }
    :global(.rendered-content li) {
        margin: 0.25rem 0 !important;
    }
    :global(.rendered-content p) {
        margin: 0.5rem 0 !important;
    }

</style> 
