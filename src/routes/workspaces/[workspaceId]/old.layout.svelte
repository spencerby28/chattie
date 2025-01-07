<script lang="ts">
  import { page } from '$app/stores';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  
</script>

{#if $page.data.workspace}
  <div class="h-full flex">
    <Sidebar />
    <div class="flex-1">
      <slot />
    </div>
  </div>
{:else}
  <div class="h-full flex items-center justify-center">
    <p>Workspace not found or you don't have access.</p>
  </div>
{/if}