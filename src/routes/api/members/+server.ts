import { json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';

export async function POST({ request }) {
    const { memberIds } = await request.json();
    
    try {
        const { users } = createAdminClient();
        
        const memberPromises = memberIds.map(async (memberId: string) => {
            try {
                const user = await users.get(memberId);
                const prefs = user.prefs || {};
                
                return {
                    id: user.$id,
                    name: user.name || user.email,
                    avatarId: prefs.avatarId || null
                };
            } catch (e) {
                console.error(`Error fetching user ${memberId}:`, e);
                return { id: memberId, name: 'Unknown User', avatarId: null };
            }
        });

        const memberData = await Promise.all(memberPromises);
        return json({ members: memberData });
    } catch (error) {
        console.error('Error fetching members:', error);
        return json({ members: [] }, { status: 500 });
    }
} 