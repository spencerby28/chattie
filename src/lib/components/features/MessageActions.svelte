<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { MessageSquare, Smile, MoreVertical } from 'lucide-svelte';
	import type { Message, User } from '$lib/types';
	import { getContext } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { messageStore } from '$lib/stores/messages';

	const dispatch = createEventDispatcher();
	export let message: Message;
	export let user: User;
	export let onDropdownOpenChange: (open: boolean) => void;
	const commonEmojis = ['👍', '❤️', '😂', '🎉', '🙏', '👀', '🔥', '✨'];

	async function handleEmojiSelect(messageId: string, emoji: string) {
		const channelId = message.channel_id;
		try {
			const response = await fetch(`/api/message/update`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
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
		dispatch('emojiSelect', { messageId, emoji, channelId });
		onDropdownOpenChange(false);
	}

	function handleReply(messageId: string) {
		dispatch('reply', { messageId });
		onDropdownOpenChange(false);
	}

	function handleCopy(messageId: string) {
		navigator.clipboard.writeText(message.content);
		dispatch('copy', { messageId });
	}

	async function handleEdit(messageId: string) {
		dispatch('edit', { messageId });
	}

	async function handleDelete(messageId: string) {
		const response = await fetch(`/api/message/delete`, {
			method: 'POST',
			body: JSON.stringify({ messageId, channelId: message.channel_id })
		});
		if (response.ok) {
			messageStore.deleteMessage(messageId);
		}
		dispatch('delete', { messageId });
	}

	function startChannelFromMessage(messageId: string) {
		dispatch('startChannel', { messageId });
	}
</script>

<div class="flex -inset-4">
	<DropdownMenu.Root onOpenChange={onDropdownOpenChange} closeOnOutsideClick={true}>
		<DropdownMenu.Trigger>
			<button class="p-1.5 hover:bg-gray-100 rounded-md" on:click={() => console.log('Emoji button clicked')}>
				<Smile class="w-5 h-5" />
			</button>
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="start">
			<div class="p-2 grid grid-cols-4 gap-2">
				{#each commonEmojis as emoji}
					<button class="hover:bg-gray-100 p-2 rounded text-lg transition-colors" on:click={() => handleEmojiSelect(message.$id, emoji)}>
						{emoji}
					</button>
				{/each}
			</div>
		</DropdownMenu.Content>
	</DropdownMenu.Root>

	<button class="p-1.5 hover:bg-gray-100 rounded-md" on:click={() => handleReply(message.$id)}>
		<MessageSquare class="w-5 h-5" />
	</button>

	<DropdownMenu.Root onOpenChange={onDropdownOpenChange}>
		<DropdownMenu.Trigger>
			<button class="p-1.5 hover:bg-gray-100 rounded-md">
				<MoreVertical class="w-5 h-5" />
			</button>
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="end">
			<DropdownMenu.Item on:click={() => handleCopy(message.$id)}>Copy message</DropdownMenu.Item>
			{#if message.sender_id === user.$id}
				<DropdownMenu.Item on:click={() => handleEdit(message.$id)}>Edit message</DropdownMenu.Item>
				<DropdownMenu.Separator />
				<DropdownMenu.Item on:click={() => handleDelete(message.$id)} class="text-red-600 focus:text-red-600">
					Delete message
				</DropdownMenu.Item>
			{/if}
			<DropdownMenu.Separator />
			<DropdownMenu.Item on:click={() => startChannelFromMessage(message.$id)}>
				Start Channel from Message
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
</div>
