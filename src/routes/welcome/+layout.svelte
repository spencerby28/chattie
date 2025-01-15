<script lang="ts">
    import { onMount } from 'svelte';
    import { Sun, Moon } from 'lucide-svelte';

    let isDarkMode = true;

    // Check system preference on mount
    onMount(() => {
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
</script>

<header class="fixed w-full top-0 z-50 bg-background text-gray-900 dark:text-white">
    <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center space-x-4">
            <a href="/" class="text-2xl bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600 font-chattie tracking-wide ">
                Chattie
            </a>
        </div>
        
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
    </div>
</header>

<main class="h-screen">
    <slot />
</main>