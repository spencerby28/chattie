import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role, Query } from 'appwrite';
import type { Message } from '$lib/types';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { content, channelId, workspaceId, isThread } = await request.json();

        if (!content || !channelId || !workspaceId) {
            throw error(400, 'Content, channelId, and workspaceId are required');
        }
        console.log('[message/create] creating message', content, channelId, workspaceId);
        const appwrite = createAdminClient();

        let messageData = {
            content,
            channel_id: channelId,
            sender_name: locals.user.name,
            sender_id: locals.user.$id,
            workspace_id: workspaceId,
            sender_type: 'user',
            edited_at: new Date().toISOString(),
            mentions: [],
            ai_context: null,
            ai_prompt: null
        };

        // If this is a message in a thread channel, increment the thread count on the original message
        if (isThread) {
            console.log('[message/create] creating message in thread', channelId);
            try {
                // Get the original message (the one that started the thread)
                // It will have thread_id equal to this channel's ID
                const originalMessage = await appwrite.databases.listDocuments('main', 'messages', [
                    Query.equal('thread_id', channelId),
                    Query.limit(1)
                ]);

                if (originalMessage.documents.length > 0) {
                    const threadCount = (originalMessage.documents[0].thread_count || 0) + 1;
                    // Update thread count on original message
                    await appwrite.databases.updateDocument('main', 'messages', originalMessage.documents[0].$id, {
                        thread_count: threadCount
                    });
                }
            } catch (e) {
                console.warn('Could not update thread count:', e);
            }
        }
        
        const message = await appwrite.databases.createDocument(
            'main',
            'messages',
            ID.unique(),
            messageData,
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
