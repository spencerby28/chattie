import { ElevenLabsClient } from 'elevenlabs';
import { json } from '@sveltejs/kit';
import { ELEVENLABS_API_KEY } from '$env/static/private';

export async function POST({ request }) {
    try {
        const { voiceId, text } = await request.json();
        
        if (!voiceId || !text) {
            return json({ error: 'Missing required parameters' }, { status: 400 });
        }

        const client = new ElevenLabsClient({
            apiKey: ELEVENLABS_API_KEY
        });

        console.log(voiceId);

        const audioStream = await client.textToSpeech.convert(voiceId, {
            output_format: "mp3_44100_128",
            text,
            model_id: "eleven_turbo_v2_5"
        });

        console.log(audioStream);

        // Convert stream to Uint8Array
        const chunks = [];
        for await (const chunk of audioStream) {
            chunks.push(chunk);
        }
        const audioData = Buffer.concat(chunks);
        const base64Audio = audioData.toString('base64');
        
        return json({ audio: base64Audio });
    } catch (error) {
        console.error('Text-to-speech error:', error);
        return json({ error: 'Failed to convert text to speech' }, { status: 500 });
    }
} 