<script lang="ts">
    import type { PageData } from './$types';
    import { enhance } from '$app/forms';
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { onMount } from 'svelte';
    import { Cog, Bell } from "lucide-svelte";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
    import * as AlertDialog from "$lib/components/ui/alert-dialog";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
    import { goto } from '$app/navigation';

    interface NotificationPreferences {
        [key: string]: boolean;
    }

    let notificationPrefs: NotificationPreferences = {};
    let loading = false;
    let workspaceDialogOpen = false;

    onMount(async () => {
        if (data.user) {
            const { account } = createBrowserClient();
            try {
                const prefs = await account.getPrefs();
                notificationPrefs = prefs || {};
            } catch (error) {
                console.error('Error loading notification preferences:', error);
            }
        }
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

    async function handleCreateWorkspace(event: SubmitEvent) {
        event.preventDefault();
        loading = true;

        const formData = new FormData(event.target as HTMLFormElement);
        const name = formData.get('workspace_name') as string;
        const description = formData.get('workspace_description') as string;
        const visibility = formData.get('visibility') as string;
        console.log(name, description, visibility);
        try {
            const response = await fetch('/api/workspaces/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description,
                    visibility
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create workspace');
            }

            const { workspaceId } = await response.json();
            workspaceDialogOpen = false;
            await goto(`/workspaces/${workspaceId}`);
        } catch (error) {
            console.error('Error creating workspace:', error);
        } finally {
            loading = false;
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
                                        <Bell class="w-6 h-6 text-black hover:text-gray-700 cursor-pointer" />
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
                                        <Cog class="w-6 h-6 text-black hover:text-gray-700 cursor-pointer" />
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
                                        <DropdownMenu.Item class="text-destructive">Delete Workspace</DropdownMenu.Item>
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
                            <span class="block text-xs text-muted-foreground">
                                Owner ID: {workspace.owner_id}
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

<AlertDialog.Root open={workspaceDialogOpen} onOpenChange={open => workspaceDialogOpen = open}>
    <AlertDialog.Content>
        <AlertDialog.Header>
            <AlertDialog.Title>Create New Workspace</AlertDialog.Title>
            <AlertDialog.Description>
                Fill in the details below to create a new workspace.
            </AlertDialog.Description>
        </AlertDialog.Header>

        <form on:submit={handleCreateWorkspace} class="space-y-6">
            <div class="space-y-2">
                <Label for="name">Workspace Name</Label>
                <Input
                    type="text"
                    id="workspace_name"
                    name="workspace_name"
                    required
                    placeholder="Enter workspace name"
                />
            </div>

            <div class="space-y-2">
                <Label for="description">Description</Label>
                <textarea
                    id="workspace_description"
                    name="workspace_description"
                    rows="3"
                    class="w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-blue-500 dark:border-gray-700"
                    placeholder="Enter workspace description"
                ></textarea>
            </div>

            <div class="space-y-2">
                <Label>Visibility</Label>
                <div class="flex gap-4">
                    <label class="flex items-center text-foreground">
                        <input
                            type="radio"
                            name="visibility"
                            value="public"
                            class="mr-2 accent-foreground"
                            checked
                        />
                        Public
                    </label>
                    <label class="flex items-center text-foreground">
                        <input
                            type="radio"
                            name="visibility"
                            value="private"
                            class="mr-2 accent-foreground"
                        />
                        Private
                    </label>
                </div>
            </div>

            <AlertDialog.Footer>
                <AlertDialog.Cancel asChild>
                    <Button type="button" variant="outline" on:click={() => workspaceDialogOpen = false}>Cancel</Button>
                </AlertDialog.Cancel>
                <Button type="submit" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Workspace'}
                </Button>
            </AlertDialog.Footer>
        </form>
    </AlertDialog.Content>
</AlertDialog.Root>
