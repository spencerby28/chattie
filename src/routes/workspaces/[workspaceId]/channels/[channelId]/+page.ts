import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { error } from '@sveltejs/kit';
import { Query } from 'appwrite';
import type { PageLoad } from './$types';
import { reactionsStore } from '$lib/stores/reactions';

export const load: PageLoad = async ({ params }) => {
	try {
		const { databases } = createBrowserClient();

		// Fetch messages for the channel
		const messages = await databases.listDocuments(
			'main',
			'messages',
			[
				Query.equal('channel_id', params.channelId),
				Query.orderDesc('$createdAt'),
				Query.limit(50)
			]
		);

		// Get all AI messages and fetch their voice_ids
		const aiMessages = messages.documents.filter(msg => msg.sender_type === 'ai_persona');
		if (aiMessages.length > 0) {
			// Get all unique AI persona IDs
			const aiPersonaIds = [...new Set(aiMessages.map(msg => msg.sender_id))];
			
			// Fetch AI personas in a single query
			const aiPersonasResponse = await databases.listDocuments(
				'main',
				'ai_personas',
				[Query.equal('$id', aiPersonaIds)]
			);

			// Create a map of AI persona ID to voice_id
			const aiPersonaVoiceMap = new Map(
				aiPersonasResponse.documents.map(persona => [persona.$id, persona.voice_id])
			);

			// Attach voice_ids to messages
			messages.documents = messages.documents.map(msg => {
				if (msg.sender_type === 'ai_persona') {
					return {
						...msg,
						voice_id: aiPersonaVoiceMap.get(msg.sender_id)
					};
				}
				return msg;
			});
		}

		// Fetch reactions for all messages
		const reactions = await databases.listDocuments(
			'main',
			'reactions',
			[
				Query.equal('channel_id', params.channelId),
				Query.limit(250)
			]
		);

		console.log('Found reactions:', reactions.documents);

		// Group reactions by message
		const reactionsByMessage: { [messageId: string]: any[] } = {};
		reactions.documents.forEach((reaction: any) => {
			if (!reactionsByMessage[reaction.message_id]) {
				reactionsByMessage[reaction.message_id] = [];
			}
			// Pass the raw reaction document
			reactionsByMessage[reaction.message_id].push(reaction);
		});

		console.log('Grouped reactions by message:', reactionsByMessage);

		// Update the reactions store with raw reactions
		Object.entries(reactionsByMessage).forEach(([messageId, reactions]) => {
			reactionsStore.setMessageReactions(messageId, reactions);
		});

		return {
			messages: messages.documents,
			channelId: params.channelId,
			workspaceId: params.workspaceId
		};
	} catch (e) {
		console.error('Error loading channel:', e);
		throw error(500, 'Failed to load channel');
	}
}; 