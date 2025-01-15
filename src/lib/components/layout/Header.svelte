<script lang="ts">
  import { page } from '$app/stores';
  import { Button } from "$lib/components/ui/button";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
  import * as AlertDialog from "$lib/components/ui/alert-dialog";
  import { UserCircle, Sun, Moon, Search as SearchIcon, Bot } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import Avatar from '$lib/components/ui/avatar/Avatar.svelte';
  import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
  import { mode } from '$lib/stores/mode';
  import { presenceStore } from '$lib/stores/presence';

  // Import our global search store & initialization
  import { searchOpen, initializeSearch } from '$lib/components/features/search/search';
  import Search from '$lib/components/features/search/Search.svelte';

  let fps = 0;
  let frameCount = 0;
  let lastTime = performance.now();
  let windowWidth: number;
  let isDarkMode = true;
  let avatarUrl: string | null = null;
  let showAIDialog = false;

  // Derived from user presence
  $: userPresence = $page.data.user ? $presenceStore[$page.data.user.$id] : null;

  // Update avatar URL on data changes
  $: {
    if ($page.data.user?.prefs?.avatarId) {
      const { storage } = createBrowserClient();
      avatarUrl = storage.getFileView('avatars', $page.data.user.prefs.avatarId);
    } else {
      avatarUrl = null;
    }
  }

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
    // Initialize search watchers once globally
    initializeSearch();

    handleResize();
    window.addEventListener('resize', handleResize);
    requestAnimationFrame(updateFPS);

    // Check system preference on mount
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    isDarkMode =
      localStorage.getItem('theme') === 'dark' ||
      (!localStorage.getItem('theme') && prefersDark);
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

  // Reinitialize search when workspace changes
  $: if ($page.params.workspaceId) {
    initializeSearch();
  }

  function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    mode.set(isDarkMode ? 'dark' : 'light');
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

  // Manually open search
  function openSearch() {
    searchOpen.set(true);
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
      class="flex items-center gap-2 px-2 py-1 rounded bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-800/30 transition-colors"
      on:click={() => showAIDialog = true}
    >
      <Bot class="w-4 h-4" />
      <span class="text-sm">AI ON</span>
    </button>

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

    <button
      class="flex items-center gap-2 px-4 py-1 rounded bg-neutral-100 dark:bg-neutral-900 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors min-w-[200px]"
      on:click={openSearch}
      aria-label="Open search"
    >
      <SearchIcon class="w-4 h-4" />
      <span class="text-sm flex-1 text-left">Search</span>
      <kbd class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
        <span class="text-xs">⌘</span>K
      </kbd>
    </button>

    {#if $page.data.user}
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          <div class="flex items-center gap-2 hover:bg-chattie-gradient rounded-xl p-1 cursor-pointer">
            <div class="relative">
              <Avatar 
                src={avatarUrl || $page.data.user.avatarUrl || undefined}
                fallback={$page.data.user.name?.[0]?.toUpperCase()}
                name={$page.data.user.name}
                size="md"
              />
              {#if userPresence}
                <div class="absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-background" class:bg-green-500={userPresence.baseStatus === 'online'} class:bg-yellow-500={userPresence.baseStatus === 'away'} class:bg-gray-500={userPresence.baseStatus === 'offline'}></div>
              {/if}
            </div>
          </div>
        </DropdownMenu.Trigger>
        <DropdownMenu.Content>
          <DropdownMenu.Label>
            <div class="flex flex-col">
              <span>Hey, {$page.data.user.name}</span>
              <span class="text-xs text-muted-foreground">{$page.data.user.email}</span>
              {#if userPresence?.customStatus}
                <span class="text-xs text-muted-foreground mt-1">
                  {userPresence.customStatus.emoji} {userPresence.customStatus.text}
                </span>
              {/if}
            </div>
          </DropdownMenu.Label>
          <DropdownMenu.Separator />
          <DropdownMenu.Item href="/user/{$page.data.user.$id}">
            Manage Settings
          </DropdownMenu.Item>
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

  <!-- The global Search Dialog is rendered here -->
  <Search />

  <!-- AI Commands Dialog -->
  <AlertDialog.Root open={showAIDialog}>
    <AlertDialog.Content>
      <AlertDialog.Header>
        <AlertDialog.Title>AI Commands Available</AlertDialog.Title>
        <AlertDialog.Description>
          <div class="space-y-4 mt-2">
            <div class="space-y-2">
              <h2 class="font-semibold">/analyze</h2>
              <p class="text-sm text-muted-foreground">Analyze the current conversation or selected text for key insights and patterns.</p>
            </div>
            
            <div class="space-y-2">
              <h2 class="font-semibold">/summarize</h2>
              <p class="text-sm text-muted-foreground">Generate a concise summary of the conversation or selected content.</p>
            </div>
            <div class="space-y-2">
              <h2 class="font-semibold">@AI User</h2>
              <p class="text-sm text-muted-foreground">Mention the AI user in your message to get personalized assistance with your tasks.</p>
            </div>

            <div class="space-y-2">
              <h2 class="font-semibold">@Chattie Bot</h2>
              <p class="text-sm text-muted-foreground">Mention Chattie Bot to ask general questions and get helpful responses.</p>
            </div>
          </div>
        </AlertDialog.Description>
      </AlertDialog.Header>
      <AlertDialog.Footer>
        <AlertDialog.Cancel on:click={() => showAIDialog = false}>
          Got it
        </AlertDialog.Cancel>
      </AlertDialog.Footer>
    </AlertDialog.Content>
  </AlertDialog.Root>
</header>