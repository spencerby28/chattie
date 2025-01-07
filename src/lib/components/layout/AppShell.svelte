<script lang="ts">
  import { page } from '$app/stores';
  import Header from '$lib/components/layout/Header.svelte';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  
</script>

<div class="h-screen flex flex-col">
  <Header />
  <div class="flex-1 flex overflow-hidden">
    {#if $page.data.session}
      <Sidebar />
    {/if}
    <main class="flex-1 overflow-auto">
      <slot />
    </main>
  </div>
</div> 