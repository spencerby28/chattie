import { writable } from 'svelte/store';
import type { SimpleMember } from '$lib/types';

function createMemberStore() {
    const { subscribe, set, update } = writable<SimpleMember[]>([]);

    return {
        subscribe,
        set,
        update,
        updateMembers: (members: SimpleMember[]) => {
            set(members);
        },
        addMember: (member: SimpleMember) => {
            update(members => [...members, member]);
        },
        removeMember: (memberId: string) => {
            update(members => members.filter(m => m.id !== memberId));
        }
    };
}

export const memberStore = createMemberStore(); 