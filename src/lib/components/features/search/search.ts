import { writable, get } from 'svelte/store';
import { debounce } from 'lodash-es';
import { goto } from '$app/navigation';
import { createBrowserClient } from '$lib/appwrite/appwrite-browser';

/**
 * Search data interfaces
 */
export interface SearchResult {
	channel_id: string;
	workspace_id: string;
	sender_id: string;
	content: string;
	sender_name: string;
	$id?: string;
	$createdAt?: string;
}

/**
 * Global search state
 */
export const searchOpen = writable(false);
export const searchQuery = writable('');
export const searchResults = writable<SearchResult[]>([]);
export const searching = writable(false);
export const userChannels = writable<string[]>([]);

/**
 * Debounced search function
 */
const debouncedSearch = debounce(async (query: string) => {
	if (!query || query.length < 2) {
		searchResults.set([]);
		searching.set(false);
		return;
	}

	searching.set(true);
	try {
		const channels = get(userChannels);
		const response = await fetch('/api/search', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				query,
				channels
			})
		});

		if (!response.ok) throw new Error('Search failed');
		const data = await response.json();

		const results = data.hits || data.documents || [];
		searchResults.set(results);
	} catch (error) {
		console.error('Search error:', error);
		searchResults.set([]);
	} finally {
		searching.set(false);
	}
}, 300);

/**
 * Initialize watchers and setup search
 */
export async function initializeSearch() {
	// Get user's accessible channels once
	try {
		const client = createBrowserClient();
		const account = await client.account.get();
		// Store the channels the user has access to
		// This would need to be updated when channels change
		const labels = account.labels || [];
		userChannels.set(labels);
	} catch (error) {
		console.error('Failed to get user channels:', error);
	}

	// Watch changes in searchQuery
	searchQuery.subscribe((value) => {
		if (!value) {
			searchResults.set([]);
			searching.set(false);
		} else {
			debouncedSearch(value);
		}
	});
}

/**
 * Called when a user selects a message
 */
export function handleSelectMessage(message: SearchResult) {
	console.log('Selected message:', message);
	searchOpen.set(false);
	goto(`/workspaces/${message.workspace_id}/channels/${message.channel_id}?messageId=${message.$id}`);
}
