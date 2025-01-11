<script lang="ts">
    import * as AlertDialog from "$lib/components/ui/alert-dialog";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { Button } from "$lib/components/ui/button";
    import { toast } from "svelte-sonner";
    import { createBrowserClient } from '$lib/appwrite/appwrite-browser';
    import { Permission, Role } from 'appwrite';

    export let open = false;
    export let onOpenChange: (open: boolean) => void;
    export let channelId: string;
    export let workspaceId: string;

    let loading = false;
    let selectedFile: File | null = null;
    let comment = '';
    let uploadStatus = '';

    function handleFileSelect(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files[0]) {
            selectedFile = input.files[0];
        }
    }

    async function handleUpload(event: SubmitEvent) {
        event.preventDefault();
        if (!selectedFile) {
            toast.error('Please select a file to upload');
            return;
        }

        loading = true;
        uploadStatus = 'Uploading...';

        try {
            const { storage, account, databases } = createBrowserClient();
            const fileId = crypto.randomUUID();
            
            // Get current user's account
            const currentAccount = await account.get();

            // Upload file to workspace bucket with label-based permissions
            const file = await storage.createFile(
                workspaceId, // Using workspaceId as bucketId
                fileId,
                selectedFile,
                [
                    // Only users with workspace label can read
                    // Permission.read(Role.label(workspaceId)),
                    // Only file creator can update/delete 
                    // Permission.write(Role.user(currentAccount.$id)),
                    // Permission.delete(Role.user(currentAccount.$id))
                    Permission.read(Role.any()),
                    Permission.write(Role.any()),
                    Permission.delete(Role.any())
                ]
            );
            const fileUrl = storage.getFileDownload(workspaceId, fileId);
            console.log('File URL:', fileUrl);
            console.log('filesize', selectedFile.size);

            // Create attachment document
            const attachment = await databases.createDocument(
                'main',
                'attachments',
                fileId,
                {
                    message_id: '', // Will be linked when message is created
                    type: selectedFile.type,
                    url: fileUrl, // Store the storage file ID as the URL
                    name: selectedFile.name,
                    size: selectedFile.size
                },
                [
                    // Only users with workspace label can read
                    Permission.read(Role.label(workspaceId)),
                    // Only file creator can update/delete
                    Permission.write(Role.user(currentAccount.$id)),
                    Permission.delete(Role.user(currentAccount.$id))
                ]
            );
            const message = await databases.createDocument(
                'main',
                'messages',
                fileId,
                {
                    edited_at: new Date().toISOString(),
                    sender_name: currentAccount.name,
                    sender_id: currentAccount.$id,
                    sender_type: 'file',
                    workspace_id: workspaceId,
                    channel_id: channelId,
                    content: comment,
                    attachments: [fileId]
                },
                [
                    // Only users with workspace label can read
                    Permission.read(Role.label(workspaceId)),
                    // Only file creator can update/delete
                    Permission.write(Role.user(currentAccount.$id)),
                    Permission.delete(Role.user(currentAccount.$id))
                ]
            );

            console.log('created file', file);
            console.log('created message', message);
            console.log('created attachment', attachment);

            uploadStatus = 'Upload successful!';
            toast.success('File uploaded successfully');
            onOpenChange(false);
            selectedFile = null;
            comment = '';
            uploadStatus = '';
            
        } catch (error) {
            console.error('Error uploading file:', error);
            uploadStatus = 'Upload failed: ' + (error as Error).message;
            toast.error('Failed to upload file');
        } finally {
            loading = false;
        }
    }
</script>

<AlertDialog.Root {open} onOpenChange={(isOpen) => {
    onOpenChange(isOpen);
    if (!isOpen) {
        uploadStatus = '';
    }
}}>
    <AlertDialog.Content>
        <AlertDialog.Header>
            <AlertDialog.Title>Upload File</AlertDialog.Title>
            <AlertDialog.Description>
                Share a file in this channel
            </AlertDialog.Description>
        </AlertDialog.Header>

        <form on:submit={handleUpload} class="space-y-6">
            <div class="space-y-2">
                <Label for="file">Select File</Label>
                <input
                    type="file"
                    id="file"
                    name="file"
                    on:change={handleFileSelect}
                    class="w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-blue-500 dark:border-gray-700 cursor-pointer"
                />
                {#if selectedFile}
                    <p class="text-sm text-muted-foreground">Selected: {selectedFile.name}</p>
                {/if}
                {#if uploadStatus}
                    <p class="text-sm" class:text-destructive={uploadStatus.includes('failed')} class:text-green-500={uploadStatus.includes('successful')}>
                        {uploadStatus}
                    </p>
                {/if}
            </div>

            <div class="space-y-2">
                <Label for="comment">Add a Comment</Label>
                <textarea
                    id="comment"
                    bind:value={comment}
                    rows="3"
                    class="w-full px-3 py-2 border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-blue-500 dark:border-gray-700"
                    placeholder="Add a comment about this file..."
                ></textarea>
            </div>

            <AlertDialog.Footer>
                <AlertDialog.Cancel asChild>
                    <Button type="button" variant="outline" on:click={() => onOpenChange(false)}>Cancel</Button>
                </AlertDialog.Cancel>
                <Button type="submit" disabled={loading || !selectedFile}>
                    {loading ? 'Uploading...' : 'Upload File'}
                </Button>
            </AlertDialog.Footer>
        </form>
    </AlertDialog.Content>
</AlertDialog.Root>
