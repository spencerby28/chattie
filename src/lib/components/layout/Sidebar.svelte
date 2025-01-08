<script lang="ts">
  import type { Workspace } from '$lib/types';
  import WorkspaceNav from '$lib/components/layout/WorkspaceNav.svelte';
  import ChannelList from '$lib/components/layout/ChannelList.svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { channelStore } from '$lib/stores/channels';
  import { Settings } from 'lucide-svelte';
  
  import CreateWorkspace from '$lib/modal/CreateWorkspace.svelte';


  let workspaceDialogOpen = false;

  import {announceFeature} from '$lib/utils/toast';
  $: workspace = $page.data.workspace;
  $: workspaces = $page.data.workspaces;
  $: memberWorkspaces = workspaces.filter((ws: Workspace) => ws.members?.includes($page.data.user?.$id));

  // Initialize channelStore when workspace changes
  /*
  $: if (workspace?.channels) {
    channelStore.set(workspace.channels);
  }
  */

  let showChannels = true;
  let showDirectMessages = true;
</script>
<aside class="w-60 border-r flex flex-col bg-gray-50 dark:bg-gray-950">
  <div class="p-4 border-b dark:border-gray-800">
    <div class="flex items-center justify-between mb-2">
      <h1 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Workspaces</h1>
      <Button 
        variant="ghost" 
        size="icon" 
        class="h-8 w-8"
        on:click={() => {
          announceFeature('Workspace Settings');
          
        }}
      >
        <Settings class="h-4 w-4" />
      </Button>
    </div>
    {#if memberWorkspaces.length <= 1}
      <div class="flex flex-col gap-2">
        <Button variant="outline" on:click={() => workspaceDialogOpen = true} class="w-full">
          Create New Workspace
        </Button>
        <Button variant="outline" on:click={() => goto('/')} class="w-full">
          Join Another Workspace
        </Button>
      </div>
    {:else}
      <DropdownMenu.Root>
        <DropdownMenu.Trigger asChild let:builder>
          <Button variant="outline" builders={[builder]} class="w-full flex items-center justify-between bg-white hover:bg-accent dark:bg-gray-950 dark:hover:bg-accent">
            <span class="font-medium truncate">{workspace?.name || 'Select Workspace'}</span>
            <img src="/svg/carrot.svg" alt="Dropdown" class="ml-2 w-4 h-4 opacity-70 invert-0 dark:invert" />
          </Button>
        </DropdownMenu.Trigger>
        <DropdownMenu.Content class="w-56">
          <DropdownMenu.Label>Your Workspaces</DropdownMenu.Label>
          <DropdownMenu.Separator />
          {#each memberWorkspaces as ws}
            <DropdownMenu.Item 
              on:click={() => goto(`/workspaces/${ws.$id}`)}
              class={workspace?.$id === ws.$id ? 'bg-blue-100 dark:bg-blue-950' : ''}
            >
              {ws.name}
            </DropdownMenu.Item>
          {/each}
          <DropdownMenu.Separator />
          <DropdownMenu.Item on:click={() => workspaceDialogOpen = true}>
            Create New Workspace
          </DropdownMenu.Item>
          <DropdownMenu.Item on:click={() => goto('/')}>
            Join Another Workspace
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Root>
    {/if}
  </div>
  <div class="flex-1 overflow-y-auto">
    <div class="p-4">
      <button 
        class="w-full flex items-center justify-between text-sm text-gray-500 uppercase font-semibold"
        on:click={() => showChannels = !showChannels}
      >
        <span class="text-gray-500 dark:text-gray-400">Channels</span>
        <img 
          src="/svg/carrot.svg" 
          alt="Toggle channels" 
          class="w-4 h-4 opacity-70 invert-0 dark:invert transition-transform" 
          class:rotate-180={!showChannels}
        />
      </button>
      {#if showChannels}
        <div class="mt-2">
          <ChannelList workspaceId={workspace.$id} />
        </div>
      {/if}
    </div>
    
    <div class="p-4">
      <button 
        class="w-full flex items-center justify-between text-sm text-gray-500 uppercase font-semibold"
        on:click={() => showDirectMessages = !showDirectMessages}
      >
        <span class="text-gray-500 dark:text-gray-400">Direct Messages</span>
        <img 
          src="/svg/carrot.svg" 
          alt="Toggle direct messages" 
          class="w-4 h-4 opacity-70 invert-0 dark:invert transition-transform"
          class:rotate-180={!showDirectMessages}
        />
      </button>
      {#if showDirectMessages}
        <!-- DM list will go here -->
      {/if}
    </div>
  </div>

</aside>
<CreateWorkspace 
    open={workspaceDialogOpen} 
    onOpenChange={(open) => workspaceDialogOpen = open} 
/>