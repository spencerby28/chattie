import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { messageId, workspaceId, content } = await request.json();
        const appwrite = createAdminClient();

        // Create the thread channel
        const channel = await appwrite.databases.createDocument(
            'main',
            'channels',
            ID.unique(),
            {
                name: `Reply to: ${content.substring(0, 100)}${content.length > 100 ? '...' : ''}`,
                type: 'thread',
                workspace_id: workspaceId,
                description: 'thread-description',
                members: [locals.user.$id]
            },
            [
                Permission.read(Role.label(workspaceId)),
                Permission.write(Role.label(workspaceId)),
                Permission.update(Role.label(workspaceId)),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        // Create the initial message
        const message = await appwrite.databases.createDocument(
            'main',
            'messages',
            ID.unique(),
            {
                channel_id: channel.$id,
                workspace_id: workspaceId,
                content: content,
                sender_id: locals.user.$id,
                sender_name: locals.user.name,
                sender_type: 'user',
                thread_id: channel.$id,
                thread_count: 0
            },
            [
                Permission.read(Role.label(channel.$id)),
                Permission.update(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        return json({ 
            channel,
            message
        });
    } catch (e) {
        console.error('Error creating thread:', e);
        throw error(500, 'Failed to create thread');
    }
};
