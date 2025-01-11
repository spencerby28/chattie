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
    console.log(data)

    if (!name) {
        throw error(400, 'Workspace name is required');
    }
    console.log('Creating workspace:', name, description, visibility);

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
                members: [locals.user.$id]
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

        // Create storage bucket for workspace
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

        // Create default channels
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

        // Send request to Python server only if AI is enabled and in dev mode
        if (dev && useAI) {
            try {
                const response = await fetch(`http://localhost:8080/?workspace_id=${workspaceId}&description=${encodeURIComponent(description)}`);
                if (!response.ok) {
                    console.error('Error from Python server:', await response.text());
                }
            } catch (e) {
                console.error('Failed to connect to Python server:', e);
            }
        }

        return new Response(JSON.stringify({ workspaceId }), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e) {
        console.error('Error creating workspace:', e);
        throw error(500, 'Failed to create workspace');
    }
};
