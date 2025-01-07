<script lang="ts">
    import { enhance } from '$app/forms';

    const testUsers = [
        { id: 'user1', name: 'User 1' },
        { id: 'user2', name: 'User 2' },
        { id: 'user3', name: 'User 3' },
        { id: 'user4', name: 'User 4' },
        { id: 'user5', name: 'User 5' }
    ];
</script>

<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Debug Login</h1>
    <div class="max-w-md mx-auto">
        <div class="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-6">
            <p class="text-yellow-700">⚠️ This page is for development purposes only.</p>
        </div>
        
        <div class="space-y-4">
            {#each testUsers as user}
                <form 
                    method="POST" 
                    action="?/debugLogin" 
                    use:enhance 
                    class="block w-full"
                >
                    <input type="hidden" name="userId" value={user.id}>
                    <button 
                        type="submit"
                        class="w-full px-4 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-left"
                    >
                        Login as {user.name}
                        <span class="block text-sm opacity-75">ID: {user.id}</span>
                    </button>
                </form>
            {/each}
        </div>

        <div class="mt-8">
            <a 
                href="/login" 
                class="text-blue-600 hover:text-blue-800 transition-colors"
            >
                ← Back to normal login
            </a>
        </div>
    </div>
</div>`
} 