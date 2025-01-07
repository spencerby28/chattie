<script lang="ts">
  import { page } from '$app/stores';
  import type { Workspace } from '$lib/types';

  export let workspaces: Workspace[] = [];
  
  $: currentWorkspaceId = $page.params.workspaceId;
</script>

<div class="p-4 border-b">
  <div class="flex flex-col gap-2">
    {#each workspaces as workspace (workspace.id)}
      <a
        href="/workspaces/{workspace.id}"
        class="flex items-center gap-2 p-2 rounded hover:bg-gray-100 transition-colors"
        class:bg-gray-100={workspace.id === currentWorkspaceId}
      >
        <div class="w-8 h-8 rounded bg-blue-500 flex items-center justify-center text-white font-semibold">
          {workspace.name.charAt(0).toUpperCase()}
        </div>
        <span class="text-sm font-medium">{workspace.name}</span>
      </a>
    {/each}

    <button
      class="flex items-center gap-2 p-2 rounded hover:bg-gray-100 transition-colors text-gray-600"
    >
      <div class="w-8 h-8 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
        <span class="text-xl">+</span>
      </div>
      <span class="text-sm font-medium">Add Workspace</span>
    </button>
  </div>
</div> 