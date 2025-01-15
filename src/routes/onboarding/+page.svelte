<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
    import { Permission, Role } from 'appwrite';
    import * as Card from "$lib/components/ui/card";
    import { Label } from "$lib/components/ui/label";
    import { Button } from "$lib/components/ui/button";
    import { Separator } from "$lib/components/ui/separator";
    import Avatar from "$lib/components/ui/avatar/Avatar.svelte";
    import { Progress } from "$lib/components/ui/progress";
    import { goto } from '$app/navigation';

    // Hardcoded avatar options
    const defaultAvatars = [
        'db3b77f7-d4f3-44e3-b940-696012ac2040',
        'a5cb1902-6c3e-463f-acc8-55f480a12b23', 
        '937bb454-585d-49b5-b1f0-fda41e137824',
        '78663099-e7bb-4772-b99e-a6553764fc1a',
        'b72170d3-5dc2-4238-87d0-7d1299232451',
        '6858db1b-951c-4722-bf6e-a9d931a4499b'
    ];

    let selectedAvatar: string | null = null;
    let customFile: File | null = null;
    let uploadStatus = '';
    let accountData: any;
    let progress = 33; // First step of onboarding
    let hasUploaded = false;
    let showAusten = false;

    function handleFileSelect(e: Event) {
        const input = e.target as HTMLInputElement;
        customFile = input.files?.[0] || null;
        if (customFile) {
            hasUploaded = false; // Reset upload state when new file selected
        }
    }

    async function handleAvatarSelection(avatarId: string) {
        selectedAvatar = avatarId;
        hasUploaded = false; // Reset upload state when selecting preset avatar
        try {
            const { account } = createBrowserClient();
            
            const prefs = accountData?.prefs || {};
            prefs.avatarId = avatarId;
            await account.updatePrefs(prefs);
            uploadStatus = 'Avatar selected successfully!';
        } catch (error) {
            console.error('Failed to update avatar:', error);
            uploadStatus = 'Failed to select avatar';
        }
    }

    async function handleCustomUpload() {
        if (!customFile || !accountData) return;
        
        try {
            uploadStatus = 'Uploading...';
            const { storage, account } = createBrowserClient();
            const fileId = crypto.randomUUID();
            
            // Delete existing avatar if present
            try {
                const prefs = accountData.prefs || {};
                if (prefs.avatarId) {
                    await storage.deleteFile('avatars', prefs.avatarId);
                }
            } catch (error) {
                console.log('No existing avatar to delete');
            }

            // Upload new avatar
            await storage.createFile(
                'avatars',
                fileId,
                customFile,
                [
                    Permission.read(Role.users()),
                    Permission.update(Role.user(accountData.$id)),
                    Permission.delete(Role.user(accountData.$id))
                ]
            );
            
            const prefs = accountData.prefs || {};
            prefs.avatarId = fileId;
            await account.updatePrefs(prefs);
            
            uploadStatus = 'Upload successful!';
            selectedAvatar = fileId;
            hasUploaded = true;
        } catch (error) {
            console.error('Upload failed:', error);
            uploadStatus = 'Upload failed: ' + (error as Error).message;
        }
    }

    function getAvatarUrl(avatarId: string) {
        const { storage } = createBrowserClient();
        return storage.getFileView('avatars', avatarId);
    }

    function handleContinue() {
        if (selectedAvatar) {
            goto('/');
        }
    }

    onMount(async () => {
        const session = await fetch('/api/session').then(res => res.json());
        if (session.session) {
            const cookieFallback = JSON.stringify({
                [`a_session_chattie`]: session.session
            });
            localStorage.setItem('cookieFallback', cookieFallback);
        }

        if (browser) {
            const { account } = createBrowserClient();
            accountData = await account.get();
            console.log(accountData);
            if (accountData?.prefs?.avatarId) {
                selectedAvatar = accountData.prefs.avatarId;
                hasUploaded = true;
            }
        }
    });
</script>

