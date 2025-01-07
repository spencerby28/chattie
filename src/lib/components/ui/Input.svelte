<script lang="ts">
	let className = '';
	export { className as class };
	export let type = 'text';
	export let name = '';
	export let value = '';
	export let label = '';
	export let error: string | undefined = undefined;
	export let required = false;
	export let disabled = false;
</script>

<div class="flex flex-col space-y-1">
	{#if label}
		<label for={name} class="block text-sm font-medium text-gray-700">{label}</label>
	{/if}
	<input
		{type}
		{name}
		{value}
		{required}
		{disabled}
		id={name}
		class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed {error ? 'border-red-500' : ''} {className}"
		on:input
		on:change
	/>
</div> 