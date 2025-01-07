import { createSessionClient } from '$lib/appwrite/appwrite-client';
import { Query } from 'appwrite';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load = (async ({ locals, params, ...event }) => {
  if (!locals.user) {
    return {
      messages: []
    };
  }

  try {
    const client = createSessionClient(event);
    const response = await client.databases.listDocuments(
      'main',
      'messages',
      [
        Query.equal('channel_id', params.channelId)
      ]
    );
 //   console.log('[LayoutServerLoad] messages', response.documents);

    return {
      messages: response.documents
    };
  } catch (e) {
    throw error(500, 'Failed to load messages ' + e);
  }
}) satisfies LayoutServerLoad;

