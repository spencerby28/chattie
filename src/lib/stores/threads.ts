import { writable, get } from 'svelte/store';
import type { Message } from '$lib/types';

export const open = writable(false);

function createThreadStore() {
	const { subscribe, set, update } = writable<Message[]>([]);

	return {
		subscribe,
		add: (message: Message) => {
			update((messages) => [...messages, message]);
		},
		delete: (messageId: string) => {
			update((messages) => messages.filter((m) => m.$id !== messageId));
		},
		get: (messageId: string) => {
			const messages = get({ subscribe });
			return messages.find((m) => m.$id === messageId);
		},
		set
	};
}

export const threadStore = createThreadStore();
export const replyBoxStore = writable<{
	open: boolean;
	messageId: string;
	channelId: string;
}>({
	open: false,
	messageId: '',
	channelId: ''
});
