import { json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Query, Permission, Role } from 'appwrite';

export async function POST({ request, locals, fetch }) {
    if (!locals.user) {
        throw new Error('Not authenticated');
    }

    const { memberNames, memberIds, message, workspaceId, groupName } = await request.json();
    const currentUserId = locals.user.$id;

    // Add current user to members if not already included
    const allMemberIds = Array.from(new Set([currentUserId, ...memberIds]));

    const appwrite = createAdminClient();

    // Only check for existing DM if exactly 2 members
    if (allMemberIds.length === 2) {
        const [user1, user2] = allMemberIds;
        // Query for channels that contain both members using $all operator
        const existingChannels = await appwrite.databases.listDocuments(
            'main',
            'channels',
            [
                Query.equal('type', 'dm'),
                Query.contains('members', user1),
                Query.contains('members', user2)
            ]
        );

        // Check if any channel has exactly these two members
        const existingDM = existingChannels.documents.find(channel => 
            channel.members.length === 2 && 
            channel.members.includes(user1) && 
            channel.members.includes(user2)
        );

        if (existingDM) {
            // If there's an initial message, send it to the existing channel
            if (message) {
                await fetch('/api/message/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        content: message,
                        channelId: existingDM.$id,
                        workspaceId
                    })
                });
            }
            return json({ channelId: existingDM.$id });
        }
    }

    console.log('allMemberIds', allMemberIds);
    // Create new DM channel with permissions
    const channel = await appwrite.databases.createDocument(
        'main',
        'channels',
        ID.unique(),
        {
            name: memberNames.join(' & '),
            workspace_id: workspaceId,
            type: 'dm',
            members: allMemberIds,
        },
        allMemberIds.map(userId => [
            Permission.read(Role.user(userId)),
            Permission.write(Role.user(userId)),
            Permission.delete(Role.user(userId))
        ]).flat()
    );
    console.log('new channel', channel);

    // Update each member's labels to include the new channel ID
    for (const memberId of allMemberIds) {
        const account = await appwrite.users.get(memberId);
        console.log(`Updating labels for user ${memberId} to include channel:`, channel.$id);
        await appwrite.users.updateLabels(
            memberId,
            [...(account.labels || []), channel.$id]
        );
    }

    // Send initial message if provided
    if (message) {
        await fetch('/api/message/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: message,
                channelId: channel.$id,
                workspaceId
            })
        });
    }

    return json({ channelId: channel.$id });
}
