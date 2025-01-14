import { createSessionClient } from '$lib/appwrite/appwrite-client';
import { Query } from 'appwrite';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Message } from '$lib/types';

export const load = (async ({ locals, params, ...event }) => {
  if (!locals.user) {
    return {
      messages: [],
      channels: []
    };
  }

  try {
    const client = createSessionClient(event);

    // Get messages for this channel only
    /*
    const messagesResponse = await client.databases.listDocuments(
      'main', 
      'messages',
      [
        Query.equal('channel_id', params.channelId),
        Query.orderDesc('$createdAt'),
        Query.limit(50)
      ]
    );
    */

    // Get workspace document to get channels
    const workspace = await client.databases.getDocument('main', 'workspaces', params.workspaceId);

    // Filter channels based on type and membership like in workspace layout
    const filteredChannels = workspace.channels?.filter((channel: any) => {
      if (channel.type === 'public') return true;
      return channel.members.includes(locals.user!.$id);
    }) || [];

    return {
    //  messages: messagesResponse.documents as Message[],
      channels: filteredChannels
    };

  } catch (e) {
    throw error(500, 'Failed to load messages and channels: ' + e);
  }
}) satisfies LayoutServerLoad;
