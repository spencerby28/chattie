<script lang="ts">
    import markdownit from 'markdown-it'
    import type { PageData } from './$types';

    export let data: PageData;

    const md = markdownit({
        html: true,
        linkify: true,
        typographer: false,
        breaks: true
    }).enable(['list'])

    function processContent(content: string) {
        // Ensure proper list formatting by adding newlines before lists if needed
        return content.replace(/^(\d+\.)/gm, '\n$1')
                     .replace(/\*\*/g, '_'); // Convert ** to _ for emphasis
    }

    const renderContent = (content: string) => {
        return md.render(processContent(content));
    }
</script>

<style>
    /* Add proper list styling */
    :global(.rendered-content ol) {
        list-style-type: decimal !important;
        padding-left: 2rem !important;
        margin: 0.5rem 0 !important;
    }
    :global(.rendered-content li) {
        margin: 0.25rem 0 !important;
    }
    :global(.rendered-content p) {
        margin: 0.5rem 0 !important;
    }
</style>

<div class="container mx-auto p-4 space-y-6">
    <div class="grid grid-cols-2 gap-4">
        <div class="border rounded-lg p-4">
            <p class="text-sm text-muted-foreground">
                {new Date(data.message.$createdAt).toLocaleString()}
            </p>
            <div class="mt-2 max-w-none rendered-content">
                {@html renderContent(data.message.content)}
            </div>
        </div>

        <div class="border rounded-lg p-4">
            <p class="text-sm text-muted-foreground">
                Raw Message Content:
            </p>
            <div class="mt-2 whitespace-pre-wrap font-mono text-sm">
                {data.message.content}
            </div>
        </div>
    </div>
</div>
