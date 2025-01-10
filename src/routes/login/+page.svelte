<script lang="ts">
	import { Input } from '$lib/components/ui/input';
	import Button from '$lib/components/ui/Button.svelte';
	import type { ActionData } from './$types';
	import { enhance } from '$app/forms';
	import { dev } from '$app/environment';

	export let form: ActionData;
	let loading = false;
	let success = false;
</script>

<div class="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div>
			<h1 class="text-8xl font-chattie tracking-wider text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600"><a href="/welcome">Chattie</a></h1>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">Sign in to your account</h2>
			<p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
				Or
				<a href="/register" class="font-medium text-purple-600 hover:text-purple-500 dark:text-purple-400 dark:hover:text-purple-300"> create a new account </a>
			</p>
		</div>
		<form
			method="POST"
			class="mt-8 space-y-6"
			use:enhance={() => {
				loading = true;
				success = false;
				return async ({ update, result }) => {
					await update();
					if (result.type === 'redirect') {
						success = true;
						await new Promise(resolve => setTimeout(resolve, 250));
					}
					loading = false;
				};
			}}
		>
			<div class="space-y-4">
				<div class="space-y-2">
					<label for="email" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
						Email address
					</label>
					<Input
						type="email"
						id="email"
						name="email"
						required
						disabled={loading}
						value={dev ? "spencer@sb28.xyz" : form?.email ?? ''}
						class={form?.error ? "border-red-500" : ""}
					/>
				</div>

				<div class="space-y-2">
					<label for="password" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
						Password
					</label>
					<Input
						type="password"
						id="password" 
						name="password"
						required
						disabled={loading}
						value={dev ? "spencerr" : ""}
						class={form?.error ? "border-red-500" : ""}
					/>
				</div>
			</div>

			<Button type="submit" disabled={loading} class="bg-gradient-to-r from-blue-400 to-purple-600 text-white">
				{#if success}
					Success!
				{:else if loading}
					Signing in...
				{:else}
					Sign in
				{/if}
			</Button>

			{#if form?.error}
				<p class="text-center text-sm text-red-600 dark:text-red-400">{form.error}</p>
			{/if}
		</form>
		<div class="flex gap-4">
			<Button 
				on:click={() => window.location.href = '/register'}
				disabled={loading}
				class="flex-1 border-2 bg-transparent border-gray-300 dark:border-white !text-gray-700 dark:!text-white hover:border-transparent hover:!text-white hover:bg-gradient-to-r hover:from-blue-400 hover:to-purple-600 transition-all duration-200"
			>
				Try Demo Account
			</Button>
		</div>
	</div>
</div>