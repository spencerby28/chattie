import type { LayoutLoad } from './$types';
import { browser } from '$app/environment';
import { avatarStore } from '$lib/stores/avatars';

export const load: LayoutLoad = async ({ data }) => {
    if (!browser) {
        return { ...data };
    }

    // Prewarm avatar cache with valid avatar IDs
    const avatarIds = data.memberData
        .map((member: any) => member.avatarId)
        .filter(Boolean);
    avatarStore.prewarm(avatarIds);

    // Add avatar URLs to member data
    const memberDataWithAvatars = data.memberData.map((member: any) => ({
        ...member,
        avatarUrl: member.avatarId ? avatarStore.getAvatarUrl(member.avatarId) : undefined
    }));

    return {
        ...data,
        memberData: memberDataWithAvatars
    };
};