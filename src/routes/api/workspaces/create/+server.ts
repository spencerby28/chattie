import { error, redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { ID, Permission, Role } from 'appwrite';
import type { Channel } from '$lib/types';
import { dev } from '$app/environment';

export const POST: RequestHandler = async ({ request, locals }) => {
    let workspaceId: any;
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    const data = await request.json();
    const name = data.name;
    const description = data.description || '';
    const visibility = data.visibility;
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
                members: [locals.user.$id],
                channels: [{
                    name: 'general',
                    workspace_id: genId,
                    type: 'public',
                    members: [locals.user.$id]
                }, {
                    name: 'announcements',
                    workspace_id: genId,
                    type: 'public', 
                    members: [locals.user.$id]
                }, {
                    name: 'random',
                    workspace_id: genId,
                    type: 'public',
                    members: [locals.user.$id]
                }, {
                    name: 'help',
                    workspace_id: genId,
                    type: 'public',
                    members: [locals.user.$id]
                }]
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
        
        const account = await appwrite.users.get(locals.user.$id);

        const channelIds = workspace.channels.map((channel: Channel) => channel.$id);
        console.log('updating labels with channels:', channelIds);
        await appwrite.users.updateLabels(
            account.$id,
            [...(account.labels || []), ...channelIds]
        );

        // Send request to Python server in dev mode only
        /*
        if (dev) {
            try {
                const response = await fetch(`http://localhost:8080/?workspace_id=${workspaceId}&description=${encodeURIComponent(description)}`);
                if (!response.ok) {
                    console.error('Error from Python server:', await response.text());
                }
            } catch (e) {
                console.error('Failed to connect to Python server:', e);
            }
        }
        */

        return new Response(JSON.stringify({ workspaceId }), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e) {
        console.error('Error creating workspace:', e);
        throw error(500, 'Failed to create workspace');
    }
};
