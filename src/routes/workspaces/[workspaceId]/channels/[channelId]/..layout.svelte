<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';

    onMount(() => {

// Check if we need to reinitialize the realtime connection
const searchParams = new URLSearchParams($page.url.search);
if (searchParams.get('reinitialize') === 'true') {
    const realtime = RealtimeService.getInstance();
    realtime.reinitialize();
    // Remove the flag from URL to prevent unnecessary reinitializations
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.delete('reinitialize');
    window.history.replaceState({}, '', newUrl);
}
});
</script>