import { error, redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';
import type { Channel } from '$lib/types';
import { dev } from '$app/environment';

export const POST: RequestHandler = async ({ request, locals, url }) => {
    let workspaceId: any;
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
        workspaceId = workspace.$id;

        await appwrite.storage.createBucket(
            workspaceId,
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

        if (dev && useAI) {
            // Don't await the AI initialization
            fetch(`http://localhost:8080/?workspace_id=${workspaceId}&description=${encodeURIComponent(description)}`)
                .catch(e => console.error('Failed to connect to Python server:', e));
        }

        // Create default channels only if not using AI
        if (!useAI) {
            const defaultChannels = ['general', 'announcements', 'random', 'help'];
            const channelIds = [];
            for (const channelName of defaultChannels) {
                const channel = await appwrite.databases.createDocument(
                    'main',
                    'channels',
                    ID.unique(),
                    {
                        name: channelName,
                        workspace_id: workspaceId,
                        type: 'public',
                        members: [locals.user.$id]
                    },
                    visibility === 'private' ? [
                        Permission.read(Role.user(locals.user.$id)),
                        Permission.write(Role.user(locals.user.$id)),
                        Permission.delete(Role.user(locals.user.$id))
                    ] : [
                        Permission.read(Role.label(workspaceId)),
                        Permission.write(Role.label(workspaceId)), 
                        Permission.delete(Role.user(locals.user.$id))
                    ]
                );
                channelIds.push(channel.$id);
            }
            
            const account = await appwrite.users.get(locals.user.$id);

            console.log('updating labels with channels:', channelIds);
            await appwrite.users.updateLabels(
                account.$id,
                [...(account.labels || []), ...channelIds, workspaceId]
            );
        }

        // Return immediately with the workspace ID
        return new Response(JSON.stringify({ workspaceId }), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e) {
        console.error('Error creating workspace:', e);
        throw error(500, 'Failed to create workspace');
    }
};
