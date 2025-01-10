import { writable } from 'svelte/store';
import type { SimpleMember } from '$lib/types';

type BaseStatus = 'online' | 'offline' | 'away';

interface CustomStatus {
    emoji?: string;
    text?: string;
}

interface PresenceInfo {
    baseStatus: BaseStatus;
    customStatus?: CustomStatus;
    lastSeen: Date;
}

interface PresenceState {
    [userId: string]: PresenceInfo;
}

function createPresenceStore() {
    const { subscribe, set, update } = writable<PresenceState>({});

    return {
        subscribe,
        updateStatus: (userId: string, baseStatus: BaseStatus, customStatus?: CustomStatus) => {
            update(state => ({
                ...state,
                [userId]: {
                    baseStatus,
                    customStatus,
                    lastSeen: new Date()
                }
            }));
        },
        setInitialState: (members: SimpleMember[]) => {
            const initialState: PresenceState = {};
            members.forEach(member => {
                initialState[member.id] = {
                    baseStatus: 'offline',
                    lastSeen: new Date()
                };
            });
            set(initialState);
        },
        reset: () => set({})
    };
}

export const presenceStore = createPresenceStore(); 