import { json } from '@sveltejs/kit';
import { createAdminClient } from '$lib/appwrite/appwrite-server';
import { Query } from 'appwrite';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        return new Response('Unauthorized', { status: 401 });
    }

    try {
        const { channelId, offset = 0 } = await request.json();
        
        if (!channelId) {
            return json({ 
                error: 'Channel ID is required' 
            }, { status: 400 });
        }

        const client = createAdminClient();
        const limit = 50;

        // First get messages
        const messagesResponse = await client.databases.listDocuments(
            'main',
            'messages',
            [
                Query.equal('channel_id', channelId),
                Query.orderDesc('$createdAt'),
                Query.limit(limit),
                Query.offset(offset)
            ]
        );

        // Get all AI messages
        const aiMessages = messagesResponse.documents.filter(msg => msg.sender_type === 'ai_persona');
        
        if (aiMessages.length > 0) {
            // Get all unique AI persona IDs
            const aiPersonaIds = [...new Set(aiMessages.map(msg => msg.sender_id))];
            
            // Fetch AI personas in a single query
            const aiPersonasResponse = await client.databases.listDocuments(
                'main',
                'ai_personas',
                [Query.equal('$id', aiPersonaIds)]
            );

            // Create a map of AI persona ID to voice_id
            const aiPersonaVoiceMap = new Map(
                aiPersonasResponse.documents.map(persona => [persona.$id, persona.voice_id])
            );

            // Attach voice_ids to messages
            messagesResponse.documents = messagesResponse.documents.map(msg => {
                if (msg.sender_type === 'ai_persona') {
                    return {
                        ...msg,
                        voice_id: aiPersonaVoiceMap.get(msg.sender_id)
                    };
                }
                return msg;
            });
        }
        console.log(messagesResponse.documents);

        return json({
            messages: messagesResponse.documents,
            total: messagesResponse.total
        });

    } catch (error) {
        console.error('Error loading messages:', error);
        return json({ 
            error: 'Failed to load messages' 
        }, { status: 500 });
    }
};
