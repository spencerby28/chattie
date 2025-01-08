<script lang="ts">
    import { enhance } from '$app/forms';
</script>

<svelte:head>
    <title>Welcome to Chattie - Your AI-Powered Workspace</title>
</svelte:head>

<main class="h-[calc(100vh-4rem)] bg-gradient-to-b from-gray-50 to-white dark:from-gray-950 dark:to-black text-gray-900 dark:text-white">
    <!-- Hero Section -->
    <section class="container mx-auto px-6 h-2/5 flex items-center mt-12">
        <div class="text-center w-full">
            <h1 class="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                Welcome to <span class="font-chattie tracking-wider ml-2 text-6xl">Chattie</span>
            </h1>
            <p class="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-xl mx-auto">
                Chat like it's the 21st century - AI powered conversations about anything and everything you can imagine.
            </p>
            <div class="flex gap-6 justify-center">
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

    <!-- Features Section -->
    <section class="container mx-auto px-6 h-3/5">
        <div class="grid md:grid-cols-3 gap-6 h-full items-center">
            <div class="text-center p-4 rounded-xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm shadow-lg">
                <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold mb-2">AI-Powered Chat</h3>
                <p class="text-md text-gray-600 dark:text-gray-400">Engage in intelligent conversations for learning, entertainment, and exploring new ideas.</p>
            </div>

            <div class="text-center p-4 rounded-xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm shadow-lg">
                <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold mb-2">Invite Friends</h3>
                <p class="text-md text-gray-600 dark:text-gray-400">Chat with friends and invite others to join your conversations in real-time.</p>
            </div>

            <div class="text-center p-4 rounded-xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm shadow-lg">
                <div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold mb-2">Secure & Private</h3>
                <p class="text-md text-gray-600 dark:text-gray-400">Control visibility and privacy settings for each conversation with enterprise-grade security.</p>
            </div>
        </div>
    </section>
</main>

<style>
    /* Add any custom styles here */
</style>