import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';
import type { Message } from '$lib/types';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { content, channelId, workspaceId } = await request.json();

        if (!content || !channelId || !workspaceId) {
            throw error(400, 'Content, channelId, and workspaceId are required');
        }
        console.log('[message/create] creating message', content, channelId, workspaceId);
        const appwrite = createAdminClient();
        
        const message = await appwrite.databases.createDocument(
            'main',
            'messages',
            ID.unique(),
            {
                content,
                channel_id: channelId,
                sender_name: locals.user.name,
                sender_id: locals.user.$id,
                workspace_id: workspaceId,
                sender_type: 'user',
                edited_at: new Date().toISOString()
            },
            [
                Permission.read(Role.label(channelId)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );
        console.log('Message created:', message);
        

        return json({ message });

    } catch (e) {
        console.error('Error creating message:', e);
        throw error(500, 'Failed to create message');
    }
};
