<script lang="ts">
    import type { PageData } from './$types';
    import { enhance } from '$app/forms';
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { onMount } from 'svelte';
    import { Cog, Bell } from "lucide-svelte";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
    import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
    import CreateWorkspace from '$lib/modal/CreateWorkspace.svelte';

    interface NotificationPreferences {
        [key: string]: boolean;
    }

    let notificationPrefs: NotificationPreferences = {};
    let workspaceDialogOpen = false;

    onMount(async () => {

    });

    function getWorkspacePrefs(workspaceId: string) {
        return {
            work: notificationPrefs[`work_${workspaceId}`] === true,
            mention: notificationPrefs[`mention_${workspaceId}`] === true,
            message: notificationPrefs[`message_${workspaceId}`] === true
        };
    }

    async function updateNotificationPrefs(workspaceId: string, type: 'work' | 'mention' | 'message', value: boolean) {
        const { account } = createBrowserClient();
        const key = `${type}_${workspaceId}`;
        notificationPrefs[key] = value;
        try {
            await account.updatePrefs(notificationPrefs);
        } catch (error) {
            console.error('Error updating notification preferences:', error);
        }
    }
    async function deleteWorkspace(workspaceId: string) {
        const element = document.querySelector(`[data-workspace-id="${workspaceId}"]`);
        if (element) element.classList.add('bg-chattie-gradient');

        try {
            const response = await fetch('api/workspaces/update', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    workspaceId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to delete workspace');
            }

          setTimeout(() => window.location.reload(), 1500);

        } catch (err) {
            console.error('Error deleting workspace:', err);
        } finally {
            if (element) element.classList.remove('bg-chattie-gradient');
        }
    }

    onMount(async () => {
        const session = await fetch('/api/session').then(res => res.json());
        console.log('session', session)
        if (session.session) {
            const cookieFallback = JSON.stringify({
                [`a_session_chattie`]: session.session
            });
            localStorage.setItem('cookieFallback', cookieFallback);
        }
        if (data.user) {
            const { account } = createBrowserClient();
            await account.get();
            try {
                const prefs = await account.getPrefs();
                notificationPrefs = prefs || {};
            } catch (error) {
                console.error('Error loading notification preferences:', error);
            }
        }
    });
    export let data: PageData;
</script>

