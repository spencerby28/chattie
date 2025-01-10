<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import { debounce } from 'lodash-es';
    import type { PageData } from './$types';

    export let data: PageData;

    let searchInput = $page.url.searchParams.get('q') || '';
    let isSearching = false;

    // Debounced search function for instant search
    const debouncedSearch = debounce((value: string) => {
        const url = new URL(window.location.href);
        url.searchParams.set('q', value);
        goto(url.toString(), { replaceState: true });
    }, 300);

    // Handle input changes for instant search
    function handleInput(event: Event) {
        const value = (event.target as HTMLInputElement).value;
        searchInput = value;
        debouncedSearch(value);
    }

    // Handle search button click for full search
    function handleSearchClick() {
        isSearching = true;
        const url = new URL(window.location.href);
        url.searchParams.set('q', searchInput);
        goto(url.toString())
            .finally(() => {
                isSearching = false;
            });
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

    {#if data.error}
        <div class="text-destructive">{data.error}</div>
    {/if}

    <div class="space-y-4">
        {#if data.messages.length === 0}
            <p class="text-muted-foreground">No messages found</p>
        {:else}
            {#each data.messages as message}
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
