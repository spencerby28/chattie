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

    // Hardcoded avatar options
    const defaultAvatars = [
        'acd1b47b-923a-4b3b-b3d5-4f8477322ec4',
        'b028239c-6769-4386-8c9c-f55161b2c6ef', 
        'c907105b-3c66-4a41-af4f-769751568740',
        'c491e057-dd58-4d22-85c2-0801d469319b',
        'f509c043-1ac3-4640-ac6f-5e2b5d09c3bf',
        '00fbfeee-b33b-4eb3-b793-72806baa1038'
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
                                size="full"
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
                                class="relative aspect-square w-24 rounded-xl overflow-hidden hover:ring-2 hover:ring-primary transition-all
                                       {selectedAvatar === 'cc7f49c5-b0ba-4caa-8293-cbd1ea7153dc' ? 'ring-2 ring-primary' : ''}"
                                on:click={() => handleAvatarSelection('cc7f49c5-b0ba-4caa-8293-cbd1ea7153dc')}
                            >
                                <Avatar 
                                    src={getAvatarUrl('cc7f49c5-b0ba-4caa-8293-cbd1ea7153dc')}
                                    name="Austen Avatar"
                                    size="full"
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
            <Button variant="default" href="/" disabled={!selectedAvatar}>
                Continue to Workspaces
            </Button>
        </div>
    </div>
</div>
