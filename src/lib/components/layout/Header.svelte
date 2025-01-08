<script lang="ts">
  import { page } from '$app/stores';
  import { Button } from "$lib/components/ui/button";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
  import { UserCircle, Sun, Moon } from 'lucide-svelte';
  import { onMount } from 'svelte';

  let fps = 0;
  let frameCount = 0;
  let lastTime = performance.now();
  let windowWidth: number;
  let isDarkMode = true;

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

    // Check system preference on mount
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    isDarkMode = localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && prefersDark);
    updateTheme();

    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        isDarkMode = e.matches;
        updateTheme();
      }
    });

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });

  function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    updateTheme();
  }

  function updateTheme() {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  async function handleSignOut() {
    const response = await fetch('/api/signOut', {
      method: 'POST'
    });
    if (response.ok) {
      window.location.href = '/debugLogin';
    }
  }

</script>

<header class="h-14 border-b flex items-center px-4 justify-between bg-background">
  <div class="flex items-center gap-4">
    <h1 class="text-4xl font-chattie tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600"><a href="/">Chattie</a></h1>
    <span class="text-sm font-mono bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent animate-pulse [animation-duration:1s] [animation-iteration-count:3]">{fps} FPS</span>
    <!--
    <span class="text-sm text-gray-500">Width: {windowWidth}px</span>
    -->
  </div>

  <div class="flex items-center gap-4">
    <button 
      class="flex items-center gap-2 px-2 py-1 rounded bg-neutral-100 dark:bg-neutral-900 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors"
      on:click={toggleTheme}
      aria-label="Toggle theme"
    >
      <span class="text-sm">
        {isDarkMode ? 'Dark Mode' : 'Light Mode'}
      </span>
      {#if isDarkMode}
        <Sun class="w-5 h-5" />
      {:else}
        <Moon class="w-5 h-5" />
      {/if}
    </button>

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
              <span>Hey, {$page.data.user.name}</span>
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