import { Client } from 'appwrite';
import { PUBLIC_APPWRITE_PROJECT, PUBLIC_APPWRITE_ENDPOINT } from '$env/static/public';
import type { Message, Channel, Workspace } from '$lib/types';
import { messageStore } from '$lib/stores/messages';
import { channelStore } from '$lib/stores/channels';
import { goto } from '$app/navigation';
import { toast } from 'svelte-sonner';
import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { get, writable, type Writable } from 'svelte/store';
import type { SimpleMember } from '$lib/types';
import { avatarStore } from '$lib/stores/avatars';
import { memberStore } from '$lib/stores/members';
import { browser } from '$app/environment';
import { presenceStore } from '$lib/stores/presence';
import { reactionsStore } from '$lib/stores/reactions';

// Define connection states
type ConnectionState = 'disconnected' | 'connecting' | 'connected';

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

function parseEventType(events: string[]): string {
	if (events.some(evt => evt.includes('create'))) return 'create';
	if (events.some(evt => evt.includes('update'))) return 'update';
	if (events.some(evt => evt.includes('delete'))) return 'delete';
	return 'unknown';
}

function handlePresenceEvent(eventType: string, payload: any) {
	// console.log('[RealtimeService] Handling presence event:', { eventType, payload });
	
	// For create or update events, update the presence store
	if (eventType === 'create' || eventType === 'update') {
		presenceStore.updateStatus(
			payload.userId,
			payload.baseStatus,
			payload.customStatus
		);
	} else if (eventType === 'delete') {
		// If a presence document is deleted, set user to offline
		presenceStore.updateStatus(payload.userId, 'offline');
	}
}

export class RealtimeService {
	private static instance: RealtimeService;
	private client: Client | null = null;
	private unsubscribe: (() => void) | null = null;
	private connectionState: Writable<ConnectionState> = writable('disconnected');
	private notificationState: Writable<NotificationState>;
	private initializationPromise: Promise<() => void> | null = null;
	private unsubWorkspace: any;
	private unsubChannels: any;
	private unsubMessages: any;
	private unsubPresence: any;

	private constructor() {
		// Only create client in browser
		if (browser) {
			this.client = new Client()
				.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
				.setProject(PUBLIC_APPWRITE_PROJECT);
		}
		
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

	public getConnectionState(): Writable<ConnectionState> {
		return this.connectionState;
	}

	public getNotificationState(): Writable<NotificationState> {
		return this.notificationState;
	}

	public async initialize(): Promise<() => void> {
		// Never initialize on server
		if (!browser) {
			return () => {};
		}

		// If already initializing, return the existing promise
		if (this.initializationPromise) {
			return this.initializationPromise;
		}

		// If already connected, return the existing unsubscribe function
		if (get(this.connectionState) === 'connected' && this.unsubscribe) {
			return this.unsubscribe;
		}

		this.initializationPromise = new Promise<() => void>(async (resolve, reject) => {
			console.log('[RealtimeService] Starting initialization');
			this.connectionState.set('connecting');

			// Ensure we have a client
			if (!this.client) {
				this.client = new Client()
					.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
					.setProject(PUBLIC_APPWRITE_PROJECT);
			}

			const collections = [
				'databases.main.collections.messages.documents',
				'databases.main.collections.reactions.documents',
				'databases.main.collections.channels.documents',
				'databases.main.collections.workspaces.documents',
				'databases.main.collections.presence.documents'
			];

			try {
				// Clean up any existing subscription
				if (this.unsubscribe) {
					console.log('[RealtimeService] Cleaning up existing subscription');
					this.unsubscribe();
					this.unsubscribe = null;
				}

				this.unsubscribe = this.client.subscribe(collections, (response) => {
					const event = response as RealtimeEvent;
					const collectionName = event.events[0].split('.')[3];
					const eventType = event.events[0].split('.').pop();
					const payload = event.payload;

					// Log the event for debugging
				//	console.log(`[RealtimeService] ${collectionName} ${eventType}:`, payload);

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
						case 'presence':
							handlePresenceEvent(eventType!, payload);
							break;
					}
				});

				this.connectionState.set('connected');
				console.log('[RealtimeService] Successfully initialized and connected');
				resolve(() => {
					if (this.unsubscribe) this.unsubscribe();
				});
			} catch (error) {
				console.error('[RealtimeService] Failed to initialize:', error);
				this.connectionState.set('disconnected');
				this.unsubscribe = null;
				reject(error);
			} finally {
				this.initializationPromise = null;
			}
		});

		return this.initializationPromise;
	}

