<script lang="ts">
    import { enhance } from '$app/forms';
    import { onMount } from 'svelte';

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

    function updateTheme() {
        const tweet = document.querySelector('.twitter-tweet');
        if (tweet) {
            tweet.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
        }
    }
</script>

<svelte:head>
    <title>Welcome to Chattie - Your AI-Powered Workspace</title>
</svelte:head>

<div class="bg-gradient-to-b from-gray-50 to-white dark:from-gray-950 dark:to-black text-gray-900 dark:text-white overflow-y-visible h-screen">
    <div class="container mx-auto px-6 h-full flex items-center">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
            <!-- Hero Section -->
            <section class="flex flex-col justify-center">
                <div>
                    <h1 class="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                        Welcome to <span class="font-chattie tracking-wider ml-2 text-5xl md:text-6xl">Chattie</span>
                    </h1>
                    <p class="text-lg text-gray-600 dark:text-gray-300 mb-6 max-w-xl">
                        Chat like it's the 21st century - AI powered conversations about anything and everything you can imagine.
                    </p>
                    <div class="flex gap-6">
                        <a href="/register" class="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors">
                            Get Started
                        </a>
                        <a
                            href="/login"
                            class="px-8 py-3 rounded-lg font-semibold transition-colors bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
                        >
                            Sign In
                        </a>
                    </div>
                </div>
            </section>

            <!-- Tweet Section -->
            <section class="flex items-center justify-center">
                <blockquote class="twitter-tweet" data-dnt="true" data-theme={isDarkMode ? 'dark' : 'light'}>
                    <p lang="en" dir="ltr">Deep dive into Chattie AI MVP <br><br>Built in ~15 hours of work<br><br>1. /commands<br><br>Use /summarize or /analyze to get information about a current thread <a href="https://t.co/M9VhWfu0tX">pic.twitter.com/M9VhWfu0tX</a></p>
                    &mdash; mojo ☁️ (@toeachiloveyou) <a href="https://twitter.com/toeachiloveyou/status/1879334314074407360?ref_src=twsrc%5Etfw">January 15, 2025</a>
                </blockquote>
                <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            </section>
        </div>
    </div>
</div>

<style>
    /* Add any custom styles here */
</style>