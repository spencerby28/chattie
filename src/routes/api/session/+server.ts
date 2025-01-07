import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { SESSION_COOKIE } from '$lib/appwrite/constants';
export const GET: RequestHandler = async ({ cookies }) => {
  const sessionId = cookies.get(SESSION_COOKIE);
  
  if (!sessionId) {
    return json({ session: null });
  }

  return json({
    session: sessionId
  });
};
