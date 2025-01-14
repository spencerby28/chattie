import { MEILISEARCH_URL, MEILISEARCH_ADMIN_API_KEY } from '$env/static/private';
import { MeiliSearch } from 'meilisearch';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const client = new MeiliSearch({
  host: MEILISEARCH_URL,
  apiKey: MEILISEARCH_ADMIN_API_KEY
});

export const POST: RequestHandler = async ({ request }) => {
  const { query, channels } = await request.json();

  if (!query || query.length < 2) {
    return json({ hits: [] });
  }

  try {
    const searchResults = await client.index('messages').search(query, {
      limit: 10,
      rankingScoreThreshold: 0.5,
      filter: channels?.length ? [`channel_id IN ${JSON.stringify(channels)}`] : undefined
    });
    console.log(searchResults);

    return json(searchResults);
  } catch (error) {
    console.error('Meilisearch error:', error);
    return json({ error: 'Search failed' }, { status: 500 });
  }
};
