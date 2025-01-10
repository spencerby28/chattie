<script lang="ts">
    import { onMount } from 'svelte';
    import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
    import { Permission, Role } from 'appwrite';
    import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";

    let files: File[] = [];
    let uploadStatuses: {file: string, status: string, id?: string}[] = [];
    let accountData: any;
    let dragOver = false;

    onMount(async () => {
        const { account } = createBrowserClient();
        accountData = await account.get();
    });

    function handleDragOver(e: DragEvent) {
        e.preventDefault();
        dragOver = true;
    }

    function handleDragLeave() {
        dragOver = false;
    }

    function handleDrop(e: DragEvent) {
        e.preventDefault();
        dragOver = false;
        
        const droppedFiles = Array.from(e.dataTransfer?.files || []);
        files = [...files, ...droppedFiles.filter(file => file.type.startsWith('image/'))];
        
        // Initialize upload statuses for new files
        droppedFiles.forEach(file => {
            uploadStatuses = [...uploadStatuses, {
                file: file.name,
                status: 'pending'
            }];
        });

        processUploads();
    }

    async function processUploads() {
        if (!accountData) return;

        const { storage } = createBrowserClient();

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const statusIndex = uploadStatuses.findIndex(s => s.file === file.name);
            
            try {
                uploadStatuses[statusIndex].status = 'uploading';
                uploadStatuses = [...uploadStatuses];

                const fileId = crypto.randomUUID();
                await storage.createFile(
                    'avatars',
                    fileId,
                    file,
                    [
                        Permission.read(Role.users()),
                        Permission.update(Role.user(accountData.$id)),
                        Permission.delete(Role.user(accountData.$id))
                    ]
                );

                uploadStatuses[statusIndex].status = 'complete';
                uploadStatuses[statusIndex].id = fileId;
                uploadStatuses = [...uploadStatuses];

            } catch (error) {
                uploadStatuses[statusIndex].status = 'failed';
                uploadStatuses = [...uploadStatuses];
                console.error('Upload failed:', error);
            }
        }

        files = [];
    }
</script>

<div class="container mx-auto py-8 max-w-3xl">
    <Card>
        <CardHeader>
            <CardTitle>Batch Image Upload</CardTitle>
            <CardDescription>Drag and drop multiple images to upload them</CardDescription>
        </CardHeader>
        <CardContent>
            <div
                class="border-2 border-dashed rounded-lg p-8 text-center transition-colors
                       {dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}"
                on:dragover={handleDragOver}
                on:dragleave={handleDragLeave}
                on:drop={handleDrop}
            >
                <p class="text-muted-foreground">
                    Drag and drop images here
                </p>
            </div>

            {#if uploadStatuses.length > 0}
                <div class="mt-8 space-y-4">
                    <h3 class="font-semibold">Upload Status</h3>
                    {#each uploadStatuses as status}
                        <div class="flex items-center justify-between p-4 bg-muted rounded-lg">
                            <span class="text-sm truncate max-w-[200px]">{status.file}</span>
                            <div class="flex items-center gap-4">
                                {#if status.id}
                                    <code class="text-xs bg-primary/10 px-2 py-1 rounded">{status.id}</code>
                                {/if}
                                <span class="text-sm" class:text-yellow-500={status.status === 'uploading'}
                                                    class:text-green-500={status.status === 'complete'}
                                                    class:text-destructive={status.status === 'failed'}>
                                    {status.status}
                                </span>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </CardContent>
    </Card>
</div>
