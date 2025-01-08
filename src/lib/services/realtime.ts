import { Client } from 'appwrite';
import { PUBLIC_APPWRITE_PROJECT, PUBLIC_APPWRITE_ENDPOINT } from '$env/static/public';
import type { Message, Channel, Workspace } from '$lib/types';
import { messageStore } from '$lib/stores/messages';
import { channelStore } from '$lib/stores/channels';
import { goto } from '$app/navigation';
import { toast } from 'svelte-sonner';
import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { writable, type Writable } from 'svelte/store';

type RealtimeEvent = {
	events: string[];
	payload: any;
};

export interface NotificationState {
	unreadMessages: { [channelId: string]: number };
	mentions: Message[];
	recentActivity: Array<{
		type: 'message' | 'reaction' | 'channel';
		payload: any;
		timestamp: number;
	}>;
}

export class RealtimeService {
	private static instance: RealtimeService;
	private client: Client;
	private unsubscribe: (() => void) | null = null;
	private isConnected: boolean;
	public notificationState: Writable<NotificationState>;

	private constructor() {
		this.client = new Client()
			.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
			.setProject(PUBLIC_APPWRITE_PROJECT);
		this.isConnected = false;
		this.notificationState = writable({
			unreadMessages: {},
			mentions: [],
			recentActivity: []
		});
	}

	public static getInstance(): RealtimeService {
		if (!RealtimeService.instance) {
			RealtimeService.instance = new RealtimeService();
		}
		return RealtimeService.instance;
	}

	public initialize(): () => void {
		console.log('Initializing global realtime connection');
		if (this.unsubscribe) {
			console.log('Already connected to realtime');
			return this.unsubscribe;
		}

		const collections = [
			'databases.main.collections.messages.documents',
			'databases.main.collections.reactions.documents',
			'databases.main.collections.channels.documents',
			'databases.main.collections.workspaces.documents'
		];

		console.log('Subscribing to all collections:', collections);

		this.unsubscribe = this.client.subscribe(collections, (response) => {
			const event = response as RealtimeEvent;
			console.log('Global event received:', event);

			const collectionName = event.events[0].split('.')[3];
			const eventType = event.events[0].split('.').pop();
			const payload = event.payload;

			switch (collectionName) {
				case 'messages':
					this.handleMessageEvent(eventType!, payload);
					break;
				case 'reactions':
					this.handleReactionEvent(eventType!, payload);
					break;
				case 'channels':
					this.handleChannelEvent(eventType!, payload);
					break;
				case 'workspaces':
					this.handleWorkspaceEvent(eventType!, payload);
					break;
			}
		});

		return () => this.cleanup();
	}

	private async handleMessageEvent(eventType: string, payload: Message) {
		//console.log('Handling message event:', eventType, payload);

		// Update stores
		if (eventType === 'create') {
		//	console.log('Adding new message to store:', payload);
			messageStore.addMessage(payload);

			// Update unread count for channel
			this.notificationState.update((state) => {
				const count = (state.unreadMessages[payload.channel_id] || 0) + 1;
		//		console.log('Updating unread count for channel', payload.channel_id, 'to', count);
				return {
					...state,
					unreadMessages: {
						...state.unreadMessages,
						[payload.channel_id]: count
					}
				};
			});

			// Check for mentions
			if (payload.mentions?.length) {
				console.log('Message contains mentions:', payload.mentions);
				this.notificationState.update((state) => ({
					...state,
					mentions: [payload, ...state.mentions].slice(0, 50) // Keep last 50 mentions
				}));
			}
		} else if (eventType === 'update') {
			console.log('Updating existing message:', payload.$id);
			// Fetch the full message to get the latest state

			const { databases } = createBrowserClient();
			const fullMessage = await databases.getDocument('main', 'messages', payload.$id);
		

			messageStore.updateMessage(payload.$id, fullMessage);
		} else if (eventType === 'delete') {
			console.log('Deleting message:', payload.$id);
			messageStore.deleteMessage(payload.$id);
		}

		// Add to recent activity
		this.notificationState.update((state) => ({
			...state,
			recentActivity: [
				{
					type: 'message' as const,
					payload,
					timestamp: Date.now()
				},
				...state.recentActivity
			].slice(0, 50) // Keep last 50 activities
		}));

		// Show toast if needed (based on preferences)
		if (eventType === 'create') {
			const { account } = createBrowserClient();
			const currentUser = await account.get();

			// Only show notification if message is from someone else
			if (payload.sender_id !== currentUser.$id) {
				console.log('Checking notification preferences for message from:', payload.sender_name);
				const shouldShow = await this.shouldNotify(payload.workspace_id, 'message');

				// Check if user is currently in the channel where message was sent
				const currentPath = window.location.pathname;
				const isInChannel = currentPath.includes(
					`/workspaces/${payload.workspace_id}/channels/${payload.channel_id}`
				);

				if (shouldShow && !isInChannel) {
					const author = payload.sender_name || 'Someone';
					console.log('Showing toast notification for message from:', author);
					toast(`💬 New message in #${payload.channel_name || 'channel'}`, {
						description: `${author}: ${payload.content.substring(0, 60)}${payload.content.length > 60 ? '...' : ''}`,
						action: {
							label: 'View',
							onClick: () =>
								goto(`/workspaces/${payload.workspace_id}/channels/${payload.channel_id}`)
						}
					});
				} else if (isInChannel) {
					// TODO: Implement last seen functionality here
					// This is where we'll track when the user last saw messages in this channel
				}
			}
		}
	}

