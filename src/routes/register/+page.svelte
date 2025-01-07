<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import type { ActionData } from './$types';
	import { enhance } from '$app/forms';

	export let form: ActionData;
	let loading = false;
	let success = false;

	// Generate random user data
	const randomString = (length: number) => Math.random().toString(36).substring(2, length + 2);
	const randomEmail = () => `${randomString(8)}@${randomString(6)}.com`;
	const randomName = () => `Test User ${randomString(4)}`;
	const randomPassword = () => randomString(12);

	const defaultValues = {
		name: randomName(),
		email: randomEmail(),
		password: randomPassword()
	};
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">Create your account</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Or
				<a href="/login" class="font-medium text-blue-600 hover:text-blue-500">
					sign in to your existing account
				</a>
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
					type="text"
					name="name"
					label="Full name"
					required
					value={form?.name ?? defaultValues.name}
					error={form?.error}
					disabled={loading}
				/>
				<Input
					type="email"
					name="email"
					label="Email address"
					required
					value={form?.email ?? defaultValues.email}
					error={form?.error}
					disabled={loading}
				/>
				<Input
					type="password"
					name="password"
					label="Password"
					required
					value={defaultValues.password}
					disabled={loading}
				/>
			</div>

			<Button type="submit" disabled={loading}>
				{#if success}
					Success!
				{:else if loading}
					Creating account...
				{:else}
					Create account
				{/if}
			</Button>

			{#if form?.error}
				<p class="text-center text-sm text-red-600">{form.error}</p>
			{/if}
		</form>
	</div>
</div>