<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import type { ActionData } from './$types';
	import { enhance } from '$app/forms';

	export let form: ActionData;
	let loading = false;
	let success = false;
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">Sign in to your account</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Or
				<a href="/register" class="font-medium text-blue-600 hover:text-blue-500"> create a new account </a>
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
				<Input
					type="email"
					name="email"
					label="Email address"
					required
					error={form?.error}
					value={form?.email ?? ''}
					disabled={loading}
				/>
				<Input
					type="password"
					name="password"
					label="Password"
					required
					disabled={loading}
				/>
			</div>

			<Button type="submit" disabled={loading}>
				{#if success}
					Success!
				{:else if loading}
					Signing in...
				{:else}
					Sign in
				{/if}
			</Button>

			{#if form?.error}
				<p class="text-center text-sm text-red-600">{form.error}</p>
			{/if}
		</form>
	</div>
</div> 