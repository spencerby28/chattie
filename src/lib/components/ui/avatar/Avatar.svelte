<script lang="ts">
    export let src: string | null = null;
    export let name: string;
    export let fallback: string | undefined = undefined;
    export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
    
    const sizeClasses = {
        sm: 'w-6 h-6 text-xs',
        md: 'w-8 h-8 text-sm',
        lg: 'w-12 h-12 text-base',
        xl: 'w-32 h-32 text-3xl'
    };
    
    const classes = sizeClasses[size];
</script>

{#if src}
    <img
        {src}
        alt={`${name}'s avatar`}
        class="{classes} rounded-xl object-cover"
    />
{:else}
    <div class="{classes} rounded-xl bg-accent text-accent-foreground flex items-center justify-center font-medium">
        {fallback || name[0].toUpperCase()}
    </div>
{/if}