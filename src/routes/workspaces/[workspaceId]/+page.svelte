<script lang="ts">
    export let data;
    let channels = data.workspace?.channels || [];
    import { dev } from '$app/environment';
    import { onMount } from 'svelte';

   // $: console.log(data);

    
    function joinChannel(channelId: string) {
        console.log(`Joining channel: ${channelId}`);
    }

    function navigateToChannel(channelId: string) {
        window.location.href = `/channels/${channelId}`;
    }
    onMount(() => {
        console.log(data);
    });
</script>

<div class="flex h-full">
    <main class="flex-1 p-4">

            {#if dev}
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
            {:else}
                <div class="flex flex-col items-center justify-center h-full space-y-8">
                    <div class="text-center space-y-4">
                        <h1 class="text-4xl font-light text-gray-600">
                            Welcome to Your Workspace
                        </h1>
                        <p class="text-gray-500 text-lg max-w-lg">
                            Select a channel from the sidebar to start collaborating with your team
                        </p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
                        <div class="p-6 bg-card rounded-lg border border-border">
                            <h3 class="text-xl font-semibold mb-2">Real-time Chat</h3>
                            <p class="text-muted-foreground">
                                Communicate instantly with your team through text, emojis, and file sharing
                            </p>
                        </div>

                        <div class="p-6 bg-card rounded-lg border border-border">
                            <h3 class="text-xl font-semibold mb-2">File Sharing</h3>
                            <p class="text-muted-foreground">
                                Easily share and preview files with your team members
                            </p>
                        </div>

                        <div class="p-6 bg-card rounded-lg border border-border">
                            <h3 class="text-xl font-semibold mb-2">Thread Discussions</h3>
                            <p class="text-muted-foreground">
                                Keep conversations organized with threaded replies and discussions
                            </p>
                        </div>

                        <div class="p-6 bg-card rounded-lg border border-border">
                            <h3 class="text-xl font-semibold mb-2">Reactions</h3>
                            <p class="text-muted-foreground">
                                React to messages with emojis to express yourself quickly
                            </p>
                        </div>
                    </div>
                </div>
            {/if}

    </main>
</div>