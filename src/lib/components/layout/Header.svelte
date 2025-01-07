<script lang="ts">
  import { page } from '$app/stores';
  import { Button } from "$lib/components/ui/button";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
  import { UserCircle } from 'lucide-svelte';
  import { onMount } from 'svelte';

  let fps = 0;
  let frameCount = 0;
  let lastTime = performance.now();
  let windowWidth: number;

  function updateFPS() {
    frameCount++;
    const currentTime = performance.now();
    const elapsed = currentTime - lastTime;

    if (elapsed >= 1000) {
      fps = Math.round((frameCount * 1000) / elapsed);
      frameCount = 0;
      lastTime = currentTime;
    }
    requestAnimationFrame(updateFPS);
  }

  function handleResize() {
    windowWidth = window.innerWidth;
  }

  onMount(() => {
    handleResize(); // Set initial width
    window.addEventListener('resize', handleResize);
    requestAnimationFrame(updateFPS);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });

  async function handleSignOut() {
    const response = await fetch('/api/signOut', {
      method: 'POST'
    });
    if (response.ok) {
      window.location.href = '/debugLogin';
    }
  }

</script>

<header class="h-14 border-b flex items-center px-4 justify-between bg-white">
  <div class="flex items-center gap-4">
    <h1 class="font-semibold text-2xl"><a href="/">Chattie</a></h1>
    <span class="text-sm text-gray-500">{fps} FPS</span>
    <span class="text-sm text-gray-500">Width: {windowWidth}px</span>
  </div>

  <div class="flex items-center gap-4">
    {#if $page.data.user}
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          <div class="flex items-center gap-2 hover:bg-gray-100 rounded-full p-1 cursor-pointer">
            <UserCircle class="w-8 h-8" />
          </div>
        </DropdownMenu.Trigger>
        <DropdownMenu.Content>
          <DropdownMenu.Label>
            <div class="flex flex-col">
              <span>Hey {$page.data.user.name}</span>
              <span class="text-xs text-muted-foreground">{$page.data.user.email}</span>
            </div>
          </DropdownMenu.Label>
          <DropdownMenu.Separator />
          <DropdownMenu.Item 
            on:click={handleSignOut}
            class="text-destructive"
          >
            Sign Out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Root>
    {:else}
      <a href="/debugLogin" class="text-blue-600 hover:text-blue-800">Log in</a>
    {/if}
  </div>
</header>