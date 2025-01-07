<script lang="ts">
	import { enhance } from '$app/forms';
</script>

<div class="container mx-auto max-w-[60%] p-4">
	<h1 class="text-2xl font-bold mb-6">Create New Workspace</h1>

	<form method="POST" use:enhance class="space-y-4">
		<div>
			<label for="name" class="block text-sm font-medium mb-1">Workspace Name</label>
			<input
				type="text"
				id="name"
				name="name"
				required
				class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
				placeholder="Enter workspace name"
			/>
		</div>

		<div>
			<label for="description" class="block text-sm font-medium mb-1">Description</label>
			<textarea
				id="description"
				name="description"
				rows="3"
				class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
				placeholder="Enter workspace description"
			></textarea>
		</div>

		<div>
			<label class="block text-sm font-medium mb-1">Visibility</label>
			<div class="flex gap-4">
				<label class="flex items-center">
					<input
						type="radio"
						name="visibility"
						value="public"
						class="mr-2"
						checked
					/>
					Public
				</label>
				<label class="flex items-center">
					<input
						type="radio"
						name="visibility"
						value="private"
						class="mr-2"
					/>
					Private
				</label>
			</div>
		</div>

		<button
			type="submit"
			class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors"
		>
			Create Workspace
		</button>
	</form>
</div>
