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

        // Get the original message
        const originalMessage = await appwrite.databases.getDocument('main', 'messages', messageId);

        // Create the thread channel
        const channel = await appwrite.databases.createDocument(
            'main',
            'channels',
            ID.unique(),
            {
                name: `Reply to: ${originalMessage.content.substring(0, 100)}${originalMessage.content.length > 100 ? '...' : ''}`,
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
        console.log('channel', channel)

        // Update the original message with thread info
        await appwrite.databases.updateDocument(
            'main',
            'messages',
            messageId,
            {
                thread_id: channel.$id,
                thread_count: 0  // Will be incremented when replies are added
            }
        );

        // Create a copy of the original message in the thread channel
        const threadMessage = await appwrite.databases.createDocument(
            'main',
            'messages',
            ID.unique(),
            {
                content: originalMessage.content,
                channel_id: channel.$id,
                workspace_id: workspaceId,
                sender_id: originalMessage.sender_id,
                sender_name: originalMessage.sender_name,
                sender_type: originalMessage.sender_type,
                edited_at: originalMessage.edited_at,
                mentions: originalMessage.mentions || [],
                ai_context: originalMessage.ai_context || null,
                ai_prompt: originalMessage.ai_prompt || null
            },
            [
                Permission.read(Role.label(channel.$id)),
                Permission.write(Role.user(originalMessage.sender_id)),
                Permission.delete(Role.user(originalMessage.sender_id))
            ]
        );

        // Get workspace to update member labels
        const workspace = await appwrite.databases.getDocument('main', 'workspaces', workspaceId);

        // Update labels for all workspace members
        const memberPromises = workspace.members.map(async (memberId: string) => {
            const memberAccount = await appwrite.users.get(memberId);
            await appwrite.users.updateLabels(
                memberId,
                [...(memberAccount.labels || []), channel.$id]
            );
        });
        await Promise.all(memberPromises);

        return json({ 
            channel,
            threadMessage
        });
    } catch (e) {
        console.error('Error creating thread:', e);
        throw error(500, 'Failed to create thread');
    }
};
