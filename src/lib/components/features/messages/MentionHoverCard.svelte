<script lang="ts">
	import * as HoverCard from '$lib/components/ui/hover-card';
	import type { SimpleMember } from '$lib/types';

	let { member } = $props<{
		member: SimpleMember;
	}>();
</script>

<HoverCard.Root>
	<HoverCard.Trigger>
		<span class="mention">@{member.name}</span>
	</HoverCard.Trigger>
	<HoverCard.Content class="w-80">
		<div class="flex justify-between space-x-4">
			<div class="space-y-1">
				<h4 class="text-sm font-semibold">{member.name}</h4>
				<div class="flex items-center pt-2">
					<span class="text-xs text-muted-foreground">
						Click to send direct message
					</span>
				</div>
			</div>
		</div>
	</HoverCard.Content>
</HoverCard.Root>

<style>
	.mention {
		color: rgb(59 130 246);
		cursor: pointer;
		display: inline-block;
	}
</style> 