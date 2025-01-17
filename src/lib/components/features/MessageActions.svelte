<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { MessageSquare, Smile, MoreVertical, Speaker, Loader2 } from 'lucide-svelte';
	import type { Message, SimpleMember, Reaction } from '$lib/types';
	
	import { createEventDispatcher } from 'svelte';
	import { announceFeature } from '$lib/utils/toast';
	import { messageStore } from '$lib/stores/messages';
	import { RealtimeService } from '$lib/services/realtime';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { channelStore } from '$lib/stores/channels';
	import { reactionsStore } from '$lib/stores/reactions';

	const dispatch = createEventDispatcher();
	export let message: Message;
	export let user: any;
	export let onDropdownOpenChange: (open: boolean) => void;
	const commonEmojis = ['👍', '❤️', '😂', '🎉', '🙏', '👀', '🔥', '✨'];

	// Get realtime service instance
	const realtime = RealtimeService.getInstance();

	// Subscribe to reactions for this message
	$: messageReactions = $reactionsStore[message.$id] || [];

	// Audio playback state
	let loadingVoiceId: string | null = null;
	let playingAudio: { element: HTMLAudioElement; voiceId: string } | null = null;

	async function playTextToSpeech(voiceId: string, text: string) {
		// If already playing this audio, stop it
		if (playingAudio?.voiceId === voiceId) {
			playingAudio.element.pause();
			playingAudio.element.currentTime = 0;
			playingAudio = null;
			return;
		}

		// Stop any other playing audio
		if (playingAudio) {
			playingAudio.element.pause();
			playingAudio.element.currentTime = 0;
			playingAudio = null;
		}

		if (loadingVoiceId) return;
		loadingVoiceId = voiceId;
		
		try {
			const response = await fetch('/api/speech', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ voiceId, text })
			});

			if (!response.ok) throw new Error('Failed to convert text to speech');

			const { audio } = await response.json();
			const audioElement = new Audio(`data:audio/mp3;base64,${audio}`);
			
			audioElement.addEventListener('ended', () => {
				playingAudio = null;
			});

			await audioElement.play();
			playingAudio = { element: audioElement, voiceId };
		} catch (error) {
			console.error('Text-to-speech error:', error);
			toast.error('Failed to play audio');
		} finally {
			loadingVoiceId = null;
		}
	}

	async function handleEmojiSelect(messageId: string, emoji: string) {
		const channelId = message.channel_id;
		
		// Find reaction with matching emoji and check if user's ID is in userIds array
		const existingReaction = messageReactions.find(reaction => 
			reaction.emoji === emoji && 
			reaction.userIds?.includes(user.$id)
		);
		
		try {
			if (existingReaction?.reactionIds?.[user.$id]) {
				// User has already reacted - remove it using the stored reaction ID
				await fetch(`/api/reactions/update`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ reactionId: existingReaction.reactionIds[user.$id] })
				});
			} else {
				// User hasn't reacted - add new reaction
				await fetch(`/api/reactions/create`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ messageId, emoji, channelId })
				});
			}
		} catch (error) {
			console.error('Error handling reaction:', error);
			toast.error('Failed to update reaction');
		}
		
		onDropdownOpenChange(false);
	}

	// Helper to check if user has reacted with an emoji
	function hasUserReacted(emoji: string): boolean {
		return messageReactions.some(r => 
			r.emoji === emoji && r.userIds?.includes(user.$id)
		);
	}

	async function handleReply(messageId: string) {
		try {
			// If message already has a thread, just navigate to it
			if (message.thread_id) {
				await goto(`/workspaces/${message.workspace_id}/channels/${message.thread_id}?thread=true`);
				return;
			}

			// Create thread channel and initial message
			const response = await fetch('/api/thread/add', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					messageId,
					workspaceId: message.workspace_id,
					content: message.content
				})
			});

			if (!response.ok) {
				throw new Error('Failed to create thread');
			}

			const { channel } = await response.json();
			
			// Reinitialize realtime to get new permissions
			await realtime.reinitialize();
			console.log('realtime reinitialized')
			console.log('channel', channel)

			// Add channel to store
			channelStore.addChannel(channel);

			// Navigate to the new thread channel
			await goto(`/workspaces/${message.workspace_id}/channels/${channel.$id}?thread=true`);
		} catch (error) {
			console.error('Error creating thread:', error);
			toast.error('Failed to create thread');
		}
	}

	function handleCopy(messageId: string) {
		navigator.clipboard.writeText(message.content);
		dispatch('copy', { messageId });
	}

	async function handleEdit(messageId: string) {
		dispatch('edit', { messageId });
		announceFeature('Edit messages');
	}

	async function handleDelete(messageId: string) {
		const response = await fetch(`/api/message/update`, {
			method: 'DELETE',
			body: JSON.stringify({ messageId })
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
			<button class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md" on:click={() => console.log('Emoji button clicked')}>
				<Smile class="w-5 h-5" />
			</button>
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="start">
			<div class="p-2 grid grid-cols-4 gap-2">
				{#each commonEmojis as emoji}
					<button 
						class={`hover:bg-gray-100 dark:hover:bg-gray-800 p-2 rounded text-lg transition-colors ${hasUserReacted(emoji) ? 'bg-accent' : ''}`}
						on:click={() => handleEmojiSelect(message.$id, emoji)}
					>
						{emoji}
					</button>
				{/each}
			</div>
		</DropdownMenu.Content>
	</DropdownMenu.Root>

	<button class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md" on:click={() => handleReply(message.$id)}>
		<MessageSquare class="w-5 h-5" />
	</button>

	{#if message.voice_id}
		<button 
			class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md"
			on:click={() => playTextToSpeech(message.voice_id, message.content)}
			disabled={loadingVoiceId !== null && loadingVoiceId !== message.voice_id}
			title={playingAudio?.voiceId === message.voice_id ? "Stop audio" : "Play text-to-speech"}
		>
			{#if loadingVoiceId === message.voice_id}
				<Loader2 class="w-5 h-5 animate-spin" />
			{:else if playingAudio?.voiceId === message.voice_id}
				<Speaker class="w-5 h-5 animate-pulse" />
			{:else}
				<Speaker class="w-5 h-5" />
			{/if}
		</button>
	{/if}

	<DropdownMenu.Root onOpenChange={onDropdownOpenChange}>
		<DropdownMenu.Trigger>
			<button class="p-1.5 hover:bg-accent rounded-md">
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
