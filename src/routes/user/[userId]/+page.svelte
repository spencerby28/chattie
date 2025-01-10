<script lang="ts">
import { onMount } from 'svelte';
import type { PageData } from './$types';
import { browser } from '$app/environment';
import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
import { Permission, Role } from 'appwrite';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
import { Label } from "$lib/components/ui/label";
import { Switch } from "$lib/components/ui/switch";
import { Separator } from "$lib/components/ui/separator";
import { Button } from "$lib/components/ui/button";
import Avatar from "$lib/components/ui/avatar/Avatar.svelte";
import { Skeleton } from "$lib/components/ui/skeleton";

export let data: PageData;

let loading = true;
let filePreview: string | null = null;
let accountData: any;
let fileData: any;
let uploadStatus = '';
let selectedFile: File | null = null;
let localPreviewUrl: string | null = null;

// Notification preferences
let emailNotifications = false;
let pushNotifications = false;
let soundEnabled = false;

function getOptimizedAvatarUrl(fileId: string) {
    const { storage } = createBrowserClient();
    return storage.getFileView('avatars', fileId);
}

function handleFileSelect(e: Event) {
    const input = e.target as HTMLInputElement;
    selectedFile = input.files?.[0] || null;
    
    if (localPreviewUrl) {
        URL.revokeObjectURL(localPreviewUrl);
    }
    
    if (selectedFile) {
        localPreviewUrl = URL.createObjectURL(selectedFile);
    } else {
        localPreviewUrl = null;
    }
}

async function handleFileUpload() {
    if (!selectedFile || !accountData) return;
    
    try {
        uploadStatus = 'Uploading...';
        const { storage, account } = createBrowserClient();
        const fileId = crypto.randomUUID();
        
        try {
            const prefs = accountData.prefs || {};
            if (prefs.avatarId) {
                try {
                    await storage.deleteFile('avatars', prefs.avatarId);
                } catch (error) {
                    console.log('No existing avatar to delete');
                }
            }
        } catch (error) {
            console.log('Error deleting existing avatar:', error);
        }

        fileData = await storage.createFile(
            'avatars',
            fileId,
            selectedFile,
            [
                Permission.read(Role.users()),
                Permission.update(Role.user(accountData.$id)),
                Permission.delete(Role.user(accountData.$id))
            ]
        );
        
        const prefs = accountData.prefs || {};
        prefs.avatarId = fileId;
        await account.updatePrefs(prefs);
        
        await new Promise((resolve) => setTimeout(resolve, 500));
        
        try {
            await storage.getFile('avatars', fileId);
            filePreview = getOptimizedAvatarUrl(fileId);
            if (localPreviewUrl) {
                URL.revokeObjectURL(localPreviewUrl);
                localPreviewUrl = null;
            }
        } catch (error) {
            console.error('Error verifying uploaded file:', error);
        }
        
        accountData = await account.get();
        uploadStatus = 'Upload successful!';
        window.location.reload();
    } catch (error) {
        console.error('Upload failed:', error);
        uploadStatus = 'Upload failed: ' + (error as Error).message;
    }
}

async function updateNotificationPreferences() {
    try {
        const { account } = createBrowserClient();
        const prefs = accountData.prefs || {};
        prefs.notifications = {
            email: emailNotifications,
            push: pushNotifications,
            sound: soundEnabled
        };
        await account.updatePrefs(prefs);
        accountData = await account.get();
        window.location.reload();
    } catch (error) {
        console.error('Failed to update preferences:', error);
    }
}

onMount(async () => {
    if (browser) {
        try {
            const { account } = createBrowserClient();
            accountData = await account.get();
            
            // Load notification preferences
            const notificationPrefs = accountData.prefs?.notifications || {};
            emailNotifications = notificationPrefs.email || false;
            pushNotifications = notificationPrefs.push || false;
            soundEnabled = notificationPrefs.sound || false;
            
            const avatarId = accountData.prefs?.avatarId;
            if (avatarId) {
                filePreview = getOptimizedAvatarUrl(avatarId);
                try {
                    const { storage } = createBrowserClient();
                    fileData = await storage.getFile('avatars', avatarId);
                } catch (error) {
                    console.log('Error loading avatar:', error);
                    filePreview = null;
                    fileData = null;
                    
                    const prefs = accountData.prefs || {};
                    delete prefs.avatarId;
                    await account.updatePrefs(prefs);
                }
            } else {
                filePreview = null;
                fileData = null;
            }
            
            loading = false;
        } catch (error) {
            console.error('Client-side auth failed:', error);
            loading = false;
        }
    }
});

onMount(() => {
    return () => {
        if (localPreviewUrl) {
            URL.revokeObjectURL(localPreviewUrl);
        }
    };
});
</script>

