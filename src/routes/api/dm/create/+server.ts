import { json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Query, Permission, Role } from 'appwrite';

export async function POST({ request, locals }) {
    if (!locals.user) {
        throw new Error('Not authenticated');
    }

    const { otherUserId } = await request.json();
    const currentUserId = locals.user.$id;

    const { databases } = createAdminClient();

    // Check if DM channel already exists
    const existingChannel = await databases.listDocuments(
        'main',
        'channels',
        [
            Query.equal('type', 'dm'),
            Query.search('members', currentUserId),
            Query.search('members', otherUserId)
        ]
    );

    if (existingChannel.documents.length > 0) {
        return json({ channel: existingChannel.documents[0] });
    }

    // Create new DM channel with permissions
    const channel = await databases.createDocument(
        'main',
        'channels',
        ID.unique(),
        {
            type: 'dm',
            members: [currentUserId, otherUserId],
            created_at: new Date().toISOString()
        },
        [
            Permission.read(Role.user(currentUserId)),
            Permission.read(Role.user(otherUserId)),
            Permission.update(Role.user(currentUserId)),
            Permission.update(Role.user(otherUserId)),
            Permission.delete(Role.user(currentUserId)),
            Permission.delete(Role.user(otherUserId))
        ]
    );

    return json({ channel });
}
