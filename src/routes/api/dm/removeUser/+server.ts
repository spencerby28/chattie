import { error, json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';

export async function POST({ request, locals }) {
    if (!locals.user) {
        throw error(401, 'Not authenticated');
    }

    try {
        const { channelId, userId } = await request.json();

        if (!channelId || !userId) {
            throw error(400, 'Channel ID and user ID are required');
        }

        const appwrite = createAdminClient();

        // Get user's current labels
        const user = await appwrite.users.get(userId);
        
        // Remove channel ID from user's labels
        const updatedLabels = (user.labels || []).filter((label: string) => label !== channelId);
        
        // Update user's labels
        await appwrite.users.updateLabels(userId, updatedLabels);

        // Get the channel document
        const channel = await appwrite.databases.getDocument('main', 'channels', channelId);

        // Remove user from channel members
        const updatedMembers = channel.members.filter((memberId: string) => memberId !== userId);

        // Update channel document with new members list
        await appwrite.databases.updateDocument('main', 'channels', channelId, {
            members: updatedMembers
        });

        return json({ success: true });

    } catch (e) {
        console.error('Error updating DM:', e);
        throw error(500, 'Failed to update DM');
    }
}