	private handleMessageEvent(eventType: string, payload: Message) {
		switch (eventType) {
			case 'create':
				messageStore.addMessage(payload);
				this.updateUnreadCount(payload.channel_id);
				this.checkMentions(payload);
				break;
			case 'update':
				messageStore.updateMessage(payload.$id, payload);
				break;
			case 'delete':
				messageStore.deleteMessage(payload.$id);
				break;
		}

		this.addToRecentActivity('message', payload);
	}

	private handleReactionEvent(eventType: string, payload: any) {
		switch (eventType) {
			case 'create':
			case 'update':
				reactionsStore.updateReaction(payload.message_id, {
					emoji: payload.emoji,
					userIds: payload.userIds || [payload.user_id]
				});
				break;
			case 'delete':
				reactionsStore.removeReaction(payload.message_id, payload.emoji);
				break;
		}
		this.addToRecentActivity('reaction', payload);
	}

	private handleChannelEvent(eventType: string, payload: Channel) {
		switch (eventType) {
			case 'create':
				// Delay channel store update to ensure label is updated first
				setTimeout(() => {
					channelStore.addChannel(payload);
					this.showChannelToast('Channel Created', payload);
					// Reinitialize realtime to get new channel permissions
					console.log('[RealtimeService] New channel created, reinitializing to get new permissions');
					this.reinitialize().catch(error => {
						console.error('[RealtimeService] Failed to reinitialize after channel creation:', error);
					});
				}, 500); // Small delay to ensure label update completes
				break;
			case 'update':
				channelStore.updateChannel(payload.$id, payload);
				this.showChannelToast('Channel Updated', payload);
				break;
			case 'delete':
				channelStore.deleteChannel(payload.$id);
				this.showChannelToast('Channel Deleted', payload);
				break;
		}

		this.addToRecentActivity('channel', payload);
	}

	private handleWorkspaceEvent(eventType: string, payload: Workspace) {
		// Workspace events might require navigation or UI updates
		switch (eventType) {
			case 'delete':
				// If user is in the deleted workspace, redirect to home
				const currentPath = window.location.pathname;
				if (currentPath.includes(`/workspaces/${payload.$id}`)) {
					toast('Workspace Deleted', {
						description: `The workspace "${payload.name}" has been deleted.`
					});
					goto('/');
				}
				break;
			case 'update':
				// Update member store with new members and ensure avatars are initialized
				if (payload.members) {
					const currentMembers = get(memberStore);
					const currentMemberIds = new Set(currentMembers.map(m => m.id));
					const newMemberIds = new Set(payload.members);
					
					// Only fetch details for members that aren't already in the store
					const membersToFetch = payload.members.filter(id => !currentMemberIds.has(id));
					const membersToRemove = currentMembers.filter(m => !newMemberIds.has(m.id));
					
					if (membersToFetch.length > 0) {
						Promise.all(
							membersToFetch.map(async (memberId) => {
								try {
									const response = await fetch('/api/user', {
										method: 'POST',
										headers: {
											'Content-Type': 'application/json'
										},
										body: JSON.stringify({ userId: memberId })
									});

									if (!response.ok) {
										throw new Error('Failed to fetch user');
									}

									const user = await response.json();
									const avatarId = user.prefs?.avatarId;
									const avatarUrl = avatarId ? avatarStore.getAvatarUrl(avatarId) : null;

									return {
										id: memberId,
										name: user.name,
										avatarId: avatarId,
										avatarUrl
									} as SimpleMember;
								} catch (error) {
									console.error(`Failed to fetch user details for ${memberId}:`, error);
									return null;
								}
							})
						)
						.then((newMembers) => {
							const validNewMembers = newMembers.filter((m): m is SimpleMember => m !== null);
							// Keep existing members that are still valid and add new ones
							const updatedMembers = [
								...currentMembers.filter(m => !membersToRemove.some(rm => rm.id === m.id)),
								...validNewMembers
							];
							memberStore.updateMembers(updatedMembers);
						})
						.catch((error) => {
							console.error('Failed to update members:', error);
						});
					} else if (membersToRemove.length > 0) {
						// If we only need to remove members, do that without fetching
						const updatedMembers = currentMembers.filter(m => !membersToRemove.some(rm => rm.id === m.id));
						memberStore.updateMembers(updatedMembers);
					}
				}
				
				toast('Workspace Updated', {
					description: `The workspace "${payload.name}" has been updated.`
				});
				break;
		}
	}

