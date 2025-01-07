<script lang="ts">
	let className = '';
	export { className as class };
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let disabled = false;
</script>

<button
	{type}
	{disabled}
	class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed {className}"
	on:click
>
	<slot />
</button> 