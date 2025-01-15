<script lang="ts">
	import { page } from '$app/stores';
	import { memberStore } from '$lib/stores/members';
	import type { Channel } from '$lib/types';

	const currentUser = $page.data.user;

	$: dmChannels =
		$page.data.channels?.filter(
			(c: Channel) => c.type === 'dm' && c.members.includes(currentUser.$id)
		) || [];

	$: otherUsers = dmChannels.map((channel: Channel) => {
		const otherId = channel.members.find((id) => id !== currentUser.$id);
		return $memberStore.find((m) => m.id === otherId);
	});
	$: console.log($memberStore.members);
</script>

<div class="space-y-2">
	<h3 class="px-3 font-semibold">Direct Messages</h3>
	{#each otherUsers as user}
		<a href="/dm/{user.id}" class="flex items-center gap-2 px-3 py-2 hover:bg-accent rounded-lg">
			<img src={user.avatar || '/images/avatar.png'} alt="" class="w-6 h-6 rounded-full" />
			<span>{user.name}</span>
		</a>
	{/each}
</div>
