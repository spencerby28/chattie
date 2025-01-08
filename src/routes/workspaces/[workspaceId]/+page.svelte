<script lang="ts">
    export let data;
    let channels = data.workspace.channels || [];
    import { onMount } from 'svelte';


    
    function joinChannel(channelId: string) {
        console.log(`Joining channel: ${channelId}`);
    }

    function navigateToChannel(channelId: string) {
        window.location.href = `/channels/${channelId}`;
    }
</script>

<div class="flex h-full">
    <main class="flex-1 p-4">
        {#if channels.length === 0}
            <div class="flex flex-col items-center justify-center h-full">
                <div class="text-2xl font-semibold text-gray-700 mb-4">
                    No Channels Yet
                </div>
                <p class="text-gray-500">
                    Channels will appear here once they're created
                </p>
            </div>
        {:else}
            <div class="flex flex-col items-center justify-center h-full space-y-6">
                <div class="text-4xl font-light text-gray-600">
                    Select a channel to start chatting
                </div>
                <p class="text-gray-500 text-lg">
                    Choose from the channels list on the left to begin your conversation
                </p>
            </div>
        {/if}

        <!-- Debug Data Section (Commented out for production) -->
        <!--
        <div class="bg-gray-50 rounded-lg p-6 shadow-sm mt-8">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Debug Workspace Data</h3>
            <details class="mb-4">
                <summary class="cursor-pointer text-sm text-gray-600 hover:text-gray-900">View Channels Data</summary>
                <pre class="bg-white p-4 rounded border border-gray-200 overflow-auto mt-2">
                    <code class="text-sm text-gray-800">{JSON.stringify(channels, null, 2)}</code>
                </pre>
            </details>
            <details>
                <summary class="cursor-pointer text-sm text-gray-600 hover:text-gray-900">View User Data</summary>
                <pre class="bg-white p-4 rounded border border-gray-200 overflow-auto mt-2">
                    <code class="text-sm text-gray-800">{JSON.stringify(data.user, null, 2)}</code>
                </pre>
            </details>
        </div>
        -->
    </main>
</div>