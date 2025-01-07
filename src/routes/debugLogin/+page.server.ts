import { error, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { createAdminClient, SESSION_COOKIE } from '$lib/appwrite/appwrite-server';
import { ID } from 'appwrite';

export const actions: Actions = {
	debugLogin: async ({ cookies, request }) => {
		const data = await request.formData();
		const userId = data.get('userId')?.toString();

		if (!userId) {
			throw error(400, 'User ID is required');
		}

		// In a real app, you'd want to validate these IDs against your database
		const validUserIds = ['user1', 'user2', 'user3', 'user4', 'user5'];

		if (!validUserIds.includes(userId)) {
			throw error(400, 'Invalid test user ID');
		}

		const email = `${userId}@test2.com`;
		try {
			const { account } = createAdminClient();

			// Try to create the user if they don't exist
			try {
				await account.create(
					userId,
					email,
					'password', // No password needed for test users
					userId.replace('-', ' ').toUpperCase() // Convert test-user-1 to TEST USER 1
				);
			} catch (err: any) {
				// Ignore error if user already exists
				if (err.code !== 409) {
					throw err;
				}
			}

			// Create a new session for the test user
			const session = await account.createEmailPasswordSession(email, 'password');

			// Set the session in a cookie
			cookies.set(SESSION_COOKIE, session.secret, {
				path: '/',
				httpOnly: true,
				sameSite: 'strict',
				secure: true
			});
		} catch (err) {
			console.error('Debug login error:', err);
			throw error(500, 'Failed to create debug session');
		}
		throw redirect(303, '/');
	}
};