	private updateUnreadCount(channelId: string) {
		this.notificationState.update((state) => ({
			...state,
			unreadMessages: {
				...state.unreadMessages,
				[channelId]: (state.unreadMessages[channelId] || 0) + 1
			}
		}));
	}

	private checkMentions(message: Message) {
		if (message.mentions?.length) {
			this.notificationState.update((state) => ({
				...state,
				mentions: [message, ...state.mentions].slice(0, 50)
			}));
		}
	}

	private addToRecentActivity(type: 'message' | 'reaction' | 'channel', payload: any) {
		this.notificationState.update((state) => ({
			...state,
			recentActivity: [
				{ type, payload, timestamp: Date.now() },
				...state.recentActivity
			].slice(0, 50)
		}));
	}

	private showChannelToast(action: string, channel: Channel) {
		toast(action, {
			description: `#${channel.name}`,
			action: {
				label: 'View',
				onClick: () => goto(`/workspaces/${channel.workspace_id}/channels/${channel.$id}`)
			}
		});
	}

	public markChannelAsRead(channelId: string) {
		if (!browser) return;
		
		this.notificationState.update((state) => ({
			...state,
			unreadMessages: {
				...state.unreadMessages,
				[channelId]: 0
			}
		}));
	}

	public cleanup() {
		if (!browser) return;
		
		console.log('[RealtimeService] Starting cleanup');
		
		// Cleanup subscription
		if (this.unsubscribe) {
			console.log('[RealtimeService] Unsubscribing from realtime events');
			this.unsubscribe();
			this.unsubscribe = null;
		}
		
		// Reset connection state
		this.connectionState.set('disconnected');
		
		// Reset initialization promise
		this.initializationPromise = null;
		
		// Reset client to force WebSocket closure
		this.client = null;
		
		// Cleanup workspace subscription
		if (this.unsubWorkspace) this.unsubWorkspace();
		if (this.unsubChannels) this.unsubChannels();
		if (this.unsubMessages) this.unsubMessages();
		if (this.unsubPresence) this.unsubPresence();
		
		console.log('[RealtimeService] Cleanup complete');
	}

	public async reinitialize(): Promise<() => void> {
		if (!browser) return () => {};
		
		console.log('[RealtimeService] Starting reinitialization');
		
		// Clean up existing subscription
		if (this.unsubscribe) {
			console.log('[RealtimeService] Cleaning up existing subscription');
			this.unsubscribe();
			this.unsubscribe = null;
		}
		
		// Reset connection state
		this.connectionState.set('disconnected');
		
		// Reset initialization promise
		this.initializationPromise = null;
		
		// Create new client
		this.client = new Client()
			.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
			.setProject(PUBLIC_APPWRITE_PROJECT);
		
		// Small delay to ensure old connection is fully closed
		await new Promise((resolve) => setTimeout(resolve, 100));
		
		// Initialize new connection
		return this.initialize();
	}
}
