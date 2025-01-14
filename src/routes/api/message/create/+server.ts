import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role, Query } from 'appwrite';
import type { Message } from '$lib/types';

export const POST: RequestHandler = async ({ request, locals }) => {
    const startTime = performance.now();
    console.log('[message/create] Starting message creation');

    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { content, channelId, workspaceId, isThread } = await request.json();
        console.log(`[message/create] Parsed request data at ${performance.now() - startTime}ms`);

        if (!content || !channelId || !workspaceId) {
            throw error(400, 'Content, channelId, and workspaceId are required');
        }
        console.log('[message/create] creating message', content, channelId, workspaceId);
        const appwrite = createAdminClient();
        console.log(`[message/create] Created Appwrite client at ${performance.now() - startTime}ms`);

        let messageData = {
            content,
            channel_id: channelId,
            sender_name: locals.user.name,
            sender_id: locals.user.$id,
            workspace_id: workspaceId,
            sender_type: 'user',
            edited_at: new Date().toISOString(),
        };

        // If this is a message in a thread channel, increment the thread count on the original message
        if (isThread) {
            console.log('[message/create] creating message in thread', channelId);
            const threadStartTime = performance.now();
            try {
                // Get the original message (the one that started the thread)
                // It will have thread_id equal to this channel's ID
                const originalMessage = await appwrite.databases.listDocuments('main', 'messages', [
                    Query.equal('thread_id', channelId),
                    Query.limit(1)
                ]);
                console.log(`[message/create] Found original message at ${performance.now() - threadStartTime}ms`);

                if (originalMessage.documents.length > 0) {
                    const threadCount = (originalMessage.documents[0].thread_count || 0) + 1;
                    // Update thread count on original message
                    await appwrite.databases.updateDocument('main', 'messages', originalMessage.documents[0].$id, {
                        thread_count: threadCount
                    });
                    console.log(`[message/create] Updated thread count at ${performance.now() - threadStartTime}ms`);
                }
            } catch (e) {
                console.warn('Could not update thread count:', e);
            }
        }
        
        const createStartTime = performance.now();
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
        console.log(`[message/create] Message created in ${performance.now() - createStartTime}ms:`, message);
        
        const totalTime = performance.now() - startTime;
        console.log(`[message/create] Total execution time: ${totalTime}ms`);
        return json({ message });

    } catch (e) {
        const errorTime = performance.now() - startTime;
        console.error(`[message/create] Error creating message at ${errorTime}ms:`, e);
        throw error(500, 'Failed to create message');
    }
};