<div class="container mx-auto py-8 max-w-3xl">
    <div class="mb-6">
        <Button variant="outline" href="/">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            Back to Workspaces
        </Button>
    </div>
    {#if loading}
        <div class="space-y-6">
            <Card>
                <CardHeader>
                    <Skeleton class="h-8 w-[200px]" />
                    <Skeleton class="h-4 w-[300px] mt-2" />
                </CardHeader>
                <CardContent>
                    <div class="flex items-center gap-6">
                        <Skeleton class="h-24 w-24 rounded-xl" />
                        <div class="space-y-2 flex-1">
                            <Skeleton class="h-4 w-[100px]" />
                            <Skeleton class="h-10 w-full" />
                            <Skeleton class="h-10 w-[120px]" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <Skeleton class="h-8 w-[250px]" />
                    <Skeleton class="h-4 w-[350px] mt-2" />
                </CardHeader>
                <CardContent>
                    <div class="space-y-4">
                        <div>
                            <Skeleton class="h-4 w-[60px] mb-2" />
                            <Skeleton class="h-4 w-[200px]" />
                        </div>
                        <div>
                            <Skeleton class="h-4 w-[60px] mb-2" />
                            <Skeleton class="h-4 w-[150px]" />
                        </div>
                        <div>
                            <Skeleton class="h-4 w-[100px] mb-2" />
                            <Skeleton class="h-4 w-[120px]" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    {:else}
        <div class="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Profile Settings</CardTitle>
                    <CardDescription>Manage your account settings and preferences</CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="flex items-center gap-6">
                        <Avatar 
                            src={localPreviewUrl || filePreview}
                            name={accountData?.name || 'User'}
                            size="xl"
                        />
                        <div class="flex-1 space-y-2">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-4">
                                    <Label for="avatar">Profile Picture</Label>
                                    {#if selectedFile}
                                        <span class="text-sm text-muted-foreground">{selectedFile.name}</span>
                                    {/if}
                                </div>
                                <Button 
                                    variant="outline"
                                    on:click={handleFileUpload}
                                    disabled={!selectedFile}
                                >
                                    Upload Avatar
                                </Button>
                            </div>

                            <input
                                id="avatar"
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
                                    transition-colors"
                                on:change={handleFileSelect}
                            />
                            
                            {#if uploadStatus}
                                <p class="text-sm" class:text-destructive={uploadStatus.includes('failed')} class:text-green-500={uploadStatus.includes('successful')}>
                                    {uploadStatus}
                                </p>
                            {/if}
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Account Information</CardTitle>
                    <CardDescription>Your account details and workspace information</CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="space-y-4">
                        <div>
                            <Label>Email</Label>
                            <p class="text-sm text-muted-foreground">{accountData?.email}</p>
                        </div>
                        <div>
                            <Label>Name</Label>
                            <p class="text-sm text-muted-foreground">{accountData?.name}</p>
                        </div>
                        <div>
                            <Label>Workspaces</Label>
                            <p class="text-sm text-muted-foreground">
                                {data.workspaces?.length || 0} workspace{data.workspaces?.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
<!--
            <Card>
                <CardHeader>
                    <CardTitle>Notification Preferences</CardTitle>
                    <CardDescription>Customize how you receive notifications</CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="space-y-4">
                        <div class="flex items-center justify-between">
                            <div class="space-y-0.5">
                                <Label>Email Notifications</Label>
                                <p class="text-sm text-muted-foreground">Receive notifications via email</p>
                            </div>
                            <Switch
                                checked={emailNotifications}
                                onCheckedChange={(checked) => {
                                    emailNotifications = checked;
                                    updateNotificationPreferences();
                                }}
                            />
                        </div>
                        <Separator />
                        <div class="flex items-center justify-between">
                            <div class="space-y-0.5">
                                <Label>Push Notifications</Label>
                                <p class="text-sm text-muted-foreground">Receive push notifications in your browser</p>
                            </div>
                            <Switch
                                checked={pushNotifications}
                                onCheckedChange={(checked) => {
                                    pushNotifications = checked;
                                    updateNotificationPreferences();
                                }}
                            />
                        </div>
                        <Separator />
                        <div class="flex items-center justify-between">
                            <div class="space-y-0.5">
                                <Label>Sound</Label>
                                <p class="text-sm text-muted-foreground">Play sound for new messages</p>
                            </div>
                            <Switch
                                checked={soundEnabled}
                                onCheckedChange={(checked) => {
                                    soundEnabled = checked;
                                    updateNotificationPreferences();
                                }}
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>
            -->
        </div>
    {/if}
</div>
