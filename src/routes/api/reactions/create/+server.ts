import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { messageId, emoji, channelId } = await request.json();

        if (!messageId || !emoji || !channelId) {
            throw error(400, 'MessageId, emoji and channelId are required');
        }

        const appwrite = createAdminClient();

        const reaction = await appwrite.databases.createDocument(
            'main',
            'reactions',
            ID.unique(),
            {
                message_id: messageId,
                emoji,
                user_id: locals.user.$id,
                user_name: locals.user.name,
                channel_id: channelId
            },
            [
                Permission.read(Role.label(channelId)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        console.log('Reaction created:', reaction);

        return json({ reaction });

    } catch (e) {
        console.error('Error creating reaction:', e);
        throw error(500, 'Failed to create reaction');
    }
};
