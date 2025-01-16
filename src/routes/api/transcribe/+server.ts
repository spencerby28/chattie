import { error, json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    if (!env.OPENAI_API_KEY) {
        throw error(500, 'OpenAI API key not configured');
    }

    try {
        const formData = await request.formData();
        const translate = formData.get('translate') === 'true';
        
        const endpoint = translate
            ? 'https://api.openai.com/v1/audio/translations'
            : 'https://api.openai.com/v1/audio/transcriptions';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${env.OPENAI_API_KEY}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        return json(result);

    } catch (err) {
        console.error('Transcription error:', err);
        throw error(500, {
            message: `Transcription failed: ${err}`
        });
    }
}; 