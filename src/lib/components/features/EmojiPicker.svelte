<script lang="ts">
	import * as Popover from "$lib/components/ui/popover";
	import { Smile } from "lucide-svelte";

	export let onEmojiSelect: (emoji: string) => void;

	const commonEmojis = [
		"👍", "❤️", "😂", "🎉", "🙏", "👀", "🔥", "✨",
		"😊", "🤔", "👋", "💯", "🚀", "💪", "👏", "🙌"
	];
</script>

<div class="grid grid-cols-4 gap-2 p-2 w-48 select-none">
	{#each commonEmojis as emoji}
		<button
			class="hover:bg-gray-100 p-2 rounded-lg transition-colors text-xl hover:scale-110 transform duration-100"
			on:click={() => onEmojiSelect(emoji)}
		>
			{emoji}
		</button>
	{/each}
</div>

<style>
	button {
		-webkit-user-select: none;
		-moz-user-select: none;
		-ms-user-select: none;
		user-select: none;
	}
</style> 