	private async handleReactionEvent(eventType: string, payload: any) {
		//  console.log('Handling reaction event:', eventType, payload);

		// Only process if we have a message_id
		const messageId = payload.message_id;
		if (!messageId) return;

		try {
			// Get the message from Appwrite to ensure we have latest state
			const { databases } = createBrowserClient();
			const message = await databases.getDocument('main', 'messages', messageId);

			// Update the message in our store with the latest reactions
			if (message) {
				console.log('Updating message with new reactions:', message);
				messageStore.updateMessage(messageId, message);
			}
		} catch (error) {
			console.error('Error updating message reactions:', error);
		}

		// Add to recent activity
		this.notificationState.update((state) => ({
			...state,
			recentActivity: [
				{
					type: 'reaction' as const,
					payload,
					timestamp: Date.now()
				},
				...state.recentActivity
			].slice(0, 50)
		}));

		// Show toast if needed
		if (eventType === 'create') {
			const shouldShow = await this.shouldNotify(payload.workspace_id, 'work');
			if (shouldShow) {
				const currentPath = window.location.pathname;
				const isInChannel = currentPath.includes(
					`/workspaces/${payload.workspace_id}/channels/${payload.channel_id}`
				);

				if (!isInChannel) {
					const author = payload.user_name || 'Someone';
					toast(`${payload.emoji} New reaction`, {
						description: `${author} reacted to a message in #${payload.channel_name || 'channel'}`,
						action: {
							label: 'View',
							onClick: () =>
								goto(`/workspaces/${payload.workspace_id}/channels/${payload.channel_id}`)
						}
					});
				}
			}
		}
	}

	private async handleChannelEvent(eventType: string, payload: Channel) {
		// Update channel store
		if (eventType === 'create') {
			channelStore.addChannel(payload);
			// Reinitialize realtime connection to get new permissions
			await this.reinitialize();
		} else if (eventType === 'update') {
			channelStore.updateChannel(payload.$id, payload);
		} else if (eventType === 'delete') {
			channelStore.deleteChannel(payload.$id);
		}

		// Add to recent activity
		this.notificationState.update((state) => ({
			...state,
			recentActivity: [
				{
					type: 'channel' as const,
					payload,
					timestamp: Date.now()
				},
				...state.recentActivity
			].slice(0, 50)
		}));

		// Show toast if needed
		const shouldShow = await this.shouldNotify(payload.workspace_id, 'work');
		if (shouldShow) {
			if (eventType === 'create') {
				toast('📢 New Channel Created', {
					description: `Channel #${payload.name} was created`,
					action: {
						label: 'View',
						onClick: () => goto(`/workspaces/${payload.workspace_id}/channels/${payload.$id}`)
					}
				});
			} else if (eventType === 'update') {
				toast('🔄 Channel Updated', {
					description: `Channel #${payload.name} was updated`,
					action: {
						label: 'View',
						onClick: () => goto(`/workspaces/${payload.workspace_id}/channels/${payload.$id}`)
					}
				});
			}
		}
	}

	private handleWorkspaceEvent(eventType: string, payload: Workspace) {
		console.log('Workspace event:', eventType, payload);
		console.log('Workspace channels:', payload.channels);

		// If workspace is deleted, remove all associated channels
		if (eventType === 'delete') {
			console.log('Handling workspace deletion');
			channelStore.update((channels: Channel[]) => {
				console.log('Filtering out channels for workspace:', payload.$id);
				return channels.filter((channel: Channel) => channel.workspace_id !== payload.$id);
			});

			// Show toast for workspace deletion
			toast('🏢 Workspace Deleted', {
				description: `Workspace "${payload.name}" has been deleted`
			});

			// Redirect to home if currently in the deleted workspace
			const currentPath = window.location.pathname;
			if (currentPath.includes(`/workspaces/${payload.$id}`)) {
				goto('/');
			}
		}

		// If workspace is updated, only update workspace-specific data
		if (eventType === 'update') {
			console.log('Workspace update received:', {
				id: payload.$id,
				name: payload.name,
				channelCount: payload.channels?.length || 0
			});

			// We don't update the channel store here anymore
			// But let's log what we have for debugging
			channelStore.update((channels) => {
				console.log(
					'Current channels in store:',
					channels.map((c) => ({ id: c.$id, name: c.name }))
				);
				return channels; // Return unchanged
			});

			toast('🏢 Workspace Updated', {
				description: `Workspace "${payload.name}" has been updated`
			});
		}
	}

	private async shouldNotify(
		workspaceId: string,
		type: 'work' | 'mention' | 'message'
	): Promise<boolean> {
		try {
			const { account } = createBrowserClient();
			const prefs = await account.getPrefs();
			return prefs[`${type}_${workspaceId}`] === true;
		} catch (error) {
			console.error('Error checking notification preferences:', error);
			return false;
		}
	}

	public markChannelAsRead(channelId: string) {
		this.notificationState.update((state) => ({
			...state,
			unreadMessages: {
				...state.unreadMessages,
				[channelId]: 0
			}
		}));
	}

	public cleanup() {
		console.log('Cleaning up realtime connection');
		if (this.unsubscribe) {
			this.unsubscribe();
			this.unsubscribe = null;
			this.isConnected = false;
		}
		console.log('Realtime connection cleaned up');
	}

	public async reinitialize() {
		console.log('Reinitializing realtime connection');
		// First cleanup existing connection
		this.cleanup();

		// Small delay to ensure the old connection is fully closed
		await new Promise((resolve) => setTimeout(resolve, 100));

		// Initialize new connection
		return this.initialize();
	}
}
