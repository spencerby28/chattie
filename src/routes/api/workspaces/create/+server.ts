import { error, redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role, Query } from 'appwrite';
import type { Channel } from '$lib/types';
import { dev } from '$app/environment';

export const POST: RequestHandler = async ({ request, locals, url }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const data = await request.json();
    const name = data.name;
    const description = data.description || '';
    const visibility = data.visibility;
    const useAI = url.searchParams.get('ai') === 'true';

    if (!name) {
        throw error(400, 'Workspace name is required');
    }

    try {
        const appwrite = createAdminClient();
        let genId: string = ID.unique();
        const workspace = await appwrite.databases.createDocument(
            'main',
            'workspaces',
            genId,
            {
                name: name,
                ai_persona: description,
                message_frequency: 5,
                owner_id: locals.user.$id,
                members: [locals.user.$id, 'bot']
            },
            visibility === 'private' ? [
                Permission.read(Role.user(locals.user.$id)),
                Permission.write(Role.user(locals.user.$id)), 
                Permission.delete(Role.user(locals.user.$id))
            ] : [
                Permission.read(Role.users()),
                Permission.write(Role.users()),
                Permission.delete(Role.user(locals.user.$id))
            ]
        );

        await appwrite.storage.createBucket(
            genId,
            name,
            visibility === 'private' ? [
                Permission.read(Role.user(locals.user.$id)),
                Permission.write(Role.user(locals.user.$id)),
                Permission.delete(Role.user(locals.user.$id))
            ] : [
                Permission.read(Role.users()),
                Permission.write(Role.users()),
                Permission.delete(Role.user(locals.user.$id))
            ],
            true // Enable file security
        );

        let channelIds: string[] = [];

        if (dev && useAI) {
            try {
                // Wait for AI initialization to complete
                const response = await fetch(`http://localhost:8080/?workspace_id=${genId}&description=${encodeURIComponent(description)}`);
                if (!response.ok) {
                    throw new Error('AI initialization failed');
                }
                const result = await response.json();
                
                // Get all channels created by the AI
                const channelsResponse = await appwrite.databases.listDocuments(
                    'main',
                    'channels',
                    [Query.equal('workspace_id', genId)]
                );
                channelIds = channelsResponse.documents.map(channel => channel.$id);
            } catch (e) {
                console.error('Failed to initialize AI:', e);
                throw error(500, 'Failed to initialize AI workspace');
            }
        } else {
            // Create default channels only if not using AI
            const defaultChannels = ['general', 'announcements', 'random', 'help'];
            for (const channelName of defaultChannels) {
                const channel = await appwrite.databases.createDocument(
                    'main',
                    'channels',
                    ID.unique(),
                    {
                        name: channelName,
                        workspace_id: genId,
                        type: 'public',
                        members: [locals.user.$id]
                    },
                    visibility === 'private' ? [
                        Permission.read(Role.user(locals.user.$id)),
                        Permission.write(Role.user(locals.user.$id)),
                        Permission.delete(Role.user(locals.user.$id))
                    ] : [
                        Permission.read(Role.label(genId)),
                        Permission.write(Role.label(genId)), 
                        Permission.delete(Role.user(locals.user.$id))
                    ]
                );
                channelIds.push(channel.$id);
            }
        }

        // Update user's labels with workspace ID and channel IDs
        const account = await appwrite.users.get(locals.user.$id);
        await appwrite.users.updateLabels(
            account.$id,
            [...(account.labels || []), ...channelIds, genId]
        );

        return new Response(JSON.stringify({ workspaceId: genId }), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e) {
        console.error('Error creating workspace:', e);
        throw error(500, 'Failed to create workspace');
    }
};
