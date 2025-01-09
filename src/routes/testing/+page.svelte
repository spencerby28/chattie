<script lang="ts">
	import { Tipex, Utility, defaultExtensions } from '@friendofsvelte/tipex';
	import type { Editor } from '@tiptap/core';
	import { cn } from '$lib/utils';
	import { Extension } from '@tiptap/core';
	import type { KeyboardShortcutCommand } from '@tiptap/core';
	import { Button } from '$lib/components/ui/button';

	import '@friendofsvelte/tipex/styles/Tipex.css';
	import '@friendofsvelte/tipex/styles/ProseMirror.css';

	import '@friendofsvelte/tipex/styles/CodeBlock.css';
	import Control from '$lib/components/features/messages/Control.svelte';
	import RichMessageComposer from '$lib/components/features/messages/RichMessageComposer.svelte';
</script>

<div class="bg-white h-full">
	<div class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[80vh] h-[80vh] bg-background rounded-3xl flex items-center justify-center pt-10">
		<div class="font-chattie text-[75vh] bg-gradient-to-r from-blue-400/60 to-purple-600/60 bg-clip-text text-transparent">
			C
		</div>
	</div>
</div>
