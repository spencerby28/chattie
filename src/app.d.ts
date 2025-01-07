import type { Models } from 'node-appwrite';

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user?: Models.User<Models.Preferences>;
		}
		// interface PageData {}
		// interface Platform {}
	}
}

export {};
