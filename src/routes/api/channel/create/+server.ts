import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const { name, type, workspace_id } = await request.json();

        if (!name || !type || !workspace_id) {
            throw error(400, 'Name, type and workspace_id are required');
        }

        const appwrite = createAdminClient();

        // Create the channel document
        const channel = await appwrite.databases.createDocument(
            'main',
            'channels',
            ID.unique(),
            {
                name,
                type,
                workspace_id,
                members: [locals.user.$id]
            },
            type === 'private' ? [
                Permission.read(Role.user(locals.user.$id)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ] : [
                Permission.read(Role.users()),
                Permission.write(Role.users()),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );
        // Update user's labels to include new channel
        console.log('Getting user account:', locals.user.$id);
        const account = await appwrite.users.get(locals.user.$id);
        console.log('Updating user labels to include channel:', channel.$id);
        await appwrite.users.updateLabels(
            account.$id,
            [...(account.labels || []), channel.$id]
        );

        // Update workspace to include new channel
        console.log('Getting workspace:', workspace_id);
        const workspace = await appwrite.databases.getDocument('main', 'workspaces', workspace_id);
        const updatedChannels = [...(workspace.channels || []), {
            name: channel.name,
            workspace_id: channel.workspace_id,
            type: channel.type,
            members: channel.members,
            $id: channel.$id
        }];
        console.log('Updating workspace with new channel:', channel.$id);
        await appwrite.databases.updateDocument(
            'main',
            'workspaces',
            workspace_id,
            {
                channels: updatedChannels
            }
        );

        // Update labels for all workspace members
        console.log('Updating labels for workspace members:', workspace.members);
        const memberPromises = workspace.members.map(async (memberId: string) => {
            console.log('Getting member account:', memberId);
            const memberAccount = await appwrite.users.get(memberId);
            console.log('Updating member labels:', memberId);
            await appwrite.users.updateLabels(
                memberId,
                [...(memberAccount.labels || []), channel.$id]
            );
        });
        await Promise.all(memberPromises);

        console.log('Channel creation complete:', channel.$id);
        return json({ channel });

    } catch (e) {
        console.error('Error creating channel:', e);
        throw error(500, 'Failed to create channel');
    }
};
