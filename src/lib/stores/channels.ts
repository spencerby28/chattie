import { writable } from 'svelte/store';
import type { Channel } from '$lib/types';

function createChannelStore() {
    const { subscribe, set, update } = writable<Channel[]>([]);

    return {
        subscribe,
        set,
        update,
        addChannel: (channel: Channel) => {
            update(channels => {
                const exists = channels.some(c => c.$id === channel.$id);
                if (exists) {
                    return channels;
                }
                return [...channels, channel];
            });
        },
        updateChannel: (channelId: string, updatedChannel: Channel) => {
            update(channels => channels.map(c => c.$id === channelId ? updatedChannel : c));
        },
        deleteChannel: (channelId: string) => {
            update(channels => channels.filter(c => c.$id !== channelId));
        }
    };
}

export const channelStore = createChannelStore(); 