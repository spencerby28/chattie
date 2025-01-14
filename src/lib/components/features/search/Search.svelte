<script lang="ts">
	import * as Command from '$lib/components/ui/command';
	import { Search as SearchIcon } from 'lucide-svelte';

	// Import global search stores and helpers
	import {
		searching,
		searchResults,
		searchQuery,
		searchOpen,
		handleSelectMessage
	} from './search';

	/**
	 * Close and clear the search when the dialog fires a close event
	 */
	function closeAndClear() {
		searchOpen.set(false);
		searchQuery.set('');
		searchResults.set([]);
		searching.set(false);
	}

	/**
	 * Handle CMD+K / Ctrl+K keyboard shortcut
	 */
	function handleKeydown(e: KeyboardEvent) {
		if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
			e.preventDefault();
			searchOpen.set(true);
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<Command.Dialog bind:open={$searchOpen} on:close={closeAndClear}>
	<Command.Root shouldFilter={false}>
		<div class="flex items-center border-b px-3">
			
			<Command.Input
				placeholder="Search messages..."
				bind:value={$searchQuery}
				class="h-11 w-full bg-transparent focus:outline-none placeholder:text-muted-foreground"
			/>
		</div>

		<Command.List>
			{#key $searching}
				{#if $searching}
					<Command.Loading>
						<div class="p-4 text-sm text-muted-foreground">
							Searching messages...
						</div>
					</Command.Loading>
				{:else if $searchResults.length === 0 && $searchQuery.length >= 2}
					<Command.Empty>
						<div class="p-4 text-sm text-muted-foreground">
							No results found.
						</div>
					</Command.Empty>
				{:else if $searchQuery.length < 2}
					<Command.Empty>
						<div class="p-4 text-sm text-muted-foreground">
							Type at least 2 characters to search...
						</div>
					</Command.Empty>
				{:else}
					<Command.Group heading="Messages">
						{#each $searchResults as result, i}
							<Command.Item
								value={result.$id || `result-${i}`}
								onSelect={() => handleSelectMessage(result)}
								class="flex flex-col items-start gap-2 py-2 px-4"
							>
								<div class="flex items-center gap-2 w-full">
									<span class="font-medium text-sm">{result.sender_name}</span>
									<span class="text-xs text-muted-foreground">
										{new Date(result.$createdAt || '').toLocaleString()}
									</span>
								</div>
								<div class="text-sm text-foreground/90 line-clamp-2">
									{result.content}
								</div>
							</Command.Item>
						{/each}
					</Command.Group>
				{/if}
			{/key}
		</Command.List>
	</Command.Root>
</Command.Dialog>
