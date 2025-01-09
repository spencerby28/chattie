<script lang="ts">
	import { Tipex, Utility, defaultExtensions } from '@friendofsvelte/tipex';
	import type { Editor } from '@tiptap/core';
	import { cn } from '$lib/utils';
	import { Extension } from '@tiptap/core';
	import type { KeyboardShortcutCommand } from '@tiptap/core';
	import { Button } from "$lib/components/ui/button";

	import '@friendofsvelte/tipex/styles/Tipex.css';
	import '@friendofsvelte/tipex/styles/ProseMirror.css';

	import '@friendofsvelte/tipex/styles/CodeBlock.css';
	import Control from '$lib/components/features/messages/Control.svelte';
    import RichMessageComposer from '$lib/components/features/messages/RichMessageComposer.svelte';

</script>

<div class="fixed bottom-0 left-0 right-0">
  <RichMessageComposer />
</div>