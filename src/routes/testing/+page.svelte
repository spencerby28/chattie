<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import { debounce } from 'lodash-es';
    import type { PageData } from './$types';
    import type { Message } from '$lib/types';

    export let data: PageData;

    let searchInput = $page.url.searchParams.get('q') || '';
    let isSearching = false;
    let searchResults: Message[] = [];

    // Debounced search function for instant search
    const debouncedSearch = debounce(async (value: string) => {
        if (!value || value.length < 2) {
            searchResults = [];
            return;
        }

        isSearching = true;
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(value)}`);
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            searchResults = data.hits || [];
        } catch (error) {
            console.error('Search error:', error);
            searchResults = [];
        } finally {
            isSearching = false;
        }
    }, 300);

    // Handle input changes for instant search
    function handleInput(event: Event) {
        const value = (event.target as HTMLInputElement).value;
        searchInput = value;
        debouncedSearch(value);
    }

    // Handle search button click for full search
    async function handleSearchClick() {
        if (!searchInput || searchInput.length < 2) return;
        
        isSearching = true;
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(searchInput)}`);
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            searchResults = data.hits || [];
        } catch (error) {
            console.error('Search error:', error);
            searchResults = [];
        } finally {
            isSearching = false;
        }
    }
</script>

<div class="container mx-auto p-4 space-y-6">
    <div class="flex gap-4">
        <Input
            type="search"
            placeholder="Search messages..."
            value={searchInput}
            on:input={handleInput}
            class="flex-1"
        />
        <Button 
            on:click={handleSearchClick}
            disabled={isSearching}
            variant="default"
        >
            {isSearching ? 'Searching...' : 'Search'}
        </Button>
    </div>

    <div class="space-y-4">
        {#if searchResults.length === 0}
            <p class="text-muted-foreground">No messages found</p>
        {:else}
            {#each searchResults as message}
                <div class="border rounded-lg p-4">
                    <p class="text-sm text-muted-foreground">
                        {new Date(message.$createdAt).toLocaleString()}
                    </p>
                    <p class="mt-2">{message.content}</p>
                </div>
            {/each}
        {/if}
    </div>
</div>
