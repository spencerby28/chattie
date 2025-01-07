import { Client, Databases, Account } from 'appwrite';
import { PUBLIC_APPWRITE_ENDPOINT, PUBLIC_APPWRITE_PROJECT } from '$env/static/public';

let client: Client;

export function createBrowserClient() {
    if (!client) {
        client = new Client()
            .setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
            .setProject(PUBLIC_APPWRITE_PROJECT);
    }

    return {
        client,
        get account() {
            return new Account(client);
        },
        get databases() {
            return new Databases(client);
        }
    };
} 