import { SESSION_COOKIE, createAdminClient } from '$lib/appwrite/appwrite-server';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
    default: async ({ request, cookies }) => {
        // Extract the form data
        const form = await request.formData();
        const email = form.get('email')?.toString().trim();
        const password = form.get('password')?.toString();

        try {
            // Validate inputs
            if (!email || !password) {
                return fail(400, {
                    error: 'Email and password are required',
                    email: email || ''
                });
            }

            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                return fail(400, { 
                    error: 'Invalid email format',
                    email: email
                });
            }
        } catch (error: any) {
            console.error('Validation error:', error);
            return fail(400, {
                error: 'Validation failed',
                email: email || ''
            });
        }

        try {
            // Create the Appwrite client
            const { account } = createAdminClient();

            // Create the session using the client
            const session = await account.createEmailPasswordSession(email, password);

            // Set the session cookie with the secret
            cookies.set(SESSION_COOKIE, session.secret, {
                sameSite: 'strict',
                expires: new Date(session.expire),
                secure: true,
                path: '/',
                httpOnly: true
            });

            // Redirect to workspaces after successful login
            
        } catch (error: any) {
            console.error('Login error:', error);
            return fail(400, {
                error: 'Invalid email or password',
                email: email || ''
            });
        }
        throw redirect(303, '/');
    }
} satisfies Actions; 