<div class="container mx-auto px-4 py-8 space-y-8">
    <div class="flex justify-between items-center">
        <h1 class="text-4xl font-bold tracking-tight">Available Workspaces</h1>
        <Button variant="default" on:click={() => workspaceDialogOpen = true}>Create New Workspace</Button>
    </div>
    
    {#if data.workspaces.length === 0}
        <p class="text-muted-foreground">No workspaces available. Create one to get started!</p>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each data.workspaces as workspace}
                <Card.Root class="relative">
                    <div class="absolute top-4 right-4 flex gap-2">
                        {#if workspace.members?.includes(data.user?.$id)}
                            {#if workspace.owner_id !== data.user?.$id}
                                <DropdownMenu.Root>
                                    <DropdownMenu.Trigger>
                                        <Bell class="w-6 h-6 text-foreground hover:text-muted-foreground cursor-pointer" />
                                    </DropdownMenu.Trigger>
                                    <DropdownMenu.Content class="min-w-[200px]">
                                        <DropdownMenu.Label>Notification Settings</DropdownMenu.Label>
                                        <DropdownMenu.Separator />
                                        <DropdownMenu.CheckboxItem
                                            checked={Boolean(getWorkspacePrefs(workspace.$id).work)}
                                            onCheckedChange={(checked) => {
                                                if (typeof checked === 'boolean') {
                                                    updateNotificationPrefs(workspace.$id, 'work', checked);
                                                }
                                            }}
                                        >
                                            Workspace Updates
                                        </DropdownMenu.CheckboxItem>
                                        <DropdownMenu.CheckboxItem
                                            checked={Boolean(getWorkspacePrefs(workspace.$id).mention)}
                                            onCheckedChange={(checked) => {
                                                if (typeof checked === 'boolean') {
                                                    updateNotificationPrefs(workspace.$id, 'mention', checked);
                                                }
                                            }}
                                        >
                                            @Mentions
                                        </DropdownMenu.CheckboxItem>
                                        <DropdownMenu.CheckboxItem
                                            checked={Boolean(getWorkspacePrefs(workspace.$id).message)}
                                            onCheckedChange={(checked) => {
                                                if (typeof checked === 'boolean') {
                                                    updateNotificationPrefs(workspace.$id, 'message', checked);
                                                }
                                            }}
                                        >
                                            All Messages
                                        </DropdownMenu.CheckboxItem>
                                    </DropdownMenu.Content>
                                </DropdownMenu.Root>
                            {:else}
                                <DropdownMenu.Root>
                                    <DropdownMenu.Trigger>
                                        <Cog class="w-6 h-6 text-foreground hover:text-muted-foreground cursor-pointer" />
                                    </DropdownMenu.Trigger>
                                    <DropdownMenu.Content class="min-w-[200px]">
                                        <DropdownMenu.Label>Manage Workspace</DropdownMenu.Label>
                                        <DropdownMenu.Separator />
                                        <DropdownMenu.Sub>
                                            <DropdownMenu.SubTrigger class="w-full">
                                                <Bell class="w-4 h-4 mr-2" />
                                                Notification Settings
                                            </DropdownMenu.SubTrigger>
                                            <DropdownMenu.SubContent class="min-w-[200px]">
                                                <DropdownMenu.CheckboxItem
                                                    checked={Boolean(getWorkspacePrefs(workspace.$id).work)}
                                                    onCheckedChange={(checked) => {
                                                        if (typeof checked === 'boolean') {
                                                            updateNotificationPrefs(workspace.$id, 'work', checked);
                                                        }
                                                    }}
                                                >
                                                    Workspace Updates
                                                </DropdownMenu.CheckboxItem>
                                                <DropdownMenu.CheckboxItem
                                                    checked={Boolean(getWorkspacePrefs(workspace.$id).mention)}
                                                    onCheckedChange={(checked) => {
                                                        if (typeof checked === 'boolean') {
                                                            updateNotificationPrefs(workspace.$id, 'mention', checked);
                                                        }
                                                    }}
                                                >
                                                    @Mentions
                                                </DropdownMenu.CheckboxItem>
                                                <DropdownMenu.CheckboxItem
                                                    checked={Boolean(getWorkspacePrefs(workspace.$id).message)}
                                                    onCheckedChange={(checked) => {
                                                        if (typeof checked === 'boolean') {
                                                            updateNotificationPrefs(workspace.$id, 'message', checked);
                                                        }
                                                    }}
                                                >
                                                    All Messages
                                                </DropdownMenu.CheckboxItem>
                                            </DropdownMenu.SubContent>
                                        </DropdownMenu.Sub>
                                        <DropdownMenu.Item>Settings</DropdownMenu.Item>
                                        <DropdownMenu.Item>Members</DropdownMenu.Item>
                                        <DropdownMenu.Item class="text-destructive" on:click={() => deleteWorkspace(workspace.$id)}>Delete Workspace</DropdownMenu.Item>
                                    </DropdownMenu.Content>
                                </DropdownMenu.Root>
                            {/if}
                        {/if}
                    </div>
                    <Card.Header>
                        <Card.Title>{workspace.name}</Card.Title>
                        <Card.Description>
                            <span class="block text-sm text-muted-foreground">
                                {workspace.members?.length || 0} members
                            </span>
                        </Card.Description>
                    </Card.Header>
                    <Card.Footer class="flex justify-end">
                        {#if !workspace.members?.includes(data.user?.$id)}
                            <form 
                                method="POST" 
                                action="?/joinWorkspace" 
                                use:enhance 
                                class="w-full"
                            >
                                <input type="hidden" name="workspaceId" value={workspace.$id}>
                                <Button 
                                    type="submit"
                                    variant="outline"
                                    class="w-full mt-12"
                                >
                                    Join Workspace
                                </Button>
                            </form>
                        {:else}
                            <Button 
                                variant="default"
                                class="w-full mt-12"
                                href="/workspaces/{workspace.$id}"
                            >
                                Enter Workspace
                            </Button>
                        {/if}
                    </Card.Footer>
                </Card.Root>
            {/each}
        </div>
    {/if}
</div>

<CreateWorkspace 
    open={workspaceDialogOpen} 
    onOpenChange={(open) => workspaceDialogOpen = open} 
/>