<div class="container max-w-4xl mx-auto px-4 py-8">
    <div class="text-center mb-12">
        <h1 class="text-5xl font-bold bg-chattie-gradient bg-clip-text text-transparent mb-4">
            Welcome to <span class="font-chattie text-6xl tracking-wider">Chattie!</span>
        </h1>
        <p class="text-xl text-muted-foreground">Let's get your profile set up and ready to go</p>
    </div>

    <div class="space-y-8">
        <Card.Root>
            <Card.Header>
                <Card.Title>Choose Your Avatar</Card.Title>
                <Card.Description>Select from our collection or upload your own</Card.Description>
            </Card.Header>
            <Card.Content>
                <div class="grid grid-cols-3 md:grid-cols-6 gap-4 mb-8">
                    {#each defaultAvatars as avatarId}
                        <button
                            class="relative aspect-square rounded-xl overflow-hidden hover:ring-2 hover:ring-primary transition-all
                                   {selectedAvatar === avatarId ? 'ring-2 ring-primary' : ''}"
                            on:click={() => handleAvatarSelection(avatarId)}
                        >
                            <Avatar 
                                src={getAvatarUrl(avatarId)}
                                name="Default Avatar"
                                size="xl"
                            />
                        </button>
                    {/each}
                </div>

                <Separator class="my-8" />

                <div class="space-y-4">
                    <Label>Or upload your own</Label>
                    <div class="flex gap-4">
                        <input
                            type="file"
                            accept="image/*"
                            class="block w-full text-sm text-slate-500
                                    file:mr-4 file:py-2 file:px-4
                                    file:rounded-full file:border-0
                                    file:text-sm file:font-semibold
                                    file:bg-accent file:text-accent-foreground
                                    file:cursor-pointer
                                    hover:file:bg-accent/90
                                    cursor-pointer
                                    hover:text-slate-600
                                    transition-colors
                                    disabled:opacity-50 disabled:cursor-not-allowed"
                            on:change={handleFileSelect}
                        />
                        <Button 
                            variant="default"
                            disabled={!customFile}
                            on:click={handleCustomUpload}
                        >
                            Upload
                        </Button>
                    </div>
                    {#if uploadStatus}
                        <p class="text-sm" class:text-destructive={uploadStatus.includes('failed')} class:text-green-500={uploadStatus.includes('successful')}>
                            {uploadStatus}
                        </p>
                    {/if}
                    <div class="flex flex-col items-center gap-4">
                        <button 
                            class="text-xs text-muted-foreground hover:text-foreground transition-colors"
                            on:click={() => showAusten = !showAusten}
                        >
                            Or go Austen mode...
                        </button>
                        {#if showAusten}
                            <button
                                class="relative aspect-square rounded-xl hover:ring-2 hover:ring-primary transition-all
                                       {selectedAvatar === 'f7f14697-8c86-4682-821c-f1b0c6691a3a' ? 'ring-2 ring-primary' : ''}"
                                on:click={() => handleAvatarSelection('f7f14697-8c86-4682-821c-f1b0c6691a3a')}
                            >
                                <Avatar 
                                    src={getAvatarUrl('f7f14697-8c86-4682-821c-f1b0c6691a3a')}
                                    name="Austen Avatar"
                                    size="xl"
                                />
                            </button>
                        {/if}
                    </div>
                </div>
            </Card.Content>
        </Card.Root>

        <!-- Placeholder for future components -->
        <Card.Root class="opacity-50">
            <Card.Header>
                <Card.Title>Choose Your Interests</Card.Title>
                <Card.Description>Coming soon - Select topics you'd like to discuss</Card.Description>
            </Card.Header>
            <Card.Content>
                <div class="h-32 flex items-center justify-center border-2 border-dashed rounded-lg">
                    <p class="text-muted-foreground">Interest selection coming soon...</p>
                </div>
            </Card.Content>
        </Card.Root>
        <div class="flex justify-end">
            <Button variant="default" disabled={!selectedAvatar} on:click={handleContinue}>
                Continue to Workspaces
            </Button>
        </div>
    </div>
</div>
