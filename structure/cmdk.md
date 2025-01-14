================================================
File: /README.md
================================================
<p align="center">
<img src="./static/og.png" />
</p>

# ⌘K-sv [![cmdk package version](https://img.shields.io/npm/v/cmdk-sv.svg?colorB=green)](https://www.npmjs.com/package/cmdk-sv)

<!-- automd:badges license name="cmdk-sv" color="green" github="huntabyte/cmdk-sv" -->

[![npm version](https://flat.badgen.net/npm/v/cmdk-sv?color=green)](https://npmjs.com/package/cmdk-sv)
[![npm downloads](https://flat.badgen.net/npm/dm/cmdk-sv?color=green)](https://npmjs.com/package/cmdk-sv)
[![license](https://flat.badgen.net/github/license/huntabyte/cmdk-sv?color=green)](https://github.com/huntabyte/cmdk-sv/blob/main/LICENSE)

<!-- /automd -->

A port of [cmdk](https://cmdk.paco.me), to Svelte.

⌘K-sv is a command menu Svelte component that can also be used as an accessible combobox. You render items, it filters and sorts them automatically.

Demo and examples: [cmdk-sv.com](https://cmdk-sv.com)

## Install

```bash
npm install cmdk-sv
```

## Use

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';
</script>

<Command.Root label="Command Menu">
	<Command.Input />
	<Command.List>
		<Command.Empty>No results found.</Command.Empty>

		<Command.Group heading="Letters">
			<Command.Item>a</Command.Item>
			<Command.Item>b</Command.Item>
			<Command.Separator />
			<Command.Item>c</Command.Item>
		</Command.Group>

		<Command.Item>Apple</Command.Item>
	</Command.List>
</Command.Root>
```

Or in a dialog:

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';
</script>

<Command.Dialog label="Command Menu">
	<Command.Input />
	<Command.List>
		<Command.Empty>No results found.</Command.Empty>

		<Command.Group heading="Letters">
			<Command.Item>a</Command.Item>
			<Command.Item>b</Command.Item>
			<Command.Separator />
			<Command.Item>c</Command.Item>
		</Command.Group>

		<Command.Item>Apple</Command.Item>
	</Command.List>
</Command.Dialog>
```

## Styling

Each part has a specific data-attribute (starting with `data-cmdk-`) that can be used for styling.

### Command `[cmdk-root]`

Render this to show the command menu inline, or use [Dialog](#dialog-cmdk-dialog-cmdk-overlay) to render in a elevated context. Can be controlled by binding to the `value` prop.

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';

	let value = 'apple';
</script>

<Command.Root bind:value>
	<Command.Input />
	<Command.List>
		<Command.Item>Orange</Command.Item>
		<Command.Item>Apple</Command.Item>
	</Command.List>
</Command.Root>
```

By default, this uses a scoring algorithm to filter and rank items based on the user's search input.
The algorithm takes into account various factors like continuous matches, word and character jumps among other things.

You can provide a custom `filter` function that is called to rank each item. Both strings are normalized as lowercase and trimmed.

The following example implements a strict substring match:

```svelte
<Command.Root
	filter={(value, search) => {
		if (value.includes(search)) return 1;
		return 0;
	}}
/>
```

In this strict substring match example, the filter function returns a score of 1 if the item's value contains the search string as a substring, and 0 otherwise, removing it from the result list.

Or disable filtering and sorting entirely:

```svelte
<Command.Root shouldFilter={false}>
	<Command.List>
		{#each filteredItems as item}
			<Command.Item value={item}>
				{item}
			</Command.Item>
		{/each}
	</Command.List>
</Command.Root>
```

You can make the arrow keys wrap around the list (when you reach the end, it goes back to the first item) by setting the `loop` prop:

```svelte
<Command.Root loop />
```

This component also exposes two additional slot props for `state` (the current reactive value of the command state) and `stateStore` (the underlying writable state store). These can be used to implement more advanced use cases, such as debouncing the search updates with the `stateStore.updateState` method:

```svelte
<Command.Root {state} let:stateStore>
	{@const handleUpdateState = debounce(stateStore.updateState, 200)}
	<CustomCommandInput {handleUpdateState} />
</Command.Root>
```

### Dialog `[cmdk-dialog]` `[cmdk-overlay]`

Props are forwarded to [Command](#command-cmdk-root). Composes Bits UI's Dialog component. The overlay is always rendered. See the [Bits Documentation](https://bits-ui.com/docs/) for more information. Can be controlled by binding to the `open` prop.

```svelte
<script lang="ts">
	let open = false;
	let value: string;
</script>

<Command.Dialog bind:value bind:open>
	<!-- ... -->
</Command.Dialog>
```

You can provide a `portal` prop that accepts an HTML element that is forwarded to Bits UI's Dialog Portal component to specify which element the Dialog should portal into (defaults to `body`). To disable portalling, pass `null` as the `portal` prop.

```svelte
<Command.Dialog portal={null} />
```

### Input `[cmdk-input]`

All props are forwarded to the underlying `input` element. Can be controlled as a normal input by binding to its `value` prop.

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';

	let search = '';
</script>

<Command.Input bind:value={search} />
```

### List `[cmdk-list]`

Contains items and groups. Animate height using the `--cmdk-list-height` CSS variable.

```css
[data-cmdk-list] {
	min-height: 300px;
	height: var(--cmdk-list-height);
	max-height: 500px;
	transition: height 100ms ease;
}
```

To scroll item into view earlier near the edges of the viewport, use scroll-padding:

```css
[data-cmdk-list] {
	scroll-padding-block-start: 8px;
	scroll-padding-block-end: 8px;
}
```

### Item `[cmdk-item]` `[data-disabled?]` `[data-selected?]`

Item that becomes active on pointer enter. You should provide a unique `value` for each item, but it will be automatically inferred from the `.textContent` if you don't. Text content is normalized as lowercase and trimmed.

```svelte
<Command.Item
	onSelect={(value) => {
		console.log('Selected', value);
		// Value is implicity "apple" because of the provided text content
	}}
>
	Apple
</Command.Item>
```

You can force an item to always render, regardless of filtering, by passing the `alwaysRender` prop.

### Group `[cmdk-group]` `[hidden?]`

Groups items together with the given `heading` (`[cmdk-group-heading]`).

```svelte
<Command.Group heading="Fruit">
	<Command.Item>Apple</Command.Item>
</Command.Group>
```

Groups will not be removed from the DOM, rather the `hidden` attribute is applied to hide it from view. This may be relevant in your styling.

You can force a group to always be visible, regardless of filtering, by passing the `alwaysRender` prop.

### Separator `[cmdk-separator]`

Visible when the search query is empty or `alwaysRender` is true, hidden otherwise.

### Empty `[cmdk-empty]`

Automatically renders when there are no results for the search query.

### Loading `[cmdk-loading]`

You should conditionally render this with `progress` while loading asynchronous items.

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';

	let loading = false;
</script>

<Command.List>
	{#if loading}
		<Command.Loading progress={0.5}>Loading…</Command.Loading>
	{/if}
</Command.List>;
```

### `createState(initialState?: State)`

Create a state store which can be passed and used by the component. This is provided for more advanced use cases and should not be commonly used.

A good use case would be to render a more detailed empty state, like so:

```svelte
<script lang="ts">
	import { Command, createState } from 'cmdk-sv';

	const state = createState();
</script>

<Command.Root {state}>
	<Command.Empty>
		{#if $state.search}
			No results found for "{state.search}".
		{:else}
			No results found.
		{/if}
	</Command.Empty>
</Command.Root>
```

## Examples

Code snippets for common use cases.

### Nested items

Often selecting one item should navigate deeper, with a more refined set of items. For example selecting "Change theme…" should show new items "Dark theme" and "Light theme". We call these sets of items "pages", and they can be implemented with simple state:

```svelte
<script lang="ts">
	let open = false;
	let search = '';
	let pages: string[] = [];
	let page: string | undefined = undefined;

	$: page = pages[pages.length - 1];

	function changePage(newPage: string) {
		pages = [...pages, newPage];
	}
</script>

<Command
	onKeyDown={(e) => {
		// Escape goes to previous page
		// Backspace goes to previous page when search is empty
		if (e.key === 'Escape' || (e.key === 'Backspace' && !search)) {
			e.preventDefault();
			const newPages = pages.slice(0, -1);
			pages = newPages;
		}
	}}
>
	<Command.Input bind:value={search} />
	<Command.List>
		{#if !page}
			<Command.Item onSelect={() => changePage('projects')}>Search projects…</Command.Item>
			<Command.Item onSelect={() => changePage('teams')}>Join a team…</Command.Item>
		{:else if page === 'projects'}
			<Command.Item>Project A</Command.Item>
			<Command.Item>Project B</Command.Item>
		{:else if page === 'teams'}
			<Command.Item>Team 1</Command.Item>
			<Command.Item>Team 2</Command.Item>
		{/if}
	</Command.List>
</Command>
```

### Show sub-items when searching

If your items have nested sub-items that you only want to reveal when searching, render based on the search state:

```svelte
<!-- SubItem.svelte -->
<script lang="ts">
	import { Command } from 'cmdk-sv';

	type $$Props = Command.ItemProps & {
		search?: string;
	};
</script>

{#if search}
	<Command.Item {...$$restProps}>
		<slot />
	</Command.Item>
{/if}
```

Using the state store:

```svelte
<!-- CommandMenu.svelte -->
<script lang="ts">
	import { Command, createState } from 'cmdk-sv';
	import SubItem from './SubItem.svelte';
	const state = createState();
</script>

<Command.Root {state}>
	<Command.Input />
	<Command.List>
		<Command.Item>Change theme…</Command.Item>
		<SubItem search={$state.search}>Change theme to dark</SubItem>
		<SubItem search={$state.search}>Change theme to light</SubItem>
	</Command.List>
</Command.Root>
```

or

Using the input value:

```svelte
<!-- CommandMenu.svelte -->
<script lang="ts">
	import { Command } from 'cmdk-sv';
	import SubItem from './SubItem.svelte';
	let search: string;
</script>

<Command.Root>
	<Command.Input bind:value={search} />
	<Command.List>
		<Command.Item>Change theme…</Command.Item>
		<SubItem {search}>Change theme to dark</SubItem>
		<SubItem {search}>Change theme to light</SubItem>
	</Command.List>
</Command.Root>
```

### Asynchronous results

Render the items as they become available. Filtering and sorting will happen automatically.

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';

	let loading = false;
	let items: string[] = [];

	onMount(async () => {
		loading = true;
		const res = await api.get('/dictionary');
		items = res;
		loading = false;
	});
</script>

<Command.Root>
	<Command.Input />
	<Command.List>
		{#if loading}
			<Command.Loading>Fetching words…</Command.Loading>
		{:else}
			{#each items as item}
				<Command.Item value={item}>
					{item}
				</Command.Item>
			{/each}
		{/if}
	</Command.List>
</Command.Root>
```

### Use inside Popover

We recommend using the [Bits UI popover](https://www.bits-ui.com/docs/components/popover) component. ⌘K-sv relies on the Bits UI Dialog component, so this will reduce the number of dependencies you'll need.

```bash
npm install bits-ui
```

Render `Command` inside of the popover content:

```svelte
<script lang="ts">
	import { Command } from 'cmdk-sv';
	import { Popover } from 'bits-ui';
</script>

<Popover.Root>
	<Popover.Trigger>Toggle popover</Popover.Trigger>

	<Popover.Content>
		<Command.Root>
			<Command.Input />
			<Command.List>
				<Command.Item>Apple</Command.Item>
			</Command.List>
		</Command.Root>
	</Popover.Content>
</Popover.Root>
```

### Drop in stylesheets

You can find global stylesheets to drop in as a starting point for styling. See [src/styles/cmdk](src/styles/cmdk) for examples.

### Render Delegation

Each of the components (except the dialog) accept an `asChild` prop that can be used to render a custom element in place of the default. When using this prop, you'll need to check the components slot props to see what attributes & actions you'll need to pass to your custom element.

Components that contain only a single element will just have `attrs` & `action` slot props, or just `attrs`. Components that contain multiple elements will have an `attrs` and possibly an `actions` object whose properties are the attributes and actions for each element.

## FAQ

**Accessible?** Yes. Labeling, aria attributes, and DOM ordering tested with Voice Over and Chrome DevTools. [Dialog](#dialog-cmdk-dialog-cmdk-overlay) composes an accessible Dialog implementation.

**Filter/sort items manually?** Yes. Pass `shouldFilter={false}` to [Command](#command-cmdk-root). Better memory usage and performance. Bring your own virtualization this way.

**Unstyled?** Yes, use the listed CSS selectors.

**Weird/wrong behavior?** Make sure your `Command.Item` has a unique `value`.

**Listen for ⌘K automatically?** No, do it yourself to have full control over keybind context.

## History

Written in 2019 by Paco ([@pacocoursey](https://twitter.com/pacocoursey)) to see if a composable combobox API was possible. Used for the Vercel command menu and autocomplete by Rauno ([@raunofreiberg](https://twitter.com/raunofreiberg)) in 2020. Re-written independently in 2022 with a simpler and more performant approach. Ideas and help from Shu ([@shuding\_](https://twitter.com/shuding_)).

Ported to Svelte in 2023 by Huntabyte ([@huntabyte](https://twitter.com/huntabyte))

## Sponsors

This project is supported by the following beautiful people/organizations:

<p align="center">
  <a href="https://github.com/sponsors/huntabyte">
    <img src='https://github.com/huntabyte/static/blob/main/sponsors.svg?raw=true' alt="Logos from Sponsors" />
  </a>
</p>

## License

<!-- automd:contributors license=MIT author="huntabyte" github="huntabyte/cmdk-sv" -->

Published under the [MIT](https://github.com/huntabyte/cmdk-sv/blob/main/LICENSE) license.
Made by [@huntabyte](https://github.com/huntabyte) and [community](https://github.com/huntabyte/cmdk-sv/graphs/contributors) 💛
<br><br>
<a href="https://github.com/huntabyte/cmdk-sv/graphs/contributors">
<img src="https://contrib.rocks/image?repo=huntabyte/cmdk-sv" />
</a>

<!-- /automd -->


================================================
File: /CHANGELOG.md
================================================
# cmdk-sv

## 0.0.18

### Patch Changes

- chore: Add Svelte 5 as a peer dependency ([#88](https://github.com/huntabyte/cmdk-sv/pull/88))

- fix: select first value after search ([#83](https://github.com/huntabyte/cmdk-sv/pull/83))

- fix: Removes self-closing non-void elements to fix Svelte 5 warnings ([#84](https://github.com/huntabyte/cmdk-sv/pull/84))

- fix: Support meta key and home/end shortcuts ([#78](https://github.com/huntabyte/cmdk-sv/pull/78))

## 0.0.17

### Patch Changes

- fix: remove leftover logs ([#70](https://github.com/huntabyte/cmdk-sv/pull/70))

## 0.0.16

### Patch Changes

- Fixed bug where page would crash when a large list was rendered ([#55](https://github.com/huntabyte/cmdk-sv/pull/55))

## 0.0.15

### Patch Changes

- chore: Updated `svelte-package` to fix malformed package build ([#64](https://github.com/huntabyte/cmdk-sv/pull/64))

## 0.0.14

### Patch Changes

- Expose keydown event from Input component ([#57](https://github.com/huntabyte/cmdk-sv/pull/57))

- change `moduleResolution` to `NodeNext` ([#62](https://github.com/huntabyte/cmdk-sv/pull/62))

## 0.0.13

### Patch Changes

- Fix type resolution and intellisense for most components ([#46](https://github.com/huntabyte/cmdk-sv/pull/46))

## 0.0.12

### Patch Changes

- feat: expose state slot prop for Command.Root ([#38](https://github.com/huntabyte/cmdk-sv/pull/38))

## 0.0.11

### Patch Changes

- fix: maintain original list order when clearing search value ([#35](https://github.com/huntabyte/cmdk-sv/pull/35))

## 0.0.10

### Patch Changes

- fix: move Command additional props to types file ([#31](https://github.com/huntabyte/cmdk-sv/pull/31))

## 0.0.9

### Patch Changes

- feat: export `defaultFilter` function ([#29](https://github.com/huntabyte/cmdk-sv/pull/29))

## 0.0.8

### Patch Changes

- fix: `autofocus` input behavior ([#25](https://github.com/huntabyte/cmdk-sv/pull/25))

## 0.0.7

### Patch Changes

- Fix: Bug with conditional rendering ([#22](https://github.com/huntabyte/cmdk-sv/pull/22))

## 0.0.6

### Patch Changes

- Fix: bug where best match wasnt selected ([#17](https://github.com/huntabyte/cmdk-sv/pull/17))

## 0.0.5

### Patch Changes

- Add `asChild` prop & forward input events ([#14](https://github.com/huntabyte/cmdk-sv/pull/14))

## 0.0.4

### Patch Changes

- Fix: input autofocus ([#11](https://github.com/huntabyte/cmdk-sv/pull/11))

## 0.0.3

### Patch Changes

- Fix: `autofocus` prop autofocuses input on mount ([#8](https://github.com/huntabyte/cmdk-sv/pull/8))

## 0.0.2

### Patch Changes

- Fix exports ([#5](https://github.com/huntabyte/cmdk-sv/pull/5))

## 0.0.1

### Patch Changes

- initial release ([#1](https://github.com/huntabyte/cmdk-sv/pull/1))


================================================
File: /LICENSE
================================================
MIT License

Copyright (c) 2024 Hunter Johnston <https://github.com/huntabyte>
Copyright (c) 2022 Paco Coursey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


================================================
File: /package.json
================================================
{
	"name": "cmdk-sv",
	"version": "0.0.18",
	"scripts": {
		"dev": "vite dev",
		"build": "vite build && npm run package",
		"preview": "vite preview",
		"package": "svelte-kit sync && svelte-package && publint",
		"prepublishOnly": "npm run package",
		"check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
		"check:watch": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json --watch",
		"lint": "prettier --check . && eslint .",
		"format": "prettier --write .",
		"test": "vitest",
		"release": "changeset publish",
		"changeset": "changeset"
	},
	"exports": {
		".": {
			"types": "./dist/index.d.ts",
			"svelte": "./dist/index.js"
		}
	},
	"files": [
		"dist",
		"!dist/**/*.test.*",
		"!dist/**/*.spec.*"
	],
	"peerDependencies": {
		"svelte": "^4.0.0 || ^5.0.0-next.1"
	},
	"devDependencies": {
		"@changesets/cli": "^2.27.7",
		"@playwright/test": "^1.45.1",
		"@sveltejs/adapter-vercel": "^4.0.0",
		"@sveltejs/kit": "^2.5.18",
		"@sveltejs/package": "^2.3.2",
		"@sveltejs/vite-plugin-svelte": "^3.1.1",
		"@svitejs/changesets-changelog-github-compact": "^1.1.0",
		"@types/prismjs": "^1.26.4",
		"@typescript-eslint/eslint-plugin": "^7.16.1",
		"@typescript-eslint/parser": "^7.16.1",
		"autoprefixer": "^10.4.19",
		"eslint": "^8.57.0",
		"eslint-config-prettier": "^8.10.0",
		"eslint-plugin-svelte": "^2.42.0",
		"mode-watcher": "^0.4.0",
		"postcss": "^8.4.39",
		"postcss-load-config": "^6.0.1",
		"postcss-preset-env": "^9.6.0",
		"prettier": "^3.3.3",
		"prettier-plugin-svelte": "^3.2.5",
		"prism-svelte": "^0.5.0",
		"prismjs": "^1.29.0",
		"publint": "^0.1.9",
		"svelte": "^4.2.18",
		"svelte-check": "^3.8.4",
		"tslib": "^2.6.2",
		"typescript": "^5.2.2",
		"vite": "^5.3.3",
		"vitest": "^1.6.0"
	},
	"svelte": "./dist/index.js",
	"types": "./dist/index.d.ts",
	"type": "module",
	"dependencies": {
		"bits-ui": "^0.21.12",
		"nanoid": "^5.0.7"
	},
	"packageManager": "pnpm@9.5.0"
}


================================================
File: /playwright.config.ts
================================================
import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	webServer: {
		command: 'npm run build && npm run preview',
		port: 4173
	},
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/
};

export default config;


================================================
File: /postcss.config.cjs
================================================
module.exports = {
	plugins: { autoprefixer: {} }
};


================================================
File: /svelte.config.js
================================================
import adapter from '@sveltejs/adapter-vercel';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
	// for more information about preprocessors
	preprocess: [vitePreprocess()],

	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
		// If your environment is not supported or you settled on a specific environment, switch out the adapter.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		adapter: adapter(),
		alias: {
			$docs: './src/docs',
			$styles: './src/styles'
		}
	}
};

export default config;


================================================
File: /tsconfig.json
================================================
{
	"extends": "./.svelte-kit/tsconfig.json",
	"compilerOptions": {
		"allowJs": true,
		"checkJs": true,
		"esModuleInterop": true,
		"forceConsistentCasingInFileNames": true,
		"resolveJsonModule": true,
		"skipLibCheck": true,
		"sourceMap": true,
		"strict": true,
		"moduleResolution": "NodeNext",
		"module": "NodeNext"
	}
}


================================================
File: /vite.config.ts
================================================
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	},
	server: {
		fs: {
			allow: ['package.json']
		}
	}
});


================================================
File: /.eslintignore
================================================
.DS_Store
node_modules
/build
/.svelte-kit
/package
.env
.env.*
!.env.example

# Ignore files for PNPM, NPM and YARN
pnpm-lock.yaml
package-lock.json
yarn.lock
/dist
.changeset/

================================================
File: /.eslintrc.cjs
================================================
/** @type { import("eslint").Linter.Config } */
module.exports = {
	root: true,
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/recommended',
		'plugin:svelte/recommended',
		'prettier'
	],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 'latest',
		extraFileExtensions: ['.svelte']
	},
	env: {
		browser: true,
		es2024: true,
		node: true
	},
	globals: { $$Generic: 'readable', NodeJS: true },
	rules: {
		'no-console': 'warn',
		'@typescript-eslint/no-unused-vars': [
			'warn',
			{
				argsIgnorePattern: '^_',
				varsIgnorePattern: '^_'
			}
		],
		'svelte/no-target-blank': 'error',
		'svelte/no-immutable-reactive-statements': 'error',
		'svelte/no-reactive-literals': 'error',
		'svelte/no-useless-mustaches': 'error',
		'svelte/button-has-type': 'off',
		'svelte/require-each-key': 'off',
		'svelte/no-at-html-tags': 'off',
		'svelte/no-unused-svelte-ignore': 'off',
		'svelte/require-stores-init': 'off'
	},
	overrides: [
		{
			files: ['*.svelte'],
			parser: 'svelte-eslint-parser',
			parserOptions: {
				parser: '@typescript-eslint/parser'
			},
			rules: {
				'@typescript-eslint/no-unused-vars': [
					'warn',
					{
						argsIgnorePattern: '^_',
						varsIgnorePattern: '^\\$\\$(Props|Events|Slots|Generic)$'
					}
				]
			}
		},
		{
			files: ['*.ts'],
			parser: '@typescript-eslint/parser',
			rules: {
				'@typescript-eslint/ban-types': [
					'error',
					{
						extendDefaults: true,
						types: {
							'{}': false
						}
					}
				]
			}
		},
		{
			files: ['*.js', '*.svelte', '*.ts'],
			rules: {
				'no-console': 'error'
			}
		}
	]
};


================================================
File: /.npmrc
================================================
engine-strict=true
resolution-mode=highest
package-manager-strict=false

================================================
File: /.prettierignore
================================================
.DS_Store
node_modules
/build
/.svelte-kit
/package
.env
.env.*
!.env.example

# Ignore files for PNPM, NPM and YARN
pnpm-lock.yaml
package-lock.json
yarn.lock
/dist
.vercel
.changeset

================================================
File: /.prettierrc
================================================
{
	"useTabs": true,
	"singleQuote": true,
	"trailingComma": "none",
	"printWidth": 100,
	"plugins": ["prettier-plugin-svelte"],
	"overrides": [{ "files": "*.svelte", "options": { "parser": "svelte" } }]
}


================================================
File: /src/app.d.ts
================================================
// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		interface PageData {
			version: string;
		}
		// interface Platform {}
	}
}

export {};


================================================
File: /src/app.html
================================================
<!doctype html>
<html lang="en" style="color-scheme: dark">
	<head>
		<meta charset="utf-8" />
		<link rel="icon" href="%sveltekit.assets%/favicon.svg" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		%sveltekit.head%
	</head>
	<body data-sveltekit-preload-data="hover">
		<div>%sveltekit.body%</div>
	</body>
</html>


================================================
File: /src/index.test.ts
================================================
import { describe, it, expect } from 'vitest';

describe('sum test', () => {
	it('adds 1 + 2 to equal 3', () => {
		expect(1 + 2).toBe(3);
	});
});


================================================
File: /src/docs/code.ts
================================================
export const code = `<script>
  import { Command } from 'cmdk-sv';
  let loading = false
</script>
  
<Command.Root>
  <Command.Input />
  <Command.List>
    {#if loading}
      <Command.Loading>Loading...</Command.Loading>
    {/if}
  
    <Command.Empty>No results found.</Command.Empty>
  
    <Command.Group heading="Fruits">
      <Command.Item>Apple</Command.Item>
      <Command.Item>Orange</Command.Item>
      <Command.Separator />
      <Command.Item>Pear</Command.Item>
      <Command.Item>Blueberry</Command.Item>
    </Command.Group>
    
    <Command.Item>Fish</Command.Item>
  </Command.List>
</Command.Root>`;

// a function that removes indentation from all lines in a string
export function unindent(s: string) {
	const lines = s.split('\n');
	const indent = lines[0].match(/^\s*/)?.[0];
	if (!indent) return s;
	return lines.map((line) => line.replace(indent, '')).join('\n');
}

// remove spaces from the beginning and end of a string
export function trim(s: string) {
	return s.replace(/^\s+|\s+$/g, '');
}


================================================
File: /src/docs/copy-code.ts
================================================
import { writable } from 'svelte/store';
import { isBrowser } from '$lib/internal/index.js';

export function createCopyCodeButton() {
	let codeString = '';
	const copied = writable(false);
	let copyTimeout = 0;

	function copyCode() {
		if (!isBrowser) return;
		navigator.clipboard.writeText(codeString);
		copied.set(true);
		clearTimeout(copyTimeout);
		copyTimeout = window.setTimeout(() => {
			copied.set(false);
		}, 2500);
	}

	function setCodeString(node: HTMLElement) {
		codeString = node.innerText.trim() ?? '';
	}

	return {
		copied: copied,
		copyCode: copyCode,
		setCodeString: setCodeString
	};
}


================================================
File: /src/docs/highlight.ts
================================================
import type { EnvConfig, Token } from './types.js';
import type { Grammar, Token as PrismToken, TokenStream } from 'prismjs';
import Prism from 'prismjs';

const newlineRe = /\r\n|\r|\n/;

// Empty lines need to contain a single empty token, denoted with { empty: true }
function normalizeEmptyLines(line: Token[]) {
	if (line.length === 0) {
		line.push({
			types: ['plain'],
			content: '\n',
			empty: true
		});
	} else if (line.length === 1 && line[0].content === '') {
		line[0].content = '\n';
		line[0].empty = true;
	}
}

function appendTypes(types: string[], add: string[] | string): string[] {
	const typesSize = types.length;

	if (typesSize > 0 && types[typesSize - 1] === add) {
		return types;
	}

	return types.concat(add);
}

// Takes an array of Prism's tokens and groups them by line, turning plain
// strings into tokens as well. Tokens can become recursive in some cases,
// which means that their types are concatenated. Plain-string tokens however
// are always of type "plain".
// This is not recursive to avoid exceeding the call-stack limit, since it's unclear
// how nested Prism's tokens can become
export function normalizeTokens(tokens: (PrismToken | string)[]): Token[][] {
	const typeArrStack: string[][] = [[]];
	const tokenArrStack = [tokens];
	const tokenArrIndexStack = [0];
	const tokenArrSizeStack = [tokens.length];
	let i = 0;
	let stackIndex = 0;
	let currentLine: Token[] = [];
	const acc = [currentLine];

	while (stackIndex > -1) {
		while ((i = tokenArrIndexStack[stackIndex]++) < tokenArrSizeStack[stackIndex]) {
			let content: TokenStream;
			let types = typeArrStack[stackIndex];
			const tokenArr = tokenArrStack[stackIndex];
			const token = tokenArr[i];

			// Determine content and append type to types if necessary
			if (typeof token === 'string') {
				types = stackIndex > 0 ? types : ['plain'];
				content = token;
			} else {
				types = appendTypes(types, token.type);

				if (token.alias) {
					types = appendTypes(types, token.alias);
				}

				content = token.content;
			}

			// If token.content is an array, increase the stack depth and repeat this while-loop
			if (typeof content !== 'string') {
				stackIndex++;
				typeArrStack.push(types);
				tokenArrStack.push(content as PrismToken[]);
				tokenArrIndexStack.push(0);
				tokenArrSizeStack.push(content.length);
				continue;
			}

			// Split by newlines
			const splitByNewlines = content.split(newlineRe);
			const newlineCount = splitByNewlines.length;
			currentLine.push({
				types,
				content: splitByNewlines[0]
			});

			// Create a new line for each string on a new line
			for (let i = 1; i < newlineCount; i++) {
				normalizeEmptyLines(currentLine);
				acc.push((currentLine = []));
				currentLine.push({
					types,
					content: splitByNewlines[i]
				});
			}
		}

		// Decreate the stack depth
		stackIndex--;
		typeArrStack.pop();
		tokenArrStack.pop();
		tokenArrIndexStack.pop();
		tokenArrSizeStack.pop();
	}

	normalizeEmptyLines(currentLine);
	return acc;
}

export function tokenize(code: string, grammar: Grammar, language: string) {
	if (!grammar) {
		return normalizeTokens([code]);
	}

	const prismConfig: EnvConfig = {
		code,
		grammar,
		language,
		tokens: []
	};

	Prism.hooks.run('before-tokenize', prismConfig);
	prismConfig.tokens = Prism.tokenize(code, grammar);
	Prism.hooks.run('after-tokenize', prismConfig);
	return normalizeTokens(prismConfig.tokens);
}

const entities = [
	[/</g, '&lt;'],
	[/>/g, '&gt;'],
	[/{/g, '&#123;'],
	[/}/g, '&#125;']
];

export function escape(s: string) {
	let newStr = s;
	for (let i = 0; i < entities.length; i += 1) {
		newStr = newStr.replace(entities[i][0], entities[i][1] as string);
	}
	return newStr;
}


================================================
File: /src/docs/types.ts
================================================
import type { Token as PrismToken, Grammar } from 'prismjs';

export type Language = string;
export type PrismGrammar = Grammar;

export type Themes = 'linear' | 'raycast' | 'vercel' | 'framer';

export type Token = {
	types: string[];
	content: string;
	empty?: boolean;
};

export type EnvConfig = {
	code: string;
	grammar: PrismGrammar;
	language: Language;
	tokens: (string | PrismToken)[];
};


================================================
File: /src/docs/utils.ts
================================================
import { cubicOut } from 'svelte/easing';
import type { TransitionConfig } from 'svelte/transition';

export type FlyAndScaleParams = {
	y?: number;
	start?: number;
	duration?: number;
	delay?: number;
};

export const flyAndScale = (
	node: Element,
	params: FlyAndScaleParams = { y: -8, start: 0.95, duration: 200, delay: 0 }
): TransitionConfig => {
	const style = getComputedStyle(node);
	const transform = style.transform === 'none' ? '' : style.transform;

	const scaleConversion = (valueA: number, scaleA: [number, number], scaleB: [number, number]) => {
		const [minA, maxA] = scaleA;
		const [minB, maxB] = scaleB;

		const percentage = (valueA - minA) / (maxA - minA);
		const valueB = percentage * (maxB - minB) + minB;

		return valueB;
	};

	const styleToString = (style: Record<string, number | string | undefined>): string => {
		return Object.keys(style).reduce((str, key) => {
			if (style[key] === undefined) return str;
			return str + `${key}:${style[key]};`;
		}, '');
	};

	return {
		duration: params.duration ?? 200,
		delay: params.delay ?? 0,
		css: (t) => {
			const y = scaleConversion(t, [0, 1], [params.y ?? -8, 0]);
			const scale = scaleConversion(t, [0, 1], [params.start ?? 0.95, 1]);

			return styleToString({
				transform: `${transform} translate3d(0, ${y}px, 0) scale(${scale})`,
				opacity: t
			});
		},
		easing: cubicOut
	};
};


================================================
File: /src/docs/components/cmdk-wrapper.svelte
================================================
<script lang="ts">
	import { flyAndScale, type FlyAndScaleParams } from '$docs/utils.js';

	const outConf: FlyAndScaleParams = {
		y: 0,
		duration: 200,
		start: 0.98
	};

	const inConf: FlyAndScaleParams = {
		y: 0,
		delay: 210,
		duration: 200,
		start: 0.98
	};
</script>

<div style:position="relative" style:width="100%">
	<div
		style:height="475px"
		style:width="100%"
		style:position="absolute"
		style:top="0"
		style:left="0"
		out:flyAndScale={outConf}
		in:flyAndScale={inConf}
	>
		<slot />
	</div>
</div>


================================================
File: /src/docs/components/code-block.svelte
================================================
<script lang="ts">
	import Prism from 'prismjs';
	import 'prism-svelte';
	import { code } from '$docs/code.js';
	import { escape, tokenize } from '$docs/highlight.js';
	import { createCopyCodeButton } from '$docs/copy-code.js';
	import { CopyIcon } from './icons/index.js';
	import '$styles/code.postcss';

	const tokens = tokenize(code, Prism.languages.svelte, 'svelte');

	const { copyCode, setCodeString } = createCopyCodeButton();

	const rawCode: string[] = [];

	for (const lines of tokens) {
		const workingLines = [];
		workingLines.push('<div class="token-line">');
		for (const token of lines) {
			const { types, content, empty } = token;
			if (!empty) {
				let strTypes = types.join(' ');

				if (content === '#') {
					strTypes += ' keyword';
				}

				workingLines.push(`<span class="token ${strTypes}">${escape(content)}</span>`);
			}
		}
		workingLines.push('</div>');
		rawCode.push(workingLines.join(''));
	}

	const rawCodeString = rawCode.join('');
</script>

<div class="codeBlock">
	<div class="line2" aria-hidden></div>
	<div class="line3" aria-hidden></div>
	<pre
		use:setCodeString
		class="root prism-code language-svelte"
		style:color="var(--gray12)"
		style:font-size="12px">
		<button aria-label="Copy Code" on:click={copyCode}>
			<CopyIcon />
		</button>
		<div class="shine"></div>
			{@html rawCodeString}
	</pre>
</div>


================================================
File: /src/docs/components/footer.svelte
================================================
<footer class="footer">
	<div class="footerText">
		Crafted by
		<a href="https://paco.me" target="_blank" rel="noopener noreferrer">
			<img src="/paco.png" alt="Avatar of Paco" />
			Paco
		</a>
		and
		<a href="https://rauno.me" target="_blank" rel="noopener noreferrer">
			<img src="/rauno.jpeg" alt="Avatar of Rauno" />
			Rauno
		</a>
	</div>
	<div class="footerText">
		Ported to Svelte by
		<a href="https://twitter.com/huntabyte" target="_blank" rel="noopener noreferrer">
			<img src="/huntabyte.png" alt="Avatar of Huntabyte" />
			Huntabyte
		</a>
	</div>
</footer>


================================================
File: /src/docs/components/github-button.svelte
================================================
<script lang="ts">
	import { GitHubIcon } from './icons/index.js';
</script>

<a
	href="https://github.com/huntabyte/cmdk-svelte"
	target="_blank"
	rel="noopener noreferrer"
	class="githubButton"
>
	<GitHubIcon />
	huntabyte/cmdk-sv
</a>


================================================
File: /src/docs/components/index.ts
================================================
export { default as VersionBadge } from './version-badge.svelte';
export { default as GitHubButton } from './github-button.svelte';
export { default as InstallButton } from './install-button.svelte';
export { default as CMDKWrapper } from './cmdk-wrapper.svelte';
export { default as ThemeSwitcher } from './theme-switcher.svelte';
export { default as CodeBlock } from './code-block.svelte';
export { default as Footer } from './footer.svelte';


================================================
File: /src/docs/components/install-button.svelte
================================================
<script lang="ts">
	import { CopiedIcon, CopyIcon } from './icons/index.js';
	let copied = false;

	function handleCopy() {
		navigator.clipboard.writeText('npm install cmdk-sv');
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}
</script>

<button class="installButton" on:click={handleCopy}>
	npm install cmdk-sv
	<span>
		{#if copied}
			<CopiedIcon />
		{:else}
			<CopyIcon />
		{/if}
	</span>
</button>


================================================
File: /src/docs/components/logo.svelte
================================================
<script lang="ts">
	import { styleToString } from '$lib/internal/index.js';
	export let size: string = '20px';
	import '$styles/icons.postcss';
</script>

<div
	class="blurLogo"
	style={styleToString({
		width: size,
		height: size
	})}
>
	<div class="bg" aria-hidden>
		<slot />
	</div>
	<div class="inner"><slot /></div>
</div>


================================================
File: /src/docs/components/theme-switcher.svelte
================================================
<script lang="ts">
	import type { Themes } from '$docs/types.js';
	import { RaycastIcon, LinearIcon, VercelIcon, FramerIcon } from './icons/index.js';
	import { kbd } from '$lib/internal/index.js';
	import type { ComponentType } from 'svelte';
	import { crossfade } from 'svelte/transition';
	import { cubicInOut } from 'svelte/easing';

	export let theme: Themes = 'raycast';
	let showArrowKeyHint = false;

	function isTheme(value: unknown): value is Themes {
		return typeof value === 'string' && ['raycast', 'linear', 'vercel', 'framer'].includes(value);
	}

	type ThemeObj = {
		icon: ComponentType;
		key: Themes;
	};

	const themes: ThemeObj[] = [
		{
			icon: RaycastIcon,
			key: 'raycast'
		},
		{
			icon: LinearIcon,
			key: 'linear'
		},
		{
			icon: VercelIcon,
			key: 'vercel'
		},
		{
			icon: FramerIcon,
			key: 'framer'
		}
	];

	function switcherAction(_: HTMLElement) {
		function handleKeydown(e: KeyboardEvent) {
			const themeNames = themes.map(({ key }) => key);

			if (e.key === kbd.ARROW_RIGHT) {
				const currentIndex = themeNames.indexOf(theme);
				const nextIndex = currentIndex + 1;
				const nextTheme = themeNames[nextIndex];

				if (isTheme(nextTheme)) {
					theme = nextTheme;
				}
			}
			if (e.key === kbd.ARROW_LEFT) {
				const currentIndex = themeNames.indexOf(theme);
				const nextIndex = currentIndex - 1;
				const nextTheme = themeNames[nextIndex];

				if (isTheme(nextTheme)) {
					theme = nextTheme;
				}
			}
		}

		document.addEventListener('keydown', handleKeydown);

		return {
			destroy() {
				document.removeEventListener('keydown', handleKeydown);
			}
		};
	}

	function handleButtonClick(key: Themes) {
		theme = key;
		if (showArrowKeyHint === false) {
			showArrowKeyHint = true;
		}
	}

	const [send, receive] = crossfade({
		duration: 250,
		easing: cubicInOut
	});
</script>

<div class="switcher" use:switcherAction>
	<span class="arrow" style:left="100px" style:transform="translateX(-24px) translateZ(0px)">
		←
	</span>
	{#each themes as { key, icon }}
		{@const isActive = theme === key}
		<button data-selected={isActive} on:click={() => handleButtonClick(key)}>
			<svelte:component this={icon} />
			{key}
			{#if isActive}
				<div class="activeTheme" in:send={{ key: 'active' }} out:receive={{ key: 'active' }}></div>
			{/if}
		</button>
	{/each}
	<span class="arrow" style:right="100px" style:transform="translateX(20px) translateZ(0px)">→</span
	>
</div>


================================================
File: /src/docs/components/version-badge.svelte
================================================
<script lang="ts">
	import { page } from '$app/stores';
</script>

<span class="versionBadge">
	{$page.data.version}
</span>


================================================
File: /src/docs/components/cmdk/index.ts
================================================
export { default as RaycastCMDK } from './raycast/raycast-cmdk.svelte';
export { default as LinearCMDK } from './linear/linear-cmdk.svelte';
export { default as VercelCMDK } from './vercel/vercel-cmdk.svelte';
export { default as FramerCMDK } from './framer/framer-cmdk.svelte';


================================================
File: /src/docs/components/cmdk/framer/framer-cmdk.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';
	import type { ComponentType } from 'svelte';
	import {
		AvatarIcon,
		BadgeIcon,
		ButtonIcon,
		ContainerIcon,
		InputIcon,
		RadioIcon,
		SearchIcon,
		SliderIcon
	} from './icons/index.js';
	import '$styles/cmdk/framer.postcss';

	let value = 'Button';

	type Component = {
		value: string;
		subtitle: string;
		icon: ComponentType;
	};

	const components: Component[] = [
		{
			value: 'Button',
			subtitle: 'Trigger actions',
			icon: ButtonIcon
		},
		{
			value: 'Input',
			subtitle: 'Retrive user input',
			icon: InputIcon
		},
		{
			value: 'Radio',
			subtitle: 'Single choice input',
			icon: RadioIcon
		},
		{
			value: 'Badge',
			subtitle: 'Annotate context',
			icon: BadgeIcon
		},
		{
			value: 'Slider',
			subtitle: 'Free range picker',
			icon: SliderIcon
		},
		{
			value: 'Avatar',
			subtitle: 'Illustrate the user',
			icon: AvatarIcon
		},
		{
			value: 'Container',
			subtitle: 'Lay out items',
			icon: ContainerIcon
		}
	];
</script>

<div class="framer">
	<Command.Root bind:value>
		<div data-cmdk-framer-header="">
			<SearchIcon />
			<Command.Input autofocus placeholder="Find components, packages, and interactions..." />
		</div>
		<Command.List>
			<div data-cmdk-framer-items="">
				<div data-cmdk-framer-left="">
					<Command.Group heading="Components">
						{#each components as { value, subtitle, icon }}
							<Command.Item {value}>
								<div data-cmdk-framer-icon-wrapper="">
									<svelte:component this={icon} />
								</div>
								<div data-cmdk-framer-item-meta="">
									{value}
									<span data-cmdk-framer-item-subtitle="">{subtitle}</span>
								</div>
							</Command.Item>
						{/each}
					</Command.Group>
				</div>
				<hr data-cmdk-framer-separator="" />
				<div data-cmdk-framer-right="">
					{#if value === 'Button'}
						<button>Primary</button>
					{:else if value === 'Input'}
						<input type="text" placeholder="Placeholder" />
					{:else if value === 'Badge'}
						<div data-cmdk-framer-badge="">Badge</div>
					{:else if value === 'Radio'}
						<label data-cmdk-framer-radio="">
							<input type="radio" checked />
							Radio Button
						</label>
					{:else if value === 'Avatar'}
						<img src="/rauno.jpeg" alt="Avatar of Rauno" />
					{:else if value === 'Slider'}
						<div data-cmdk-framer-slider="">
							<div></div>
						</div>
					{:else if value === 'Container'}
						<div data-cmdk-framer-container=""></div>
					{/if}
				</div>
			</div>
		</Command.List>
	</Command.Root>
</div>


================================================
File: /src/docs/components/cmdk/framer/icons/avatar.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M0.877014 7.49988C0.877014 3.84219 3.84216 0.877045 7.49985 0.877045C11.1575 0.877045 14.1227 3.84219 14.1227 7.49988C14.1227 11.1575 11.1575 14.1227 7.49985 14.1227C3.84216 14.1227 0.877014 11.1575 0.877014 7.49988ZM7.49985 1.82704C4.36683 1.82704 1.82701 4.36686 1.82701 7.49988C1.82701 8.97196 2.38774 10.3131 3.30727 11.3213C4.19074 9.94119 5.73818 9.02499 7.50023 9.02499C9.26206 9.02499 10.8093 9.94097 11.6929 11.3208C12.6121 10.3127 13.1727 8.97172 13.1727 7.49988C13.1727 4.36686 10.6328 1.82704 7.49985 1.82704ZM10.9818 11.9787C10.2839 10.7795 8.9857 9.97499 7.50023 9.97499C6.01458 9.97499 4.71624 10.7797 4.01845 11.9791C4.97952 12.7272 6.18765 13.1727 7.49985 13.1727C8.81227 13.1727 10.0206 12.727 10.9818 11.9787ZM5.14999 6.50487C5.14999 5.207 6.20212 4.15487 7.49999 4.15487C8.79786 4.15487 9.84999 5.207 9.84999 6.50487C9.84999 7.80274 8.79786 8.85487 7.49999 8.85487C6.20212 8.85487 5.14999 7.80274 5.14999 6.50487ZM7.49999 5.10487C6.72679 5.10487 6.09999 5.73167 6.09999 6.50487C6.09999 7.27807 6.72679 7.90487 7.49999 7.90487C8.27319 7.90487 8.89999 7.27807 8.89999 6.50487C8.89999 5.73167 8.27319 5.10487 7.49999 5.10487Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/badge.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M3.5 6H11.5C12.3284 6 13 6.67157 13 7.5C13 8.32843 12.3284 9 11.5 9H3.5C2.67157 9 2 8.32843 2 7.5C2 6.67157 2.67157 6 3.5 6ZM1 7.5C1 6.11929 2.11929 5 3.5 5H11.5C12.8807 5 14 6.11929 14 7.5C14 8.88071 12.8807 10 11.5 10H3.5C2.11929 10 1 8.88071 1 7.5ZM4.5 7C4.22386 7 4 7.22386 4 7.5C4 7.77614 4.22386 8 4.5 8H10.5C10.7761 8 11 7.77614 11 7.5C11 7.22386 10.7761 7 10.5 7H4.5Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/button.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M2 5H13C13.5523 5 14 5.44772 14 6V9C14 9.55228 13.5523 10 13 10H2C1.44772 10 1 9.55228 1 9V6C1 5.44772 1.44772 5 2 5ZM0 6C0 4.89543 0.895431 4 2 4H13C14.1046 4 15 4.89543 15 6V9C15 10.1046 14.1046 11 13 11H2C0.89543 11 0 10.1046 0 9V6ZM4.5 6.75C4.08579 6.75 3.75 7.08579 3.75 7.5C3.75 7.91421 4.08579 8.25 4.5 8.25C4.91421 8.25 5.25 7.91421 5.25 7.5C5.25 7.08579 4.91421 6.75 4.5 6.75ZM6.75 7.5C6.75 7.08579 7.08579 6.75 7.5 6.75C7.91421 6.75 8.25 7.08579 8.25 7.5C8.25 7.91421 7.91421 8.25 7.5 8.25C7.08579 8.25 6.75 7.91421 6.75 7.5ZM10.5 6.75C10.0858 6.75 9.75 7.08579 9.75 7.5C9.75 7.91421 10.0858 8.25 10.5 8.25C10.9142 8.25 11.25 7.91421 11.25 7.5C11.25 7.08579 10.9142 6.75 10.5 6.75Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/container.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M2 1.5C2 1.77614 1.77614 2 1.5 2C1.22386 2 1 1.77614 1 1.5C1 1.22386 1.22386 1 1.5 1C1.77614 1 2 1.22386 2 1.5ZM5 13H10V2L5 2L5 13ZM4 13C4 13.5523 4.44772 14 5 14H10C10.5523 14 11 13.5523 11 13V2C11 1.44772 10.5523 1 10 1H5C4.44772 1 4 1.44771 4 2V13ZM13.5 2C13.7761 2 14 1.77614 14 1.5C14 1.22386 13.7761 1 13.5 1C13.2239 1 13 1.22386 13 1.5C13 1.77614 13.2239 2 13.5 2ZM2 3.5C2 3.77614 1.77614 4 1.5 4C1.22386 4 1 3.77614 1 3.5C1 3.22386 1.22386 3 1.5 3C1.77614 3 2 3.22386 2 3.5ZM13.5 4C13.7761 4 14 3.77614 14 3.5C14 3.22386 13.7761 3 13.5 3C13.2239 3 13 3.22386 13 3.5C13 3.77614 13.2239 4 13.5 4ZM2 5.5C2 5.77614 1.77614 6 1.5 6C1.22386 6 1 5.77614 1 5.5C1 5.22386 1.22386 5 1.5 5C1.77614 5 2 5.22386 2 5.5ZM13.5 6C13.7761 6 14 5.77614 14 5.5C14 5.22386 13.7761 5 13.5 5C13.2239 5 13 5.22386 13 5.5C13 5.77614 13.2239 6 13.5 6ZM2 7.5C2 7.77614 1.77614 8 1.5 8C1.22386 8 1 7.77614 1 7.5C1 7.22386 1.22386 7 1.5 7C1.77614 7 2 7.22386 2 7.5ZM13.5 8C13.7761 8 14 7.77614 14 7.5C14 7.22386 13.7761 7 13.5 7C13.2239 7 13 7.22386 13 7.5C13 7.77614 13.2239 8 13.5 8ZM2 9.5C2 9.77614 1.77614 10 1.5 10C1.22386 10 1 9.77614 1 9.5C1 9.22386 1.22386 9 1.5 9C1.77614 9 2 9.22386 2 9.5ZM13.5 10C13.7761 10 14 9.77614 14 9.5C14 9.22386 13.7761 9 13.5 9C13.2239 9 13 9.22386 13 9.5C13 9.77614 13.2239 10 13.5 10ZM2 11.5C2 11.7761 1.77614 12 1.5 12C1.22386 12 1 11.7761 1 11.5C1 11.2239 1.22386 11 1.5 11C1.77614 11 2 11.2239 2 11.5ZM13.5 12C13.7761 12 14 11.7761 14 11.5C14 11.2239 13.7761 11 13.5 11C13.2239 11 13 11.2239 13 11.5C13 11.7761 13.2239 12 13.5 12ZM2 13.5C2 13.7761 1.77614 14 1.5 14C1.22386 14 1 13.7761 1 13.5C1 13.2239 1.22386 13 1.5 13C1.77614 13 2 13.2239 2 13.5ZM13.5 14C13.7761 14 14 13.7761 14 13.5C14 13.2239 13.7761 13 13.5 13C13.2239 13 13 13.2239 13 13.5C13 13.7761 13.2239 14 13.5 14Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/index.ts
================================================
export { default as AvatarIcon } from './avatar.svelte';
export { default as BadgeIcon } from './badge.svelte';
export { default as ButtonIcon } from './button.svelte';
export { default as ContainerIcon } from './container.svelte';
export { default as InputIcon } from './input.svelte';
export { default as RadioIcon } from './radio.svelte';
export { default as SearchIcon } from './search.svelte';
export { default as SliderIcon } from './slider.svelte';


================================================
File: /src/docs/components/cmdk/framer/icons/input.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M6.5 1C6.22386 1 6 1.22386 6 1.5C6 1.77614 6.22386 2 6.5 2C7.12671 2 7.45718 2.20028 7.65563 2.47812C7.8781 2.78957 8 3.28837 8 4V11C8 11.7116 7.8781 12.2104 7.65563 12.5219C7.45718 12.7997 7.12671 13 6.5 13C6.22386 13 6 13.2239 6 13.5C6 13.7761 6.22386 14 6.5 14C7.37329 14 8.04282 13.7003 8.46937 13.1031C8.47976 13.0886 8.48997 13.0739 8.5 13.0591C8.51003 13.0739 8.52024 13.0886 8.53063 13.1031C8.95718 13.7003 9.62671 14 10.5 14C10.7761 14 11 13.7761 11 13.5C11 13.2239 10.7761 13 10.5 13C9.87329 13 9.54282 12.7997 9.34437 12.5219C9.1219 12.2104 9 11.7116 9 11V4C9 3.28837 9.1219 2.78957 9.34437 2.47812C9.54282 2.20028 9.87329 2 10.5 2C10.7761 2 11 1.77614 11 1.5C11 1.22386 10.7761 1 10.5 1C9.62671 1 8.95718 1.29972 8.53063 1.89688C8.52024 1.91143 8.51003 1.92611 8.5 1.9409C8.48997 1.92611 8.47976 1.91143 8.46937 1.89688C8.04282 1.29972 7.37329 1 6.5 1ZM14 5H11V4H14C14.5523 4 15 4.44772 15 5V10C15 10.5523 14.5523 11 14 11H11V10H14V5ZM6 4V5H1L1 10H6V11H1C0.447715 11 0 10.5523 0 10V5C0 4.44772 0.447715 4 1 4H6Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/radio.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M7.49985 0.877045C3.84216 0.877045 0.877014 3.84219 0.877014 7.49988C0.877014 11.1575 3.84216 14.1227 7.49985 14.1227C11.1575 14.1227 14.1227 11.1575 14.1227 7.49988C14.1227 3.84219 11.1575 0.877045 7.49985 0.877045ZM1.82701 7.49988C1.82701 4.36686 4.36683 1.82704 7.49985 1.82704C10.6328 1.82704 13.1727 4.36686 13.1727 7.49988C13.1727 10.6329 10.6328 13.1727 7.49985 13.1727C4.36683 13.1727 1.82701 10.6329 1.82701 7.49988ZM7.49999 9.49999C8.60456 9.49999 9.49999 8.60456 9.49999 7.49999C9.49999 6.39542 8.60456 5.49999 7.49999 5.49999C6.39542 5.49999 5.49999 6.39542 5.49999 7.49999C5.49999 8.60456 6.39542 9.49999 7.49999 9.49999Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/search.svelte
================================================
<svg
	xmlns="http://www.w3.org/2000/svg"
	class="h-6 w-6"
	fill="none"
	viewBox="0 0 24 24"
	stroke="currentColor"
	stroke-width={1.5}
>
	<path
		stroke-linecap="round"
		stroke-linejoin="round"
		d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/framer/icons/slider.svelte
================================================
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M10.3004 7.49991C10.3004 8.4943 9.49426 9.30041 8.49988 9.30041C7.50549 9.30041 6.69938 8.4943 6.69938 7.49991C6.69938 6.50553 7.50549 5.69942 8.49988 5.69942C9.49426 5.69942 10.3004 6.50553 10.3004 7.49991ZM11.205 8C10.9699 9.28029 9.84816 10.2504 8.49988 10.2504C7.1516 10.2504 6.0299 9.28029 5.79473 8H0.5C0.223858 8 0 7.77614 0 7.5C0 7.22386 0.223858 7 0.5 7H5.7947C6.0298 5.71962 7.15154 4.74942 8.49988 4.74942C9.84822 4.74942 10.97 5.71962 11.2051 7H14.5C14.7761 7 15 7.22386 15 7.5C15 7.77614 14.7761 8 14.5 8H11.205Z"
		fill="currentColor"
		fill-rule="evenodd"
		clip-rule="evenodd"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/linear/linear-cmdk.svelte
================================================
<script lang="ts">
	import type { ComponentType } from 'svelte';
	import { Command } from '$lib/index.js';
	import {
		AssignToIcon,
		AssignToMeIcon,
		ChangeLabelsIcon,
		ChangePriorityIcon,
		ChangeStatusIcon,
		RemoveLabelIcon,
		SetDueDateIcon
	} from './icons/index.js';
	import '$styles/cmdk/linear.postcss';

	type Item = {
		icon: ComponentType;
		label: string;
		shortcut: string[];
	};

	const items: Item[] = [
		{
			icon: AssignToIcon,
			label: 'Assign to...',
			shortcut: ['A']
		},
		{
			icon: AssignToMeIcon,
			label: 'Assign to me',
			shortcut: ['I']
		},
		{
			icon: ChangeStatusIcon,
			label: 'Change status...',
			shortcut: ['S']
		},
		{
			icon: ChangePriorityIcon,
			label: 'Change priority...',
			shortcut: ['P']
		},
		{
			icon: ChangeLabelsIcon,
			label: 'Change labels...',
			shortcut: ['L']
		},
		{
			icon: RemoveLabelIcon,
			label: 'Remove label...',
			shortcut: ['⇧', 'L']
		},
		{
			icon: SetDueDateIcon,
			label: 'Set due date...',
			shortcut: ['⇧', 'D']
		}
	];
</script>

<div class="linear">
	<Command.Root>
		<div data-cmdk-linear-badge="">Issue - FUN-343</div>
		<Command.Input autofocus placeholder="Type a command or search..." />
		<Command.List>
			<Command.Empty>No results found.</Command.Empty>
			{#each items as { label, shortcut, icon }}
				<Command.Item value={label}>
					<svelte:component this={icon} />
					{label}
					<div data-cmdk-linear-shortcuts="">
						{#each shortcut as key}
							<kbd>{key}</kbd>
						{/each}
					</div>
				</Command.Item>
			{/each}
		</Command.List>
	</Command.Root>
</div>


================================================
File: /src/docs/components/cmdk/linear/icons/assign-to-me.svelte
================================================
<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
	<path
		d="M7.00003 7C8.38128 7 9.50003 5.88125 9.50003 4.5C9.50003 3.11875 8.38128 2 7.00003 2C5.61878 2 4.50003 3.11875 4.50003 4.5C4.50003 5.88125 5.61878 7 7.00003 7Z"
	/>
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M7.00005 8C5.66505 8 3.00006 8.89333 3.00006 10.6667V11.3333C3.00006 11.7 3.22506 12 3.50006 12H3.98973C4.01095 11.9415 4.04535 11.8873 4.09266 11.8425L7.21783 8.88444C7.28966 8.81658 7.38297 8.77917 7.4796 8.77949C7.69459 8.78018 7.86826 8.96356 7.86753 9.1891L7.86214 10.629C9.00553 10.5858 10.0366 10.4354 10.9441 10.231C10.5539 8.74706 8.22087 8 7.00005 8Z"
	/>
	<path
		d="M6.72511 14.718C6.80609 14.7834 6.91767 14.7955 7.01074 14.749C7.10407 14.7036 7.16321 14.6087 7.16295 14.5047L7.1605 13.7849C11.4352 13.5894 12.9723 10.3023 12.9722 10.2563C12.9722 10.1147 12.8634 9.9971 12.7225 9.98626L12.7009 9.98634C12.5685 9.98689 12.4561 10.0833 12.4351 10.2142C12.4303 10.2413 10.4816 11.623 7.15364 11.7666L7.1504 10.8116C7.14981 10.662 7.02829 10.5412 6.87896 10.5418C6.81184 10.5421 6.74721 10.5674 6.69765 10.6127L4.54129 12.5896C4.43117 12.6906 4.42367 12.862 4.52453 12.9723C4.53428 12.9829 4.54488 12.9928 4.55621 13.0018L6.72511 14.718Z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/linear/icons/assign-to.svelte
================================================
<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
	<path
		d="M7 7a2.5 2.5 0 10.001-4.999A2.5 2.5 0 007 7zm0 1c-1.335 0-4 .893-4 2.667v.666c0 .367.225.667.5.667h2.049c.904-.909 2.417-1.911 4.727-2.009v-.72a.27.27 0 01.007-.063C9.397 8.404 7.898 8 7 8zm4.427 2.028a.266.266 0 01.286.032l2.163 1.723a.271.271 0 01.013.412l-2.163 1.97a.27.27 0 01-.452-.2v-.956c-3.328.133-5.282 1.508-5.287 1.535a.27.27 0 01-.266.227h-.022a.27.27 0 01-.249-.271c0-.046 1.549-3.328 5.824-3.509v-.72a.27.27 0 01.153-.243z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/linear/icons/change-labels.svelte
================================================
<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M10.2105 4C10.6337 4 11.0126 4.18857 11.24 4.48L14 8L11.24 11.52C11.0126 11.8114 10.6337 12 10.2105 12L3.26316 11.9943C2.56842 11.9943 2 11.4857 2 10.8571V5.14286C2 4.51429 2.56842 4.00571 3.26316 4.00571L10.2105 4ZM11.125 9C11.6773 9 12.125 8.55228 12.125 8C12.125 7.44772 11.6773 7 11.125 7C10.5727 7 10.125 7.44772 10.125 8C10.125 8.55228 10.5727 9 11.125 9Z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/linear/icons/change-priority.svelte
================================================
<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
	<rect x="1" y="8" width="3" height="6" rx="1" />
	<rect x="6" y="5" width="3" height="9" rx="1" />
	<rect x="11" y="2" width="3" height="12" rx="1" />
</svg>


================================================
File: /src/docs/components/cmdk/linear/icons/change-status.svelte
================================================
<svg width="16" height="16" viewBox="-1 -1 15 15" fill="currentColor">
	<path
		d="M10.5714 7C10.5714 8.97245 8.97245 10.5714 7 10.5714L6.99975 3.42857C8.9722 3.42857 10.5714 5.02755 10.5714 7Z"
	/>
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M7 12.5C10.0376 12.5 12.5 10.0376 12.5 7C12.5 3.96243 10.0376 1.5 7 1.5C3.96243 1.5 1.5 3.96243 1.5 7C1.5 10.0376 3.96243 12.5 7 12.5ZM7 14C10.866 14 14 10.866 14 7C14 3.13401 10.866 0 7 0C3.13401 0 0 3.13401 0 7C0 10.866 3.13401 14 7 14Z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/linear/icons/index.ts
================================================
export { default as AssignToIcon } from './assign-to.svelte';
export { default as AssignToMeIcon } from './assign-to-me.svelte';
export { default as ChangeLabelsIcon } from './change-labels.svelte';
export { default as ChangePriorityIcon } from './change-priority.svelte';
export { default as ChangeStatusIcon } from './change-status.svelte';
export { default as RemoveLabelIcon } from './remove-label.svelte';
export { default as SetDueDateIcon } from './set-due-date.svelte';


================================================
File: /src/docs/components/cmdk/linear/icons/remove-label.svelte
================================================
<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M10.2105 4C10.6337 4 11.0126 4.18857 11.24 4.48L14 8L11.24 11.52C11.0126 11.8114 10.6337 12 10.2105 12L3.26316 11.9943C2.56842 11.9943 2 11.4857 2 10.8571V5.14286C2 4.51429 2.56842 4.00571 3.26316 4.00571L10.2105 4ZM11.125 9C11.6773 9 12.125 8.55228 12.125 8C12.125 7.44772 11.6773 7 11.125 7C10.5727 7 10.125 7.44772 10.125 8C10.125 8.55228 10.5727 9 11.125 9Z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/linear/icons/set-due-date.svelte
================================================
<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M15 5C15 2.79086 13.2091 1 11 1H5C2.79086 1 1 2.79086 1 5V11C1 13.2091 2.79086 15 5 15H6.25C6.66421 15 7 14.6642 7 14.25C7 13.8358 6.66421 13.5 6.25 13.5H5C3.61929 13.5 2.5 12.3807 2.5 11V6H13.5V6.25C13.5 6.66421 13.8358 7 14.25 7C14.6642 7 15 6.66421 15 6.25V5ZM11.5001 8C11.9143 8 12.2501 8.33579 12.2501 8.75V10.75L14.2501 10.75C14.6643 10.75 15.0001 11.0858 15.0001 11.5C15.0001 11.9142 14.6643 12.25 14.2501 12.25L12.2501 12.25V14.25C12.2501 14.6642 11.9143 15 11.5001 15C11.0859 15 10.7501 14.6642 10.7501 14.25V12.25H8.75C8.33579 12.25 8 11.9142 8 11.5C8 11.0858 8.33579 10.75 8.75 10.75L10.7501 10.75V8.75C10.7501 8.33579 11.0859 8 11.5001 8Z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/raycast/item.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';
	import type { ItemProps } from '$lib/cmdk/index.js';
	export let value: string;
	export let isCommand: boolean = false;

	export let onSelect: ItemProps['onSelect'] = undefined;
</script>

<Command.Item {value} {onSelect}>
	<slot />
	<span data-cmdk-raycast-meta="">
		{#if isCommand}
			Command
		{:else}
			Application
		{/if}
	</span>
</Command.Item>


================================================
File: /src/docs/components/cmdk/raycast/raycast-cmdk.svelte
================================================
<script lang="ts">
	import { mode } from 'mode-watcher';
	import '$styles/cmdk/raycast.postcss';
	import Item from './item.svelte';
	import {
		LinearIcon,
		FigmaIcon,
		SlackIcon,
		YouTubeIcon,
		RaycastIcon
	} from '$docs/components/icons/index.js';
	import { ClipboardIcon, HammerIcon, RaycastDarkIcon, RaycastLightIcon } from './icons/index.js';
	import Logo from '$docs/components/logo.svelte';
	import { Command } from '$lib/index.js';
	import SubCommand from './sub-command.svelte';

	let value = 'linear';
	let inputEl: HTMLInputElement | undefined;
	let listEl: HTMLElement | undefined;
</script>

<div class="raycast">
	<Command.Root bind:value>
		<div data-cmdk-raycast-top-shine=""></div>
		<Command.Input autofocus placeholder="Search for apps and commands..." bind:el={inputEl} />
		<hr data-cmdk-raycast-loader="" />
		<Command.List bind:el={listEl}>
			<Command.Empty>No results found.</Command.Empty>
			<Command.Group heading="Suggestions">
				<Item value="linear">
					<Logo>
						<LinearIcon style={{ width: 12, height: 12 }} />
					</Logo>
					Linear
				</Item>
				<Item value="figma">
					<Logo>
						<FigmaIcon />
					</Logo>
					Figma
				</Item>
				<Item value="slack">
					<Logo>
						<SlackIcon />
					</Logo>
					Slack
				</Item>
				<Item value="youtube">
					<Logo>
						<YouTubeIcon />
					</Logo>
					YouTube
				</Item>
				<Item value="raycast">
					<Logo>
						<RaycastIcon />
					</Logo>
					Raycast
				</Item>
			</Command.Group>
			<Command.Group heading="Commands">
				<Item isCommand value="clipboard history">
					<Logo>
						<ClipboardIcon />
					</Logo>
					Clipboard History
				</Item>
				<Item isCommand value="import extension">
					<Logo>
						<HammerIcon />
					</Logo>
					Import Extension
				</Item>
				<Item isCommand value="manage extensions">
					<Logo>
						<HammerIcon />
					</Logo>
					Manage Extensions
				</Item>
			</Command.Group>
		</Command.List>

		<div data-cmdk-raycast-footer="">
			{#if $mode === 'dark'}
				<RaycastDarkIcon />
			{:else}
				<RaycastLightIcon />
			{/if}
			<button data-cmdk-raycast-open-trigger="">
				Open Application
				<kbd>↵</kbd>
			</button>

			<hr />

			<SubCommand {listEl} {inputEl} selectedValue={value} />
		</div>
	</Command.Root>
</div>


================================================
File: /src/docs/components/cmdk/raycast/sub-command.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';
	import { Popover } from 'bits-ui';
	import { onMount, tick } from 'svelte';
	import SubItem from './sub-item.svelte';
	import { FinderIcon, StarIcon, WindowIcon } from './icons/index.js';

	export let listEl: HTMLElement | undefined;
	export let inputEl: HTMLInputElement | undefined;
	export let selectedValue: string;
	let open = false;

	onMount(() => {
		function handleKeydown(e: KeyboardEvent) {
			if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
				e.preventDefault();
				open = true;
			}
		}

		document.addEventListener('keydown', handleKeydown);

		return () => {
			document.removeEventListener('keydown', handleKeydown);
		};
	});

	function handleStyleUpdates(open: boolean, el: HTMLElement | undefined) {
		if (!el) return;

		if (open) {
			el.style.overflow = 'hidden';
		} else {
			el.style.overflow = '';
		}
	}

	$: handleStyleUpdates(open, listEl);

	$: if (!open) {
		tick().then(() => inputEl?.focus());
	}
</script>

<Popover.Root bind:open preventScroll={true}>
	<Popover.Trigger asChild let:builder>
		<button
			use:builder.action
			{...builder}
			data-cmdk-raycast-subcommand-trigger=""
			aria-expanded={open}
		>
			Actions
			<kbd>⌘</kbd>
			<kbd>K</kbd>
		</button>
	</Popover.Trigger>
	{#if open}
		<Popover.Content class="raycast-submenu" side="top" align="end">
			<Command.Root>
				<Command.List>
					<Command.Group heading={selectedValue}>
						<SubItem shortcut="↵">
							<WindowIcon />
							Open Application
						</SubItem>
						<SubItem shortcut="⌘ ↵">
							<FinderIcon />
							Show in Finder
						</SubItem>
						<SubItem shortcut="⌘ I">
							<FinderIcon />
							Show Info in Finder
						</SubItem>
						<SubItem shortcut="⌘ ⇧ F">
							<StarIcon />
							Add to Favorites
						</SubItem>
					</Command.Group>
				</Command.List>
				<Command.Input placeholder="Search for actions..." />
			</Command.Root>
		</Popover.Content>
	{/if}
</Popover.Root>


================================================
File: /src/docs/components/cmdk/raycast/sub-item.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';
	export let shortcut: string;
</script>

<Command.Item>
	<slot />
	<div data-cmdk-raycast-submenu-shortcuts="">
		{#each shortcut.split(' ') as key, i (i)}
			<kbd>{key}</kbd>
		{/each}
	</div>
</Command.Item>


================================================
File: /src/docs/components/cmdk/raycast/icons/clipboard.svelte
================================================
<div data-cmdk-raycast-clipboard-icon="">
	<svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M6.07512 2.75H4.75C3.64543 2.75 2.75 3.64543 2.75 4.75V12.25C2.75 13.3546 3.64543 14.25 4.75 14.25H11.25C12.3546 14.25 13.25 13.3546 13.25 12.25V4.75C13.25 3.64543 12.3546 2.75 11.25 2.75H9.92488M9.88579 3.02472L9.5934 4.04809C9.39014 4.75952 8.73989 5.25 8 5.25V5.25C7.26011 5.25 6.60986 4.75952 6.4066 4.04809L6.11421 3.02472C5.93169 2.38591 6.41135 1.75 7.07573 1.75H8.92427C9.58865 1.75 10.0683 2.3859 9.88579 3.02472Z"
			stroke="currentColor"
			stroke-width="1.5"
			stroke-linecap="round"
			stroke-linejoin="round"
		/>
	</svg>
</div>


================================================
File: /src/docs/components/cmdk/raycast/icons/finder.svelte
================================================
<svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M5 4.75V6.25M11 4.75V6.25M8.75 1.75H3.75C2.64543 1.75 1.75 2.64543 1.75 3.75V12.25C1.75 13.3546 2.64543 14.25 3.75 14.25H8.75M8.75 1.75H12.25C13.3546 1.75 14.25 2.64543 14.25 3.75V12.25C14.25 13.3546 13.3546 14.25 12.25 14.25H8.75M8.75 1.75L7.08831 7.1505C6.9202 7.69686 7.32873 8.25 7.90037 8.25C8.36961 8.25 8.75 8.63039 8.75 9.09963V14.25M5 10.3203C5 10.3203 5.95605 11.25 8 11.25C10.0439 11.25 11 10.3203 11 10.3203"
		stroke="currentColor"
		stroke-width="1.5"
		stroke-linecap="round"
		stroke-linejoin="round"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/raycast/icons/hammer.svelte
================================================
<div data-cmdk-raycast-hammer-icon="">
	<svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M6.73762 6.19288L2.0488 11.2217C1.6504 11.649 1.6504 12.3418 2.0488 12.769L3.13083 13.9295C3.52923 14.3568 4.17515 14.3568 4.57355 13.9295L9.26238 8.90071M6.73762 6.19288L7.0983 5.80605C7.4967 5.37877 7.4967 4.686 7.0983 4.25872L6.01627 3.09822L6.37694 2.71139C7.57213 1.42954 9.50991 1.42954 10.7051 2.71139L13.9512 6.19288C14.3496 6.62017 14.3496 7.31293 13.9512 7.74021L12.8692 8.90071C12.4708 9.328 11.8248 9.328 11.4265 8.90071L11.0658 8.51388C10.6674 8.0866 10.0215 8.0866 9.62306 8.51388L9.26238 8.90071M6.73762 6.19288L9.26238 8.90071"
			stroke="currentColor"
			stroke-width="1.5"
			stroke-linecap="round"
			stroke-linejoin="round"
		/>
	</svg>
</div>


================================================
File: /src/docs/components/cmdk/raycast/icons/index.ts
================================================
export { default as ClipboardIcon } from './clipboard.svelte';
export { default as FinderIcon } from './finder.svelte';
export { default as HammerIcon } from './hammer.svelte';
export { default as RaycastDarkIcon } from './raycast-dark.svelte';
export { default as RaycastLightIcon } from './raycast-light.svelte';
export { default as StarIcon } from './star.svelte';
export { default as WindowIcon } from './window.svelte';


================================================
File: /src/docs/components/cmdk/raycast/icons/raycast-dark.svelte
================================================
<svg
	width="1024"
	height="1024"
	viewBox="0 0 1024 1024"
	fill="none"
	xmlns="http://www.w3.org/2000/svg"
>
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M301.144 634.799V722.856L90 511.712L134.244 467.804L301.144 634.799ZM389.201 722.856H301.144L512.288 934L556.34 889.996L389.201 722.856ZM889.996 555.956L934 511.904L512.096 90L468.092 134.052L634.799 300.952H534.026L417.657 184.679L373.605 228.683L446.065 301.144H395.631V628.561H723.048V577.934L795.509 650.395L839.561 606.391L723.048 489.878V389.105L889.996 555.956ZM323.17 278.926L279.166 322.978L326.385 370.198L370.39 326.145L323.17 278.926ZM697.855 653.61L653.994 697.615L701.214 744.834L745.218 700.782L697.855 653.61ZM228.731 373.413L184.679 417.465L301.144 533.93V445.826L228.731 373.413ZM578.174 722.856H490.07L606.535 839.321L650.587 795.269L578.174 722.856Z"
		fill="#FF6363"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/raycast/icons/raycast-light.svelte
================================================
<svg
	width="1024"
	height="1024"
	viewBox="0 0 1024 1024"
	fill="none"
	xmlns="http://www.w3.org/2000/svg"
>
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M934.302 511.971L890.259 556.017L723.156 388.902V300.754L934.302 511.971ZM511.897 89.5373L467.854 133.583L634.957 300.698H723.099L511.897 89.5373ZM417.334 184.275L373.235 228.377L445.776 300.923H533.918L417.334 184.275ZM723.099 490.061V578.209L795.641 650.755L839.74 606.652L723.099 490.061ZM697.868 653.965L723.099 628.732H395.313V300.754L370.081 325.987L322.772 278.675L278.56 322.833L325.869 370.146L300.638 395.379V446.071L228.097 373.525L183.997 417.627L300.638 534.275V634.871L133.59 467.925L89.4912 512.027L511.897 934.461L555.996 890.359L388.892 723.244H489.875L606.516 839.892L650.615 795.79L578.074 723.244H628.762L653.994 698.011L701.303 745.323L745.402 701.221L697.868 653.965Z"
		fill="#FF6363"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/raycast/icons/star.svelte
================================================
<svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M7.43376 2.17103C7.60585 1.60966 8.39415 1.60966 8.56624 2.17103L9.61978 5.60769C9.69652 5.85802 9.92611 6.02873 10.186 6.02873H13.6562C14.2231 6.02873 14.4665 6.75397 14.016 7.10088L11.1582 9.3015C10.9608 9.45349 10.8784 9.71341 10.9518 9.95262L12.0311 13.4735C12.2015 14.0292 11.5636 14.4777 11.1051 14.1246L8.35978 12.0106C8.14737 11.847 7.85263 11.847 7.64022 12.0106L4.89491 14.1246C4.43638 14.4777 3.79852 14.0292 3.96889 13.4735L5.04824 9.95262C5.12157 9.71341 5.03915 9.45349 4.84178 9.3015L1.98404 7.10088C1.53355 6.75397 1.77692 6.02873 2.34382 6.02873H5.81398C6.07389 6.02873 6.30348 5.85802 6.38022 5.60769L7.43376 2.17103Z"
		stroke="currentColor"
		stroke-width="1.5"
		stroke-linecap="round"
		stroke-linejoin="round"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/raycast/icons/window.svelte
================================================
<svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M14.25 4.75V3.75C14.25 2.64543 13.3546 1.75 12.25 1.75H3.75C2.64543 1.75 1.75 2.64543 1.75 3.75V4.75M14.25 4.75V12.25C14.25 13.3546 13.3546 14.25 12.25 14.25H3.75C2.64543 14.25 1.75 13.3546 1.75 12.25V4.75M14.25 4.75H1.75"
		stroke="currentColor"
		stroke-width="1.5"
		stroke-linecap="round"
		stroke-linejoin="round"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/vercel/home.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';
	import {
		ContactIcon,
		DocsIcon,
		FeedbackIcon,
		PlusIcon,
		ProjectsIcon,
		TeamsIcon
	} from './icons/index.js';
	import Item from './item.svelte';
	export let searchProjects: () => void;
</script>

<Command.Group heading="Projects">
	<Item shortcut="S P" onSelect={searchProjects}>
		<ProjectsIcon />
		Search Projects...
	</Item>
	<Item>
		<PlusIcon />
		Create New Project...
	</Item>
</Command.Group>
<Command.Group heading="Teams">
	<Item shortcut="⇧ P">
		<TeamsIcon />
		Search Teams...
	</Item>
	<Item>
		<PlusIcon />
		Create New Team...
	</Item>
</Command.Group>
<Command.Group heading="Help">
	<Item shortcut="⇧ D">
		<DocsIcon />
		Search Docs...
	</Item>
	<Item>
		<FeedbackIcon />
		Send Feedback...
	</Item>
	<Item>
		<ContactIcon />
		Contact Support
	</Item>
</Command.Group>


================================================
File: /src/docs/components/cmdk/vercel/item.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';

	export let shortcut: string = '';
	export let onSelect: ((value: string) => void) | undefined = undefined;
</script>

<Command.Item {onSelect}>
	<slot />
	{#if shortcut}
		<div data-cmdk-vercel-shortcuts="">
			{#each shortcut.split(' ') as key}
				<kbd>{key}</kbd>
			{/each}
		</div>
	{/if}
</Command.Item>


================================================
File: /src/docs/components/cmdk/vercel/projects.svelte
================================================
<script lang="ts">
	import Item from './item.svelte';
</script>

{#each { length: 6 } as _, i}
	<Item>
		Project {i + 1}
	</Item>
{/each}


================================================
File: /src/docs/components/cmdk/vercel/vercel-cmdk.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';
	import { isHTMLElement, kbd } from '$lib/internal/index.js';
	import Home from './home.svelte';
	import Projects from './projects.svelte';
	import '$styles/cmdk/vercel.postcss';

	let inputValue: string = '';

	let pages: string[] = ['home'];
	$: activePage = pages[pages.length - 1];
	$: isHome = activePage === 'home';

	function popPage() {
		const next = [...pages];
		next.splice(-1, 1);
		pages = next;
	}

	function bounce(node: HTMLElement) {
		node.style.transform = 'scale(0.96)';
		setTimeout(() => {
			node.style.transform = '';
		}, 100);

		inputValue = '';
	}

	function handleKeydown(e: KeyboardEvent) {
		const currTarget = e.currentTarget;
		if (!isHTMLElement(currTarget)) return;

		if (e.key === kbd.ENTER) {
			bounce(currTarget);
		}

		if (isHome || inputValue.length) {
			return;
		}

		if (e.key === kbd.BACKSPACE) {
			e.preventDefault();
			popPage();
			bounce(currTarget);
		}
	}
</script>

<div class="vercel">
	<Command.Root onKeydown={handleKeydown}>
		<div>
			{#each pages as page}
				<div data-cmdk-vercel-badge="">
					{page}
				</div>
			{/each}
		</div>
		<Command.Input autofocus placeholder="What do you need?" bind:value={inputValue} />
		<Command.List>
			<Command.Empty>No results found.</Command.Empty>
			{#if activePage === 'home'}
				<Home
					searchProjects={() => {
						pages = [...pages, 'projects'];
					}}
				/>
			{/if}
			{#if activePage === 'projects'}
				<Projects />
			{/if}
		</Command.List>
	</Command.Root>
</div>


================================================
File: /src/docs/components/cmdk/vercel/icons/contact.svelte
================================================
<svg
	fill="none"
	height="24"
	shape-rendering="geometricPrecision"
	stroke="currentColor"
	stroke-linecap="round"
	stroke-linejoin="round"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	width="24"
>
	<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
	<path d="M22 6l-10 7L2 6" />
</svg>


================================================
File: /src/docs/components/cmdk/vercel/icons/docs.svelte
================================================
<svg
	fill="none"
	height="24"
	shape-rendering="geometricPrecision"
	stroke="currentColor"
	stroke-linecap="round"
	stroke-linejoin="round"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	width="24"
>
	<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
	<path d="M14 2v6h6" />
	<path d="M16 13H8" />
	<path d="M16 17H8" />
	<path d="M10 9H8" />
</svg>


================================================
File: /src/docs/components/cmdk/vercel/icons/feedback.svelte
================================================
<svg
	fill="none"
	height="24"
	shape-rendering="geometricPrecision"
	stroke="currentColor"
	stroke-linecap="round"
	stroke-linejoin="round"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	width="24"
>
	<path
		d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"
	/>
</svg>


================================================
File: /src/docs/components/cmdk/vercel/icons/index.ts
================================================
export { default as ContactIcon } from './contact.svelte';
export { default as DocsIcon } from './docs.svelte';
export { default as FeedbackIcon } from './feedback.svelte';
export { default as PlusIcon } from './plus.svelte';
export { default as ProjectsIcon } from './projects.svelte';
export { default as TeamsIcon } from './teams.svelte';


================================================
File: /src/docs/components/cmdk/vercel/icons/plus.svelte
================================================
<svg
	fill="none"
	height="24"
	shape-rendering="geometricPrecision"
	stroke="currentColor"
	stroke-linecap="round"
	stroke-linejoin="round"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	width="24"
>
	<path d="M12 5v14" />
	<path d="M5 12h14" />
</svg>


================================================
File: /src/docs/components/cmdk/vercel/icons/projects.svelte
================================================
<svg
	fill="none"
	height="24"
	shape-rendering="geometricPrecision"
	stroke="currentColor"
	stroke-linecap="round"
	stroke-linejoin="round"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	width="24"
>
	<path d="M3 3h7v7H3z" />
	<path d="M14 3h7v7h-7z" />
	<path d="M14 14h7v7h-7z" />
	<path d="M3 14h7v7H3z" />
</svg>


================================================
File: /src/docs/components/cmdk/vercel/icons/teams.svelte
================================================
<svg
	fill="none"
	height="24"
	shape-rendering="geometricPrecision"
	stroke="currentColor"
	stroke-linecap="round"
	stroke-linejoin="round"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	width="24"
>
	<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
	<circle cx="9" cy="7" r="4" />
	<path d="M23 21v-2a4 4 0 00-3-3.87" />
	<path d="M16 3.13a4 4 0 010 7.75" />
</svg>


================================================
File: /src/docs/components/icons/copied.svelte
================================================
<svg
	width="16"
	height="16"
	stroke-width="1.5"
	viewBox="0 0 24 24"
	fill="none"
	xmlns="http://www.w3.org/2000/svg"
>
	<path d="M5 13L9 17L19 7" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" />
</svg>


================================================
File: /src/docs/components/icons/copy.svelte
================================================
<svg width="16" height="16" stroke-width="1.5" viewBox="0 0 24 24" fill="none">
	<path
		d="M19.4 20H9.6C9.26863 20 9 19.7314 9 19.4V9.6C9 9.26863 9.26863 9 9.6 9H19.4C19.7314 9 20 9.26863 20 9.6V19.4C20 19.7314 19.7314 20 19.4 20Z"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
	/>
	<path
		d="M15 9V4.6C15 4.26863 14.7314 4 14.4 4H4.6C4.26863 4 4 4.26863 4 4.6V14.4C4 14.7314 4.26863 15 4.6 15H9"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
	/>
</svg>


================================================
File: /src/docs/components/icons/figma.svelte
================================================
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48px" height="48px">
	<path fill="#e64a19" d="M26,17h-8c-3.866,0-7-3.134-7-7v0c0-3.866,3.134-7,7-7h8V17z" />
	<path fill="#7c4dff" d="M25,31h-7c-3.866,0-7-3.134-7-7v0c0-3.866,3.134-7,7-7h7V31z" />
	<path
		fill="#66bb6a"
		d="M18,45L18,45c-3.866,0-7-3.134-7-7v0c0-3.866,3.134-7,7-7h7v7C25,41.866,21.866,45,18,45z"
	/>
	<path fill="#ff7043" d="M32,17h-7V3h7c3.866,0,7,3.134,7,7v0C39,13.866,35.866,17,32,17z" />
	<circle cx="32" cy="24" r="7" fill="#29b6f6" />
</svg>


================================================
File: /src/docs/components/icons/framer.svelte
================================================
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 24">
	<path
		d="M 16 0 L 16 8 L 8 8 L 0 0 Z M 0 8 L 8 8 L 16 16 L 8 16 L 8 24 L 0 16 Z"
		fill="var(--highContrast)"
	/>
</svg>


================================================
File: /src/docs/components/icons/github.svelte
================================================
<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		d="M7 0.175049C3.128 0.175049 0 3.30305 0 7.17505C0 10.259 2.013 12.885 4.79 13.825C5.14 13.891 5.272 13.672 5.272 13.497V12.316C3.325 12.731 2.909 11.375 2.909 11.375C2.581 10.565 2.122 10.347 2.122 10.347C1.488 9.90905 2.166 9.93105 2.166 9.93105C2.866 9.97505 3.237 10.653 3.237 10.653C3.872 11.725 4.878 11.419 5.272 11.243C5.338 10.784 5.512 10.478 5.709 10.303C4.156 10.128 2.516 9.51605 2.516 6.84705C2.516 6.08105 2.778 5.46905 3.237 4.96605C3.172 4.79105 2.931 4.06905 3.303 3.10605C3.303 3.10605 3.893 2.90905 5.228 3.82805C5.79831 3.67179 6.38668 3.5911 6.978 3.58805C7.568 3.58805 8.181 3.67505 8.728 3.82805C10.063 2.93105 10.653 3.10605 10.653 3.10605C11.025 4.06905 10.784 4.79105 10.719 4.96605C11.179 5.44605 11.441 6.08105 11.441 6.84605C11.441 9.53705 9.8 10.128 8.247 10.303C8.487 10.522 8.728 10.937 8.728 11.593V13.519C8.728 13.716 8.859 13.934 9.209 13.847C11.988 12.884 14 10.259 14 7.17505C14 3.30305 10.872 0.175049 7 0.175049V0.175049Z"
		fill="currentColor"
	/>
</svg>


================================================
File: /src/docs/components/icons/index.ts
================================================
export { default as CopiedIcon } from './copied.svelte';
export { default as CopyIcon } from './copy.svelte';
export { default as FigmaIcon } from './figma.svelte';
export { default as FramerIcon } from './framer.svelte';
export { default as GitHubIcon } from './github.svelte';
export { default as LinearIcon } from './linear.svelte';
export { default as RaycastIcon } from './raycast.svelte';
export { default as SlackIcon } from './slack.svelte';
export { default as VercelIcon } from './vercel.svelte';
export { default as YouTubeIcon } from './youtube.svelte';


================================================
File: /src/docs/components/icons/linear.svelte
================================================
<script lang="ts">
	import { styleToString } from '$lib/internal/index.js';
	export let style: Record<PropertyKey, string | number | undefined> = {};
</script>

<svg width="64" height="64" viewBox="0 0 64 64" fill="none" style={styleToString(style)}>
	<path
		d="M0.403013 37.3991L26.6009 63.597C13.2225 61.3356 2.66442 50.7775 0.403013 37.3991Z"
		fill="#5E6AD2"
	/>
	<path
		d="M0 30.2868L33.7132 64C35.7182 63.8929 37.6742 63.6013 39.5645 63.142L0.85799 24.4355C0.398679 26.3259 0.10713 28.2818 0 30.2868Z"
		fill="#5E6AD2"
	/>
	<path
		d="M2.53593 19.4042L44.5958 61.4641C46.1277 60.8066 47.598 60.0331 48.9956 59.1546L4.84543 15.0044C3.96691 16.402 3.19339 17.8723 2.53593 19.4042Z"
		fill="#5E6AD2"
	/>
	<path
		d="M7.69501 11.1447C13.5677 4.32093 22.2677 0 31.9769 0C49.6628 0 64 14.3372 64 32.0231C64 41.7323 59.6791 50.4323 52.8553 56.305L7.69501 11.1447Z"
		fill="#5E6AD2"
	/>
</svg>


================================================
File: /src/docs/components/icons/raycast.svelte
================================================
<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M7 18.073V20.994L0 13.994L1.46 12.534L7 18.075V18.073ZM9.921 20.994H7L14 27.994L15.46 26.534L9.921 20.994V20.994ZM26.535 15.456L27.996 13.994L13.996 -0.00598145L12.538 1.46002L18.077 6.99802H14.73L10.864 3.14002L9.404 4.60002L11.809 7.00402H10.129V17.87H20.994V16.19L23.399 18.594L24.859 17.134L20.994 13.268V9.92102L26.534 15.456H26.535ZM7.73 6.27002L6.265 7.73202L7.833 9.29802L9.294 7.83802L7.73 6.27002ZM20.162 18.702L18.702 20.164L20.268 21.732L21.73 20.27L20.162 18.702V18.702ZM4.596 9.40402L3.134 10.866L7 14.732V11.809L4.596 9.40402ZM16.192 21H13.268L17.134 24.866L18.596 23.404L16.192 21Z"
		fill="#FF6363"
	/>
</svg>


================================================
File: /src/docs/components/icons/slack.svelte
================================================
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48px" height="48px">
	<path
		fill="#33d375"
		d="M33,8c0-2.209-1.791-4-4-4s-4,1.791-4,4c0,1.254,0,9.741,0,11c0,2.209,1.791,4,4,4s4-1.791,4-4	C33,17.741,33,9.254,33,8z"
	/>
	<path
		fill="#33d375"
		d="M43,19c0,2.209-1.791,4-4,4c-1.195,0-4,0-4,0s0-2.986,0-4c0-2.209,1.791-4,4-4S43,16.791,43,19z"
	/>
	<path
		fill="#40c4ff"
		d="M8,14c-2.209,0-4,1.791-4,4s1.791,4,4,4c1.254,0,9.741,0,11,0c2.209,0,4-1.791,4-4s-1.791-4-4-4	C17.741,14,9.254,14,8,14z"
	/>
	<path
		fill="#40c4ff"
		d="M19,4c2.209,0,4,1.791,4,4c0,1.195,0,4,0,4s-2.986,0-4,0c-2.209,0-4-1.791-4-4S16.791,4,19,4z"
	/>
	<path
		fill="#e91e63"
		d="M14,39.006C14,41.212,15.791,43,18,43s4-1.788,4-3.994c0-1.252,0-9.727,0-10.984	c0-2.206-1.791-3.994-4-3.994s-4,1.788-4,3.994C14,29.279,14,37.754,14,39.006z"
	/>
	<path
		fill="#e91e63"
		d="M4,28.022c0-2.206,1.791-3.994,4-3.994c1.195,0,4,0,4,0s0,2.981,0,3.994c0,2.206-1.791,3.994-4,3.994	S4,30.228,4,28.022z"
	/>
	<path
		fill="#ffc107"
		d="M39,33c2.209,0,4-1.791,4-4s-1.791-4-4-4c-1.254,0-9.741,0-11,0c-2.209,0-4,1.791-4,4s1.791,4,4,4	C29.258,33,37.746,33,39,33z"
	/>
	<path
		fill="#ffc107"
		d="M28,43c-2.209,0-4-1.791-4-4c0-1.195,0-4,0-4s2.986,0,4,0c2.209,0,4,1.791,4,4S30.209,43,28,43z"
	/>
</svg>


================================================
File: /src/docs/components/icons/vercel.svelte
================================================
<svg aria-label="Vercel Logo" fill="var(--highContrast)" height="26" viewBox="0 0 75 65">
	<path d="M37.59.25l36.95 64H.64l36.95-64z" />
</svg>


================================================
File: /src/docs/components/icons/youtube.svelte
================================================
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48px" height="48px">
	<path
		fill="#FF3D00"
		d="M43.2,33.9c-0.4,2.1-2.1,3.7-4.2,4c-3.3,0.5-8.8,1.1-15,1.1c-6.1,0-11.6-0.6-15-1.1c-2.1-0.3-3.8-1.9-4.2-4C4.4,31.6,4,28.2,4,24c0-4.2,0.4-7.6,0.8-9.9c0.4-2.1,2.1-3.7,4.2-4C12.3,9.6,17.8,9,24,9c6.2,0,11.6,0.6,15,1.1c2.1,0.3,3.8,1.9,4.2,4c0.4,2.3,0.9,5.7,0.9,9.9C44,28.2,43.6,31.6,43.2,33.9z"
	/>
	<path fill="#FFF" d="M20 31L20 17 32 24z" />
</svg>


================================================
File: /src/lib/index.ts
================================================
import { createState, defaultFilter } from './cmdk/command.js';
import {
	CommandRoot,
	CommandDialog,
	CommandEmpty,
	CommandList,
	CommandItem,
	CommandGroup,
	CommandInput,
	CommandLoading,
	CommandSeparator
} from './cmdk/index.js';

export * as Command from './cmdk/index.js';
export type * from './cmdk/types.js';
export { createState, defaultFilter };

export {
	CommandRoot,
	CommandDialog,
	CommandEmpty,
	CommandList,
	CommandItem,
	CommandGroup,
	CommandInput,
	CommandLoading,
	CommandSeparator
};


================================================
File: /src/lib/types.ts
================================================
import type {
	LoadingProps,
	CommandProps,
	EmptyProps,
	ItemProps,
	GroupProps,
	ListProps,
	InputProps,
	SeparatorProps,
	DialogProps,
	State
} from './cmdk/types.js';

export type {
	LoadingProps,
	CommandProps,
	EmptyProps,
	ItemProps,
	GroupProps,
	ListProps,
	InputProps,
	SeparatorProps,
	DialogProps,
	State
};


================================================
File: /src/lib/cmdk/command.ts
================================================
import { getContext, setContext, tick } from 'svelte';
import { commandScore } from '$lib/internal/command-score.js';
import type { CommandProps, Context, Group, State, StateStore } from './types.js';
import { get, writable } from 'svelte/store';
import {
	omit,
	generateId,
	toWritableStores,
	isUndefined,
	kbd,
	removeUndefined,
	effect
} from '$lib/internal/index.js';

const NAME = 'Command';
const STATE_NAME = 'CommandState';
const GROUP_NAME = 'CommandGroup';

export const LIST_SELECTOR = `[data-cmdk-list-sizer]`;
export const GROUP_SELECTOR = `[data-cmdk-group]`;
export const GROUP_ITEMS_SELECTOR = `[data-cmdk-group-items]`;
export const GROUP_HEADING_SELECTOR = `[data-cmdk-group-heading]`;
export const ITEM_SELECTOR = `[data-cmdk-item]`;
export const VALID_ITEM_SELECTOR = `${ITEM_SELECTOR}:not([aria-disabled="true"])`;
export const VALUE_ATTR = `data-value`;

export const defaultFilter: (value: string, search: string) => number = (value, search) =>
	commandScore(value, search);

export function getCtx() {
	return getContext<Context>(NAME);
}

export function getState() {
	return getContext<StateStore>(STATE_NAME);
}

export function createGroup(alwaysRender: boolean | undefined) {
	const id = generateId();

	setContext<Group>(GROUP_NAME, {
		id,
		alwaysRender: isUndefined(alwaysRender) ? false : alwaysRender
	});
	return { id };
}

export function getGroup() {
	const context = getContext<Group>(GROUP_NAME);
	if (!context) return undefined;
	return context;
}

export function createState(initialValues?: Partial<State>) {
	const defaultState: State = {
		search: '',
		value: '',
		filtered: {
			count: 0,
			items: new Map(),
			groups: new Set()
		}
	};
	const state = writable<State>(
		initialValues ? { ...defaultState, ...removeUndefined(initialValues) } : defaultState
	);
	return state;
}

const defaults = {
	label: 'Command menu',
	shouldFilter: true,
	loop: false,
	onValueChange: undefined,
	value: undefined,
	filter: defaultFilter,
	ids: {
		root: generateId(),
		list: generateId(),
		label: generateId(),
		input: generateId()
	}
} satisfies CommandProps;

export function createCommand(props: CommandProps) {
	const ids = {
		root: generateId(),
		list: generateId(),
		label: generateId(),
		input: generateId(),
		...props.ids
	};

	const withDefaults = {
		...defaults,
		...removeUndefined(props)
	} satisfies CommandProps;

	const state =
		props.state ??
		createState({
			value: withDefaults.value
		});

	const allItems = writable<Set<string>>(new Set()); // [...itemIds]
	const allGroups = writable<Map<string, Set<string>>>(new Map()); // groupId → [...itemIds]
	const allIds = writable<Map<string, string>>(new Map()); // id → value
	const commandEl = writable<HTMLDivElement | null>(null);

	const options = toWritableStores(omit(withDefaults, 'value', 'ids'));

	let $allItems = get(allItems);
	let $allGroups = get(allGroups);
	let $allIds = get(allIds);

	let shouldFilter = get(options.shouldFilter);
	let loop = get(options.loop);
	let label = get(options.label);
	let filter = get(options.filter);

	effect(options.shouldFilter, ($shouldFilter) => {
		shouldFilter = $shouldFilter;
	});

	effect(options.loop, ($loop) => {
		loop = $loop;
	});
	effect(options.filter, ($filter) => {
		filter = $filter;
	});
	effect(options.label, ($label) => {
		label = $label;
	});

	effect(allItems, (v) => {
		$allItems = v;
	});
	effect(allGroups, (v) => {
		$allGroups = v;
	});
	effect(allIds, (v) => {
		$allIds = v;
	});

	const context: Context = {
		value: (id, value) => {
			if (value !== $allIds.get(id)) {
				allIds.update(($allIds) => {
					$allIds.set(id, value);
					return $allIds;
				});
				state.update(($state) => {
					$state.filtered.items.set(id, score(value, $state.search));
					return $state;
				});
			}
		},
		// Track item lifecycle (add/remove)
		item: (id, groupId) => {
			allItems.update(($allItems) => $allItems.add(id));

			// Track this item within the group
			if (groupId) {
				allGroups.update(($allGroups) => {
					if (!$allGroups.has(groupId)) {
						$allGroups.set(groupId, new Set([id]));
					} else {
						$allGroups.get(groupId)?.add(id);
					}
					return $allGroups;
				});
			}
			state.update(($state) => {
				const filteredState = filterItems($state, shouldFilter);

				if (!filteredState.value) {
					const value = selectFirstItem();
					filteredState.value = value ?? '';
				}
				return filteredState;
			});

			return () => {
				allIds.update(($allIds) => {
					$allIds.delete(id);
					return $allIds;
				});
				allItems.update(($allItems) => {
					$allItems.delete(id);
					return $allItems;
				});
				state.update(($state) => {
					$state.filtered.items.delete(id);
					const selectedItem = getSelectedItem();

					const filteredState = filterItems($state);

					if (selectedItem?.getAttribute('id') === id) {
						filteredState.value = selectFirstItem() ?? '';
					}

					return $state;
				});
			};
		},
		group: (id) => {
			allGroups.update(($allGroups) => {
				if (!$allGroups.has(id)) {
					$allGroups.set(id, new Set());
				}
				return $allGroups;
			});
			return () => {
				allIds.update(($allIds) => {
					$allIds.delete(id);
					return $allIds;
				});
				allGroups.update(($allGroups) => {
					$allGroups.delete(id);
					return $allGroups;
				});
			};
		},
		filter: () => {
			return shouldFilter;
		},
		label: label || props['aria-label'] || '',
		commandEl,
		ids,
		updateState
	};

	function updateState<K extends keyof State>(key: K, value: State[K], preventScroll?: boolean) {
		state.update((curr) => {
			if (Object.is(curr[key], value)) return curr;
			curr[key] = value;

			if (key === 'search') {
				const filteredState = filterItems(curr, shouldFilter);
				curr = filteredState;
				const sortedState = sort(curr, shouldFilter);
				curr = sortedState;
				tick().then(() =>
					state.update((curr) => {
						curr.value = selectFirstItem() ?? '';
						props.onValueChange?.(curr.value);
						return curr;
					})
				);
			} else if (key === 'value') {
				props.onValueChange?.(curr.value);
				if (!preventScroll) {
					tick().then(() => scrollSelectedIntoView());
				}
			}
			return curr;
		});
	}

	function filterItems(state: State, shouldFilterVal?: boolean): State {
		const $shouldFilter = shouldFilterVal ?? shouldFilter;
		if (!state.search || !$shouldFilter) {
			state.filtered.count = $allItems.size;
			return state;
		}

		state.filtered.groups = new Set();
		let itemCount = 0;

		// check which items should be included
		for (const id of $allItems) {
			const value = $allIds.get(id);
			const rank = score(value, state.search);
			state.filtered.items.set(id, rank);
			if (rank > 0) {
				itemCount++;
			}
		}

		// Check which groups have at least 1 item shown
		for (const [groupId, group] of $allGroups) {
			for (const itemId of group) {
				const rank = state.filtered.items.get(itemId);
				if (rank && rank > 0) {
					state.filtered.groups.add(groupId);
				}
			}
		}

		state.filtered.count = itemCount;
		return state;
	}

	function sort(state: State, shouldFilterVal?: boolean) {
		const $shouldFilter = shouldFilterVal ?? shouldFilter;
		if (!state.search || !$shouldFilter) {
			return state;
		}

		const scores = state.filtered.items;

		// sort groups
		const groups: [string, number][] = [];

		for (const value of state.filtered.groups) {
			const items = $allGroups.get(value);
			if (!items) continue;
			// get max score of the group's items
			let max = 0;
			for (const item of items) {
				const score = scores.get(item);
				if (isUndefined(score)) continue;
				max = Math.max(score, max);
			}
			groups.push([value, max]);
		}

		// Sort items within groups to bottom
		// sort items outside of groups
		// sort groups to bottom (pushed all non-grouped items to the top)
		const rootEl = document.getElementById(ids.root);
		if (!rootEl) return state;
		const list = rootEl.querySelector(LIST_SELECTOR);

		const validItems = getValidItems(rootEl).sort((a, b) => {
			const valueA = a.getAttribute(VALUE_ATTR) ?? '';
			const valueB = b.getAttribute(VALUE_ATTR) ?? '';
			return (scores.get(valueA) ?? 0) - (scores.get(valueB) ?? 0);
		});

		for (const item of validItems) {
			const group = item.closest(GROUP_ITEMS_SELECTOR);
			const closest = item.closest(`${GROUP_ITEMS_SELECTOR} > *`);
			if (group) {
				if (item.parentElement === group) {
					group.appendChild(item);
				} else {
					if (!closest) continue;
					group.appendChild(closest);
				}
			} else {
				if (item.parentElement === list) {
					list?.appendChild(item);
				} else {
					if (!closest) continue;
					list?.appendChild(closest);
				}
			}
		}

		groups.sort((a, b) => b[1] - a[1]);

		for (const group of groups) {
			const el = rootEl.querySelector(`${GROUP_SELECTOR}[${VALUE_ATTR}="${group[0]}"]`);
			el?.parentElement?.appendChild(el);
		}

		return state;
	}

	function selectFirstItem() {
		const item = getValidItems().find((item) => !item.ariaDisabled);
		if (!item) return;
		const value = item.getAttribute(VALUE_ATTR);
		if (!value) return;
		return value;
	}

	function score(value: string | undefined, search: string) {
		const lowerCaseAndTrimmedValue = value?.toLowerCase().trim();
		const filterFn = filter;
		if (!filterFn) {
			return lowerCaseAndTrimmedValue ? defaultFilter(lowerCaseAndTrimmedValue, search) : 0;
		}
		return lowerCaseAndTrimmedValue ? filterFn(lowerCaseAndTrimmedValue, search) : 0;
	}

	function scrollSelectedIntoView() {
		const item = getSelectedItem();
		if (!item) {
			return;
		}
		if (item.parentElement?.firstChild === item) {
			tick().then(() =>
				item.closest(GROUP_SELECTOR)?.querySelector(GROUP_HEADING_SELECTOR)?.scrollIntoView({
					block: 'nearest'
				})
			);
		}
		tick().then(() => item.scrollIntoView({ block: 'nearest' }));
	}

	function getValidItems(rootElement?: HTMLElement) {
		const rootEl = rootElement ?? document.getElementById(ids.root);
		if (!rootEl) return [];
		return Array.from(rootEl.querySelectorAll(VALID_ITEM_SELECTOR)).filter(
			(el): el is HTMLElement => (el ? true : false)
		);
	}

	function getSelectedItem(rootElement?: HTMLElement) {
		const rootEl = rootElement ?? document.getElementById(ids.root);
		if (!rootEl) return;
		const selectedEl = rootEl.querySelector(`${VALID_ITEM_SELECTOR}[aria-selected="true"]`);
		if (!selectedEl) return;
		return selectedEl;
	}

	function updateSelectedToIndex(index: number) {
		const rootEl = document.getElementById(ids.root);
		if (!rootEl) return;
		const items = getValidItems(rootEl);
		const item = items[index];
		if (!item) return;
		updateState('value', item.getAttribute(VALUE_ATTR) ?? '');
	}

	function updateSelectedByChange(change: 1 | -1) {
		const selected = getSelectedItem();
		const items = getValidItems();
		const index = items.findIndex((item) => item === selected);

		// get item at this index
		let newSelected = items[index + change];

		if (loop) {
			if (index + change < 0) {
				newSelected = items[items.length - 1];
			} else if (index + change === items.length) {
				newSelected = items[0];
			} else {
				newSelected = items[index + change];
			}
		}

		if (newSelected) {
			updateState('value', newSelected.getAttribute(VALUE_ATTR) ?? '');
		}
	}

	function updateSelectedToGroup(change: 1 | -1) {
		const selected = getSelectedItem();
		let group = selected?.closest(GROUP_SELECTOR);
		let item: HTMLElement | undefined | null = undefined;

		while (group && !item) {
			group =
				change > 0
					? findNextSibling(group, GROUP_SELECTOR)
					: findPreviousSibling(group, GROUP_SELECTOR);
			item = group?.querySelector(VALID_ITEM_SELECTOR);
		}

		if (item) {
			updateState('value', item.getAttribute(VALUE_ATTR) ?? '');
		} else {
			updateSelectedByChange(change);
		}
	}

	function last() {
		return updateSelectedToIndex(getValidItems().length - 1);
	}

	function next(e: KeyboardEvent) {
		e.preventDefault();

		if (e.metaKey) {
			last();
		} else if (e.altKey) {
			updateSelectedToGroup(1);
		} else {
			updateSelectedByChange(1);
		}
	}

	function prev(e: KeyboardEvent) {
		e.preventDefault();

		if (e.metaKey) {
			updateSelectedToIndex(0);
		} else if (e.altKey) {
			updateSelectedToGroup(-1);
		} else {
			updateSelectedByChange(-1);
		}
	}

	function handleRootKeydown(e: KeyboardEvent) {
		switch (e.key) {
			case kbd.ARROW_DOWN:
				next(e);
				break;
			case kbd.ARROW_UP:
				prev(e);
				break;
			case kbd.HOME:
				// first item
				e.preventDefault();
				updateSelectedToIndex(0);
				break;
			case kbd.END:
				// last item
				e.preventDefault();
				last();
				break;
			case kbd.ENTER: {
				e.preventDefault();
				const item = getSelectedItem() as HTMLElement;
				if (item) {
					item?.click();
				}
			}
		}
	}

	setContext(NAME, context);

	const stateStore = {
		subscribe: state.subscribe,
		update: state.update,
		set: state.set,
		updateState
	};

	setContext(STATE_NAME, stateStore);

	return {
		state: stateStore,
		handleRootKeydown,
		commandEl,
		ids
	};
}

function findNextSibling(el: Element, selector: string) {
	let sibling = el.nextElementSibling;

	while (sibling) {
		if (sibling.matches(selector)) return sibling;
		sibling = sibling.nextElementSibling;
	}
}

function findPreviousSibling(el: Element, selector: string) {
	let sibling = el.previousElementSibling;

	while (sibling) {
		if (sibling.matches(selector)) return sibling;
		sibling = sibling.previousElementSibling;
	}
}


================================================
File: /src/lib/cmdk/index.ts
================================================
import type {
	LoadingProps,
	CommandProps,
	EmptyProps,
	ItemProps,
	GroupProps,
	ListProps,
	InputProps,
	SeparatorProps,
	DialogProps
} from './types.js';

import Root from './components/Command.svelte';
import Dialog from './components/CommandDialog.svelte';
import Empty from './components/CommandEmpty.svelte';
import Group from './components/CommandGroup.svelte';
import Input from './components/CommandInput.svelte';
import Item from './components/CommandItem.svelte';
import List from './components/CommandList.svelte';
import Loading from './components/CommandLoading.svelte';
import Separator from './components/CommandSeparator.svelte';

export {
	// Components
	Root,
	Dialog,
	Empty,
	Group,
	Input,
	Item,
	List,
	Loading,
	Separator,
	//
	Root as CommandRoot,
	Dialog as CommandDialog,
	Empty as CommandEmpty,
	Group as CommandGroup,
	Input as CommandInput,
	Item as CommandItem,
	List as CommandList,
	Loading as CommandLoading,
	Separator as CommandSeparator
};

export type {
	LoadingProps,
	DialogProps,
	CommandProps,
	EmptyProps,
	ItemProps,
	GroupProps,
	ListProps,
	InputProps,
	SeparatorProps
};


================================================
File: /src/lib/cmdk/types.ts
================================================
/* eslint-disable @typescript-eslint/ban-types */
import type { Expand, HTMLDivAttributes, Transition, PrefixKeys } from '$lib/internal/index.js';
import type { Dialog as DialogPrimitive } from 'bits-ui';
import type { HTMLInputAttributes } from 'svelte/elements';
import type { Writable } from 'svelte/store';

//
// PROPS
//

export type LoadingProps = {
	/** Estimated loading progress */
	progress?: number;

	/**
	 * Whether to delegate rendering to a custom element.
	 *
	 * The contents within the `Loading` component should be marked
	 * as `aria-hidden` to prevent screen readers from reading the
	 * contents while loading.
	 */
	asChild?: boolean;
} & HTMLDivAttributes;

export type EmptyProps = {
	/**
	 * Whether to delegate rendering to a custom element.
	 *
	 * Only receives `attrs`, no `action`.
	 */
	asChild?: boolean;
} & HTMLDivAttributes;

export type SeparatorProps = {
	/**
	 * Whether this separator is always rendered, regardless
	 * of the filter.
	 */
	alwaysRender?: boolean;

	/**
	 * Whether to delegate rendering to a custom element.
	 */
	asChild?: boolean;
} & HTMLDivAttributes;

type BaseCommandProps = {
	/**
	 * Controlled state store for the command menu.
	 * Initialize state using the `createState` function.
	 */
	state?: Writable<State>;

	/**
	 * An accessible label for the command menu.
	 * Not visible & only used for screen readers.
	 */
	label?: string;

	/**
	 * Optionally set to `false` to turn off the automatic filtering
	 * and sorting. If `false`, you must conditionally render valid
	 * items yourself.
	 */
	shouldFilter?: boolean;

	/**
	 * A custom filter function for whether each command item should
	 * match the query. It should return a number between `0` and `1`,
	 * with `1` being a perfect match, and `0` being no match, resulting
	 * in the item being hidden entirely.
	 *
	 * By default, it will use the `command-score` package to score.
	 */
	filter?: (value: string, search: string) => number;

	/**
	 * Optionally provide or bind to the selected command menu item.
	 */
	value?: string;

	/**
	 * A function that is called when the selected command menu item
	 * changes. It receives the new value as an argument.
	 */
	onValueChange?: (value: string) => void;

	/**
	 * Optionally set to `true` to enable looping through the items
	 * when the user reaches the end of the list using the keyboard.
	 */
	loop?: boolean;
};

export type CommandProps = Expand<
	BaseCommandProps & {
		/**
		 * Optionally provide custom ids for the command menu
		 * elements. These ids should be unique and are only
		 * necessary in very specific cases. Use with caution.
		 */
		ids?: Partial<CommandIds>;
	}
> &
	HTMLDivAttributes & {
		onKeydown?: (e: KeyboardEvent) => void;
		asChild?: boolean;
	};

export type ListProps = {
	/**
	 * The list element
	 */
	el?: HTMLElement;

	/**
	 * Whether to delegate rendering to a custom element.
	 *
	 * Provides 2 slot props: `container` & `list`.
	 * Container only has an `attrs` property, while `list` has
	 * `attrs` & `action` to be applied to the respective elements.
	 *
	 * The `list` wraps the `sizer`, and the `sizer` wraps the `items`, and
	 * is responsible for measuring the height of the items and setting the
	 * CSS variable to the height of the items.
	 */
	asChild?: boolean;
} & HTMLDivAttributes;

export type InputProps = {
	/**
	 * The input element
	 */
	el?: HTMLInputElement;

	/**
	 * Whether to delegate rendering to a custom element.
	 */
	asChild?: boolean;
} & HTMLInputAttributes;

export type GroupProps = {
	/**
	 * Optional heading to render for the group
	 */
	heading?: string;

	/**
	 * If heading isn't provided, you must provide a unique
	 * value for the group.
	 */
	value?: string;

	/**
	 * Whether or not this group is always rendered,
	 * regardless of filtering.
	 */
	alwaysRender?: boolean;

	/**
	 * Whether to delegate rendering to custom elements.
	 *
	 * Provides 3 slot props: `container`, `heading`, and `group`.
	 * Container has `attrs` & `action`, while `heading` & `group`
	 * only have `attrs` to be applied to the respective elements.
	 */
	asChild?: boolean;
} & HTMLDivAttributes;

export type ItemProps = {
	/**
	 * Whether this item is disabled.
	 */
	disabled?: boolean;

	/**
	 * A function called when this item is selected, either
	 * via click or keyboard selection.
	 */
	onSelect?: (value: string) => void;

	/**
	 * A unique value for this item.
	 * If not provided, it will be inferred from the rendered
	 * `textContent`. If your `textContent` is dynamic, you must
	 * provide a stable unique `value`.
	 */
	value?: string;

	/**
	 * Whether or not this item is always rendered,
	 * regardless of filtering.
	 */
	alwaysRender?: boolean;

	/**
	 * Whether to delegate rendering to a custom element.
	 * Will pass the `attrs` & `action` to be applied to the custom element.
	 */
	asChild?: boolean;

	/**
	 * Optionally override the default `id` generated for this item.
	 * NOTE: This must be unique across all items and is only necessary
	 * in very specific cases.
	 */
	id?: string;
} & HTMLDivAttributes;

type TransitionProps =
	| 'transition'
	| 'transitionConfig'
	| 'inTransition'
	| 'inTransitionConfig'
	| 'outTransition'
	| 'outTransitionConfig';

export type OverlayProps<
	T extends Transition = Transition,
	In extends Transition = Transition,
	Out extends Transition = Transition
> = PrefixKeys<Pick<DialogPrimitive.OverlayProps<T, In, Out>, TransitionProps>, 'overlay'> & {
	overlayClasses?: string;
};

export type ContentProps<
	T extends Transition = Transition,
	In extends Transition = Transition,
	Out extends Transition = Transition
> = PrefixKeys<Pick<DialogPrimitive.ContentProps<T, In, Out>, TransitionProps>, 'content'> & {
	contentClasses?: string;
};

export type DialogProps<
	ContentT extends Transition = Transition,
	ContentIn extends Transition = Transition,
	ContentOut extends Transition = Transition,
	OverlayT extends Transition = Transition,
	OverlayIn extends Transition = Transition,
	OverlayOut extends Transition = Transition
> = CommandProps &
	DialogPrimitive.Props &
	OverlayProps<OverlayT, OverlayIn, OverlayOut> &
	ContentProps<ContentT, ContentIn, ContentOut>;

//
// Events
//

export type InputEvents = {
	keydown: KeyboardEvent;
	blur: FocusEvent;
	input: Event;
	focus: FocusEvent;
	change: Event;
};

//
// Internal
//
export type CommandOptionStores = {
	[K in keyof Omit<Required<BaseCommandProps>, 'value'>]: Writable<CommandProps[K]>;
};

export type State = {
	/** The value of the search query */
	search: string;
	/** The value of the selected command menu item */
	value: string;
	/** The filtered items */
	filtered: {
		/** The count of all visible items. */
		count: number;
		/** Map from visible item id to its search store. */
		items: Map<string, number>;
		/** Set of groups with at least one visible item. */
		groups: Set<string>;
	};
};

export type CommandIds = Record<'root' | 'label' | 'input' | 'list', string>;

export type Context = {
	value: (id: string, value: string) => void;
	item: (id: string, groupId: string | undefined) => () => void;
	group: (id: string) => () => void;
	filter: () => boolean;
	label: string;
	commandEl: Writable<HTMLElement | null>;
	ids: CommandIds;
	updateState: UpdateState;
};

type UpdateState = <K extends keyof State>(
	key: K,
	value: State[K],
	preventScroll?: boolean
) => void;

export type ConextStore = Writable<Context>;

export type StateStore = Writable<State> & {
	updateState: UpdateState;
};

export type Group = {
	id: string;
	alwaysRender: boolean;
};


================================================
File: /src/lib/cmdk/components/Command.svelte
================================================
<script lang="ts">
	import {
		addEventListener,
		executeCallbacks,
		srOnlyStyles,
		styleToString
	} from '$lib/internal/index.js';
	import { createCommand } from '../command.js';
	import type { CommandProps } from '../types.js';

	type $$Props = CommandProps;

	export let label: $$Props['label'] = undefined;
	export let shouldFilter: $$Props['shouldFilter'] = true;
	export let filter: $$Props['filter'] = undefined;
	export let value: $$Props['value'] = undefined;
	export let onValueChange: $$Props['onValueChange'] = undefined;
	export let loop: $$Props['loop'] = undefined;
	export let onKeydown: $$Props['onKeydown'] = undefined;
	export let state: $$Props['state'] = undefined;
	export let ids: $$Props['ids'] = undefined;
	export let asChild: $$Props['asChild'] = false;

	const {
		commandEl,
		handleRootKeydown,
		ids: commandIds,
		state: stateStore
	} = createCommand({
		label,
		shouldFilter,
		filter,
		value,
		onValueChange: (next) => {
			if (next !== value) {
				value = next;
				onValueChange?.(next);
			}
		},
		loop,
		state,
		ids
	});

	function syncValueAndState(value: string | undefined) {
		if (value && value !== $stateStore.value) {
			$stateStore.value = value;
		}
	}

	$: syncValueAndState(value);

	function rootAction(node: HTMLDivElement) {
		commandEl.set(node);

		const unsubEvents = executeCallbacks(addEventListener(node, 'keydown', handleKeydown));

		return {
			destroy: unsubEvents
		};
	}

	const rootAttrs = {
		role: 'application',
		id: commandIds.root,
		'data-cmdk-root': ''
	};

	const labelAttrs = {
		'data-cmdk-label': '',
		for: commandIds.input,
		id: commandIds.label,
		style: styleToString(srOnlyStyles)
	};

	function handleKeydown(e: KeyboardEvent) {
		onKeydown?.(e);
		if (e.defaultPrevented) return;
		handleRootKeydown(e);
	}

	const root = {
		action: rootAction,
		attrs: rootAttrs
	};

	$: slotProps = {
		root,
		label: { attrs: labelAttrs },
		stateStore,
		state: $stateStore
	};
</script>

{#if asChild}
	<slot {...slotProps} />
{:else}
	<div use:rootAction {...rootAttrs} {...$$restProps}>
		<!-- svelte-ignore a11y-label-has-associated-control applied in attrs -->
		<label {...labelAttrs}>
			{label ?? ''}
		</label>
		<slot {...slotProps} />
	</div>
{/if}


================================================
File: /src/lib/cmdk/components/CommandDialog.svelte
================================================
<script lang="ts">
	import type { DialogProps } from '../types.js';
	import { Dialog as DialogPrimitive } from 'bits-ui';
	import type { Transition } from '$lib/internal/types.js';
	import { Command } from '$lib/index.js';

	type ContentT = $$Generic<Transition>;
	type ContentIn = $$Generic<Transition>;
	type ContentOut = $$Generic<Transition>;
	type OverlayT = $$Generic<Transition>;
	type OverlayIn = $$Generic<Transition>;
	type OverlayOut = $$Generic<Transition>;

	type $$Props = DialogProps<ContentT, ContentIn, ContentOut, OverlayT, OverlayIn, OverlayOut>;

	export let open: $$Props['open'] = false;
	export let value: $$Props['value'] = undefined;
	export let portal: $$Props['portal'] = undefined;
	export let overlayClasses: $$Props['overlayClasses'] = undefined;
	export let contentClasses: $$Props['contentClasses'] = undefined;

	export let contentTransition: $$Props['contentTransition'] = undefined;
	export let contentTransitionConfig: $$Props['contentTransitionConfig'] = undefined;
	export let contentInTransition: $$Props['contentInTransition'] = undefined;
	export let contentInTransitionConfig: $$Props['contentInTransitionConfig'] = undefined;
	export let contentOutTransition: $$Props['contentOutTransition'] = undefined;
	export let contentOutTransitionConfig: $$Props['contentOutTransitionConfig'] = undefined;

	export let overlayTransition: $$Props['overlayTransition'] = undefined;
	export let overlayTransitionConfig: $$Props['overlayTransitionConfig'] = undefined;
	export let overlayInTransition: $$Props['overlayInTransition'] = undefined;
	export let overlayInTransitionConfig: $$Props['overlayInTransitionConfig'] = undefined;
	export let overlayOutTransition: $$Props['overlayOutTransition'] = undefined;
	export let overlayOutTransitionConfig: $$Props['overlayOutTransitionConfig'] = undefined;

	$: overlayProps = {
		class: overlayClasses,
		transition: overlayTransition,
		transitionConfig: overlayTransitionConfig,
		inTransition: overlayInTransition,
		inTransitionConfig: overlayInTransitionConfig,
		outTransition: overlayOutTransition,
		outTransitionConfig: overlayOutTransitionConfig,
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		'data-cmdk-overlay': '' as any
	};

	$: contentProps = {
		class: contentClasses,
		transition: contentTransition,
		transitionConfig: contentTransitionConfig,
		inTransition: contentInTransition,
		inTransitionConfig: contentInTransitionConfig,
		outTransition: contentOutTransition,
		outTransitionConfig: contentOutTransitionConfig,
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		'data-cmdk-dialog': '' as any
	};

	export let label: $$Props['label'] = undefined;
</script>

<DialogPrimitive.Root bind:open {...$$restProps}>
	{#if portal === null}
		<DialogPrimitive.Overlay {...overlayProps} />
		<DialogPrimitive.Content aria-label={label} {...contentProps}>
			<Command.Root {...$$restProps} bind:value>
				<slot />
			</Command.Root>
		</DialogPrimitive.Content>
	{:else}
		<DialogPrimitive.Portal>
			<DialogPrimitive.Overlay {...overlayProps} />
			<DialogPrimitive.Content aria-label={label} {...contentProps}>
				<Command.Root {...$$restProps} bind:value>
					<slot />
				</Command.Root>
			</DialogPrimitive.Content>
		</DialogPrimitive.Portal>
	{/if}
</DialogPrimitive.Root>


================================================
File: /src/lib/cmdk/components/CommandEmpty.svelte
================================================
<script lang="ts">
	import { onMount } from 'svelte';
	import { getState } from '../command.js';
	import type { EmptyProps } from '../types.js';

	type $$Props = EmptyProps;

	export let asChild: $$Props['asChild'] = false;

	let isFirstRender = true;

	onMount(() => {
		isFirstRender = false;
	});

	const state = getState();

	$: render = $state.filtered.count === 0;

	const attrs = {
		'data-cmdk-empty': '',
		role: 'presentation'
	};
</script>

{#if !isFirstRender && render}
	{#if asChild}
		<slot {attrs} />
	{:else}
		<div {...attrs} {...$$restProps}>
			<slot />
		</div>
	{/if}
{/if}


================================================
File: /src/lib/cmdk/components/CommandGroup.svelte
================================================
<script lang="ts">
	import { generateId } from '$lib/internal/index.js';
	import { derived } from 'svelte/store';
	import { VALUE_ATTR, getCtx, getState, createGroup } from '../command.js';
	import type { GroupProps } from '../types.js';
	import { onMount } from 'svelte';

	type $$Props = GroupProps;

	export let heading: $$Props['heading'] = undefined;
	export let value = '';
	export let alwaysRender: $$Props['alwaysRender'] = false;
	export let asChild: $$Props['asChild'] = false;

	const { id } = createGroup(alwaysRender);

	const context = getCtx();
	const state = getState();
	const headingId = generateId();

	const render = derived(state, ($state) => {
		if (alwaysRender) return true;
		if (context.filter() === false) return true;
		if (!$state.search) return true;
		return $state.filtered.groups.has(id);
	});

	onMount(() => {
		const unsubGroup = context.group(id);
		return unsubGroup;
	});

	function containerAction(node: HTMLElement) {
		if (value) {
			context.value(id, value);
			node.setAttribute(VALUE_ATTR, value);
			return;
		}

		if (heading) {
			value = heading.trim().toLowerCase();
		} else if (node.textContent) {
			value = node.textContent.trim().toLowerCase();
		}

		context.value(id, value);
		node.setAttribute(VALUE_ATTR, value);
	}

	$: containerAttrs = {
		'data-cmdk-group': '',
		role: 'presentation',
		hidden: $render ? undefined : true,
		'data-value': value
	};

	const headingAttrs = {
		'data-cmdk-group-heading': '',
		'aria-hidden': true,
		id: headingId
	};

	$: groupAttrs = {
		'data-cmdk-group-items': '',
		role: 'group',
		'aria-labelledby': heading ? headingId : undefined
	};

	$: container = {
		action: containerAction,
		attrs: containerAttrs
	};

	$: group = {
		attrs: groupAttrs
	};
</script>

{#if asChild}
	<slot {container} {group} heading={{ attrs: headingAttrs }} />
{:else}
	<div use:containerAction {...containerAttrs} {...$$restProps}>
		{#if heading}
			<div {...headingAttrs}>
				{heading}
			</div>
		{/if}
		<div {...groupAttrs}>
			<slot {container} {group} heading={{ attrs: headingAttrs }} />
		</div>
	</div>
{/if}


================================================
File: /src/lib/cmdk/components/CommandInput.svelte
================================================
<script lang="ts">
	import { derived, get } from 'svelte/store';
	import { ITEM_SELECTOR, VALUE_ATTR, getCtx, getState } from '../command.js';
	import { addEventListener, isBrowser } from '$lib/internal/index.js';
	import type { InputEvents, InputProps } from '../types.js';
	import { sleep } from '$lib/internal/helpers/sleep.js';

	type $$Props = InputProps;
	type $$Events = InputEvents;

	const { ids, commandEl } = getCtx();
	const state = getState();
	const search = derived(state, ($state) => $state.search);
	const valueStore = derived(state, ($state) => $state.value);

	export let autofocus: $$Props['autofocus'] = undefined;
	export let value: $$Props['value'] = get(search);
	export let asChild: $$Props['asChild'] = false;

	export let el: HTMLElement | undefined = undefined;

	const selectedItemId = derived([valueStore, commandEl], ([$value, $commandEl]) => {
		if (!isBrowser) return undefined;
		const item = $commandEl?.querySelector(`${ITEM_SELECTOR}[${VALUE_ATTR}="${$value}"]`);
		return item?.getAttribute('id');
	});

	function handleValueUpdate(v: string) {
		state.updateState('search', v);
	}

	function action(node: HTMLInputElement) {
		if (autofocus) {
			sleep(10).then(() => node.focus());
		}
		if (asChild) {
			const unsubEvents = addEventListener(node, 'change', (e) => {
				const currTarget = e.currentTarget as HTMLInputElement;
				state.updateState('search', currTarget.value as string);
			});

			return {
				destroy: unsubEvents
			};
		}
	}

	$: handleValueUpdate(value);

	let attrs: Record<string, unknown>;

	$: attrs = {
		type: 'text',
		'data-cmdk-input': '',
		autocomplete: 'off',
		autocorrect: 'off',
		spellcheck: false,
		'aria-autocomplete': 'list',
		role: 'combobox',
		'aria-expanded': true,
		'aria-controls': ids.list,
		'aria-labelledby': ids.label,
		'aria-activedescendant': $selectedItemId ?? undefined,
		id: ids.input
	};
</script>

{#if asChild}
	<slot {action} {attrs} />
{:else}
	<input
		bind:this={el}
		{...attrs}
		bind:value
		use:action
		{...$$restProps}
		on:keydown
		on:input
		on:focus
		on:blur
		on:change
	/>
{/if}


================================================
File: /src/lib/cmdk/components/CommandItem.svelte
================================================
<script lang="ts">
	import {
		addEventListener,
		executeCallbacks,
		generateId,
		isUndefined
	} from '$lib/internal/index.js';
	import { onMount } from 'svelte';
	import { VALUE_ATTR, getCtx, getGroup, getState } from '../command.js';
	import type { ItemProps } from '../types.js';
	import { derived } from 'svelte/store';

	type $$Props = ItemProps;

	export let disabled: $$Props['disabled'] = false;
	export let value: string = '';
	export let onSelect: $$Props['onSelect'] = undefined;
	export let alwaysRender: $$Props['alwaysRender'] = false;
	export let asChild: $$Props['asChild'] = false;
	export let id: string = generateId();

	const groupContext = getGroup();
	const context = getCtx();
	const state = getState();

	const trueAlwaysRender = alwaysRender ?? groupContext?.alwaysRender;

	const render = derived(state, ($state) => {
		if (trueAlwaysRender || context.filter() === false || !$state.search) return true;
		const currentScore = $state.filtered.items.get(id);
		if (isUndefined(currentScore)) return false;
		return currentScore > 0;
	});

	let isFirstRender = true;

	onMount(() => {
		isFirstRender = false;
		const unsub = context.item(id, groupContext?.id);
		return unsub;
	});

	const selected = derived(state, ($state) => $state.value === value);

	function action(node: HTMLElement) {
		if (!value && node.textContent) {
			value = node.textContent.trim().toLowerCase();
		}
		context.value(id, value);
		node.setAttribute(VALUE_ATTR, value);

		const unsubEvents = executeCallbacks(
			addEventListener(node, 'pointermove', () => {
				if (disabled) return;
				select();
			}),
			addEventListener(node, 'click', () => {
				if (disabled) return;
				handleItemClick();
			})
		);

		return {
			destroy() {
				unsubEvents();
			}
		};
	}

	function handleItemClick() {
		select();
		onSelect?.(value);
	}

	function select() {
		state.updateState('value', value, true);
	}

	$: attrs = {
		'aria-disabled': disabled ? true : undefined,
		'aria-selected': $selected ? true : undefined,
		'data-disabled': disabled ? true : undefined,
		'data-selected': $selected ? true : undefined,
		'data-cmdk-item': '',
		'data-value': value,
		role: 'option',
		id
	};
</script>

{#if $render || isFirstRender}
	{#if asChild}
		<slot {action} {attrs} />
	{:else}
		<div {...attrs} use:action {...$$restProps}>
			<slot {action} {attrs} />
		</div>
	{/if}
{/if}


================================================
File: /src/lib/cmdk/components/CommandList.svelte
================================================
<script lang="ts">
	import { isHTMLElement } from '$lib/internal/index.js';
	import { getCtx, getState } from '../command.js';
	import type { ListProps } from '../types.js';

	const { ids } = getCtx();
	const state = getState();

	type $$Props = ListProps;

	export let el: $$Props['el'] = undefined;
	export let asChild: $$Props['asChild'] = false;

	function sizerAction(node: HTMLElement) {
		let animationFrame: number;
		const listEl = node.closest('[data-cmdk-list]');
		if (!isHTMLElement(listEl)) {
			return;
		}

		const observer = new ResizeObserver(() => {
			animationFrame = requestAnimationFrame(() => {
				const height = node.offsetHeight;
				listEl.style.setProperty('--cmdk-list-height', height.toFixed(1) + 'px');
			});
		});

		observer.observe(node);
		return {
			destroy() {
				cancelAnimationFrame(animationFrame);
				observer.unobserve(node);
			}
		};
	}

	const listAttrs = {
		'data-cmdk-list': '',
		role: 'listbox',
		'aria-label': 'Suggestions',
		id: ids.list,
		'aria-labelledby': ids.input
	};

	const sizerAttrs = {
		'data-cmdk-list-sizer': ''
	};

	const list = {
		attrs: listAttrs
	};

	const sizer = {
		attrs: sizerAttrs,
		action: sizerAction
	};
</script>

{#if asChild}
	{#key $state.search === ''}
		<slot {list} {sizer} />
	{/key}
{:else}
	<div {...listAttrs} bind:this={el} {...$$restProps}>
		<div {...sizerAttrs} use:sizerAction>
			{#key $state.search === ''}
				<slot />
			{/key}
		</div>
	</div>
{/if}


================================================
File: /src/lib/cmdk/components/CommandLoading.svelte
================================================
<script lang="ts">
	import type { LoadingProps } from '../types.js';

	type $$Props = LoadingProps;
	export let progress: $$Props['progress'] = 0;
	export let asChild: $$Props['asChild'] = false;

	$: attrs = {
		'data-cmdk-loading': '',
		role: 'progressbar',
		'aria-valuenow': progress,
		'aria-valuemin': 0,
		'aria-valuemax': 100,
		'aria-label': 'Loading...'
	};
</script>

{#if asChild}
	<slot {attrs} />
{:else}
	<div {...attrs} {...$$restProps}>
		<div aria-hidden>
			<slot {attrs} />
		</div>
	</div>
{/if}


================================================
File: /src/lib/cmdk/components/CommandSeparator.svelte
================================================
<script lang="ts">
	import { derived } from 'svelte/store';
	import { getState } from '../command.js';
	import type { SeparatorProps } from '../types.js';

	type $$Props = SeparatorProps;

	export let alwaysRender: $$Props['alwaysRender'] = false;
	export let asChild: $$Props['asChild'] = false;

	const state = getState();
	const render = derived(state, ($state) => !$state.search);

	const attrs = {
		'data-cmdk-separator': '',
		role: 'separator'
	};
</script>

{#if $render || alwaysRender}
	{#if asChild}
		<slot {attrs} />
	{:else}
		<div {...attrs} {...$$restProps}></div>
	{/if}
{/if}


================================================
File: /src/lib/internal/command-score.ts
================================================
// The scores are arranged so that a continuous match of characters will
// result in a total score of 1.
//
// The best case, this character is a match, and either this is the start
// of the string, or the previous character was also a match.
const SCORE_CONTINUE_MATCH = 1,
	// A new match at the start of a word scores better than a new match
	// elsewhere as it's more likely that the user will type the starts
	// of fragments.
	// NOTE: We score word jumps between spaces slightly higher than slashes, brackets
	// hyphens, etc.
	SCORE_SPACE_WORD_JUMP = 0.9,
	SCORE_NON_SPACE_WORD_JUMP = 0.8,
	// Any other match isn't ideal, but we include it for completeness.
	SCORE_CHARACTER_JUMP = 0.17,
	// If the user transposed two letters, it should be significantly penalized.
	//
	// i.e. "ouch" is more likely than "curtain" when "uc" is typed.
	SCORE_TRANSPOSITION = 0.1,
	// The goodness of a match should decay slightly with each missing
	// character.
	//
	// i.e. "bad" is more likely than "bard" when "bd" is typed.
	//
	// This will not change the order of suggestions based on SCORE_* until
	// 100 characters are inserted between matches.
	PENALTY_SKIPPED = 0.999,
	// The goodness of an exact-case match should be higher than a
	// case-insensitive match by a small amount.
	//
	// i.e. "HTML" is more likely than "haml" when "HM" is typed.
	//
	// This will not change the order of suggestions based on SCORE_* until
	// 1000 characters are inserted between matches.
	PENALTY_CASE_MISMATCH = 0.9999,
	// If the word has more characters than the user typed, it should
	// be penalised slightly.
	//
	// i.e. "html" is more likely than "html5" if I type "html".
	//
	// However, it may well be the case that there's a sensible secondary
	// ordering (like alphabetical) that it makes sense to rely on when
	// there are many prefix matches, so we don't make the penalty increase
	// with the number of tokens.
	PENALTY_NOT_COMPLETE = 0.99;

const IS_GAP_REGEXP = /[\\/_+.#"@[({&]/,
	COUNT_GAPS_REGEXP = /[\\/_+.#"@[({&]/g,
	IS_SPACE_REGEXP = /[\s-]/,
	COUNT_SPACE_REGEXP = /[\s-]/g;

function commandScoreInner(
	string: string,
	abbreviation: string,
	lowerString: string,
	lowerAbbreviation: string,
	stringIndex: number,
	abbreviationIndex: number,
	memoizedResults: { [key: string]: number }
) {
	if (abbreviationIndex === abbreviation.length) {
		if (stringIndex === string.length) {
			return SCORE_CONTINUE_MATCH;
		}
		return PENALTY_NOT_COMPLETE;
	}

	const memoizeKey = `${stringIndex},${abbreviationIndex}`;
	if (memoizedResults[memoizeKey] !== undefined) {
		return memoizedResults[memoizeKey];
	}

	const abbreviationChar = lowerAbbreviation.charAt(abbreviationIndex);
	let index = lowerString.indexOf(abbreviationChar, stringIndex);
	let highScore = 0;

	let score, transposedScore, wordBreaks, spaceBreaks;

	while (index >= 0) {
		score = commandScoreInner(
			string,
			abbreviation,
			lowerString,
			lowerAbbreviation,
			index + 1,
			abbreviationIndex + 1,
			memoizedResults
		);
		if (score > highScore) {
			if (index === stringIndex) {
				score *= SCORE_CONTINUE_MATCH;
			} else if (IS_GAP_REGEXP.test(string.charAt(index - 1))) {
				score *= SCORE_NON_SPACE_WORD_JUMP;
				wordBreaks = string.slice(stringIndex, index - 1).match(COUNT_GAPS_REGEXP);
				if (wordBreaks && stringIndex > 0) {
					score *= Math.pow(PENALTY_SKIPPED, wordBreaks.length);
				}
			} else if (IS_SPACE_REGEXP.test(string.charAt(index - 1))) {
				score *= SCORE_SPACE_WORD_JUMP;
				spaceBreaks = string.slice(stringIndex, index - 1).match(COUNT_SPACE_REGEXP);
				if (spaceBreaks && stringIndex > 0) {
					score *= Math.pow(PENALTY_SKIPPED, spaceBreaks.length);
				}
			} else {
				score *= SCORE_CHARACTER_JUMP;
				if (stringIndex > 0) {
					score *= Math.pow(PENALTY_SKIPPED, index - stringIndex);
				}
			}

			if (string.charAt(index) !== abbreviation.charAt(abbreviationIndex)) {
				score *= PENALTY_CASE_MISMATCH;
			}
		}

		if (
			(score < SCORE_TRANSPOSITION &&
				lowerString.charAt(index - 1) === lowerAbbreviation.charAt(abbreviationIndex + 1)) ||
			(lowerAbbreviation.charAt(abbreviationIndex + 1) ===
				lowerAbbreviation.charAt(abbreviationIndex) && // allow duplicate letters. Ref #7428
				lowerString.charAt(index - 1) !== lowerAbbreviation.charAt(abbreviationIndex))
		) {
			transposedScore = commandScoreInner(
				string,
				abbreviation,
				lowerString,
				lowerAbbreviation,
				index + 1,
				abbreviationIndex + 2,
				memoizedResults
			);

			if (transposedScore * SCORE_TRANSPOSITION > score) {
				score = transposedScore * SCORE_TRANSPOSITION;
			}
		}

		if (score > highScore) {
			highScore = score;
		}

		index = lowerString.indexOf(abbreviationChar, index + 1);
	}

	memoizedResults[memoizeKey] = highScore;
	return highScore;
}

function formatInput(string: string) {
	// convert all valid space characters to space so they match each other
	return string.toLowerCase().replace(COUNT_SPACE_REGEXP, ' ');
}

export function commandScore(string: string, abbreviation: string) {
	/* NOTE:
	 * in the original, we used to do the lower-casing on each recursive call, but this meant that toLowerCase()
	 * was the dominating cost in the algorithm, passing both is a little ugly, but considerably faster.
	 */
	return commandScoreInner(
		string,
		abbreviation,
		formatInput(string),
		formatInput(abbreviation),
		0,
		0,
		{}
	);
}


================================================
File: /src/lib/internal/index.ts
================================================
export * from './command-score.js';
export * from './helpers/index.js';
export * from './types.js';


================================================
File: /src/lib/internal/types.ts
================================================
import type { HTMLAttributes } from 'svelte/elements';
import type { TransitionConfig } from 'svelte/transition';

export type Expand<T> = T extends object
	? T extends infer O
		? { [K in keyof O]: O[K] }
		: never
	: T;

export type ValueOf<T> = T[keyof T];

export type HTMLDivAttributes = HTMLAttributes<HTMLDivElement>;

export type Prettify<T> = {
	[K in keyof T]: T[K];
	// eslint-disable-next-line @typescript-eslint/ban-types
} & {};

export type RenameProperties<T, NewNames extends Partial<Record<keyof T, string>>> = Expand<{
	[K in keyof T as K extends keyof NewNames
		? NewNames[K] extends PropertyKey
			? NewNames[K]
			: K
		: K]: T[K];
}>;

export type PrefixKeys<T, Prefix extends string> = Expand<{
	[K in keyof T as `${Prefix}${Capitalize<string & K>}`]: T[K];
}>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Transition = (node: Element, params?: any) => TransitionConfig;

export type Arrayable<T> = T | T[];


================================================
File: /src/lib/internal/helpers/callbacks.ts
================================================
/**
 * A callback function that takes an array of arguments of type `T` and returns `void`.
 * @template T The types of the arguments that the callback function takes.
 */
export type Callback<T extends unknown[] = unknown[]> = (...args: T) => void;

/**
 * Executes an array of callback functions with the same arguments.
 * @template T The types of the arguments that the callback functions take.
 * @param n array of callback functions to execute.
 * @returns A new function that executes all of the original callback functions with the same arguments.
 */
export function executeCallbacks<T extends unknown[]>(
	...callbacks: Array<Callback<T>>
): (...args: T) => void {
	return (...args) => {
		for (const callback of callbacks) {
			if (typeof callback === 'function') {
				callback(...args);
			}
		}
	};
}


================================================
File: /src/lib/internal/helpers/event.ts
================================================
import type { Arrayable } from '$lib/internal/index.js';

/**
 * A type alias for a general event listener function.
 *
 * @template E - The type of event to listen for
 * @param evt - The event object
 * @returns The return value of the event listener function
 */
export type GeneralEventListener<E = Event> = (evt: E) => unknown;

/**
 *  Overloaded function signatures for addEventListener
 */
export function addEventListener<E extends keyof HTMLElementEventMap>(
	target: Window,
	event: E,
	handler: (this: Window, ev: HTMLElementEventMap[E]) => unknown,
	options?: boolean | AddEventListenerOptions
): VoidFunction;

export function addEventListener<E extends keyof HTMLElementEventMap>(
	target: Document,
	event: E,
	handler: (this: Document, ev: HTMLElementEventMap[E]) => unknown,
	options?: boolean | AddEventListenerOptions
): VoidFunction;

export function addEventListener<E extends keyof HTMLElementEventMap>(
	target: EventTarget,
	event: E,
	handler: GeneralEventListener<HTMLElementEventMap[E]>,
	options?: boolean | AddEventListenerOptions
): VoidFunction;

/**
 * Adds an event listener to the specified target element(s) for the given event(s), and returns a function to remove it.
 * @param target The target element(s) to add the event listener to.
 * @param event The event(s) to listen for.
 * @param handler The function to be called when the event is triggered.
 * @param options An optional object that specifies characteristics about the event listener.
 * @returns A function that removes the event listener from the target element(s).
 */
export function addEventListener(
	target: Window | Document | EventTarget,
	event: Arrayable<string>,
	handler: EventListenerOrEventListenerObject,
	options?: boolean | AddEventListenerOptions
) {
	const events = Array.isArray(event) ? event : [event];

	// Add the event listener to each specified event for the target element(s).
	events.forEach((_event) => target.addEventListener(_event, handler, options));

	// Return a function that removes the event listener from the target element(s).
	return () => {
		events.forEach((_event) => target.removeEventListener(_event, handler, options));
	};
}


================================================
File: /src/lib/internal/helpers/id.ts
================================================
import { nanoid } from 'nanoid/non-secure';

export function generateId() {
	return nanoid(10);
}


================================================
File: /src/lib/internal/helpers/index.ts
================================================
export * from './is.js';
export * from './id.js';
export * from './kbd.js';
export * from './object.js';
export * from './store.js';
export * from './style.js';
export * from './event.js';
export * from './callbacks.js';


================================================
File: /src/lib/internal/helpers/is.ts
================================================
export const isBrowser = typeof document !== 'undefined';

export function isHTMLElement(element: unknown): element is HTMLElement {
	return element instanceof HTMLElement;
}

export function isHTMLInputElement(element: unknown): element is HTMLInputElement {
	return element instanceof HTMLInputElement;
}

export function isUndefined(value: unknown): value is undefined {
	return value === undefined;
}


================================================
File: /src/lib/internal/helpers/kbd.ts
================================================
export const kbd = {
	ALT: 'Alt',
	ARROW_DOWN: 'ArrowDown',
	ARROW_LEFT: 'ArrowLeft',
	ARROW_RIGHT: 'ArrowRight',
	ARROW_UP: 'ArrowUp',
	BACKSPACE: 'Backspace',
	CAPS_LOCK: 'CapsLock',
	CONTROL: 'Control',
	DELETE: 'Delete',
	END: 'End',
	ENTER: 'Enter',
	ESCAPE: 'Escape',
	F1: 'F1',
	F10: 'F10',
	F11: 'F11',
	F12: 'F12',
	F2: 'F2',
	F3: 'F3',
	F4: 'F4',
	F5: 'F5',
	F6: 'F6',
	F7: 'F7',
	F8: 'F8',
	F9: 'F9',
	HOME: 'Home',
	META: 'Meta',
	PAGE_DOWN: 'PageDown',
	PAGE_UP: 'PageUp',
	SHIFT: 'Shift',
	SPACE: ' ',
	TAB: 'Tab',
	CTRL: 'Control',
	ASTERISK: '*'
};


================================================
File: /src/lib/internal/helpers/object.ts
================================================
import type { ValueOf } from '$lib/internal/types.js';

export function omit<T extends Record<string, unknown>, K extends keyof T>(
	obj: T,
	...keys: K[]
): Omit<T, K> {
	const result = {} as Omit<T, K>;
	for (const key of Object.keys(obj)) {
		if (!keys.includes(key as unknown as K)) {
			result[key as keyof Omit<T, K>] = obj[key] as ValueOf<Omit<T, K>>;
		}
	}
	return result;
}

export function removeUndefined<T extends object>(obj: T): T {
	const result = {} as T;
	for (const key in obj) {
		const value = obj[key];
		if (value !== undefined) {
			result[key] = value;
		}
	}
	return result;
}


================================================
File: /src/lib/internal/helpers/sleep.ts
================================================
export function sleep(ms: number) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}


================================================
File: /src/lib/internal/helpers/store.ts
================================================
import {
	type Writable,
	type Stores,
	type StoresValues,
	type Readable,
	derived,
	writable
} from 'svelte/store';
import { onDestroy } from 'svelte';

/**
 * Given an object of properties, returns an object of writable stores
 * with the same properties and values.
 */
export function toWritableStores<T extends Record<string, unknown>>(
	properties: T
): { [K in keyof T]: Writable<T[K]> } {
	const result = {} as { [K in keyof T]: Writable<T[K]> };

	Object.keys(properties).forEach((key) => {
		const propertyKey = key as keyof T;
		const value = properties[propertyKey];
		result[propertyKey] = writable(value);
	});

	return result;
}

/**
 * A utility function that creates an effect from a set of stores and a function.
 * The effect is automatically cleaned up when the component is destroyed.
 *
 * @template S - The type of the stores object
 * @param stores - The stores object to derive from
 * @param fn - The function to run when the stores change
 * @returns A function that can be used to unsubscribe the effect
 */
export function effect<S extends Stores>(
	stores: S,
	fn: (values: StoresValues<S>) => (() => void) | void
): () => void {
	// Create a derived store that contains the stores object and an onUnsubscribe function
	const unsub = derivedWithUnsubscribe(stores, (stores, onUnsubscribe) => {
		return {
			stores,
			onUnsubscribe
		};
	}).subscribe(({ stores, onUnsubscribe }) => {
		const returned = fn(stores);
		// If the function returns a cleanup function, call it when the effect is unsubscribed
		if (returned) {
			onUnsubscribe(returned);
		}
	});

	// Automatically unsubscribe the effect when the component is destroyed
	onDestroy(unsub);
	return unsub;
}

/**
 * A utility function that creates a derived store that automatically
 * unsubscribes from its dependencies.
 *
 * @template S - The type of the stores object
 * @template T - The type of the derived store
 * @param stores - The stores object to derive from
 * @param fn - The function to derive the store from
 * @returns A derived store that automatically unsubscribes from its dependencies
 */
export function derivedWithUnsubscribe<S extends Stores, T>(
	stores: S,
	fn: (values: StoresValues<S>, onUnsubscribe: (cb: () => void) => void) => T
): Readable<T> {
	let unsubscribers: (() => void)[] = [];
	const onUnsubscribe = (cb: () => void) => {
		unsubscribers.push(cb);
	};

	const unsubscribe = () => {
		// Call all of the unsubscribe functions from the previous run of the function
		unsubscribers.forEach((fn) => fn());
		// Clear the list of unsubscribe functions
		unsubscribers = [];
	};

	const derivedStore = derived(stores, ($storeValues) => {
		unsubscribe();
		return fn($storeValues, onUnsubscribe);
	});

	onDestroy(unsubscribe);

	const subscribe: typeof derivedStore.subscribe = (...args) => {
		const unsub = derivedStore.subscribe(...args);
		return () => {
			unsub();
			unsubscribe();
		};
	};

	return {
		...derivedStore,
		subscribe
	};
}


================================================
File: /src/lib/internal/helpers/style.ts
================================================
export function styleToString(style: Record<string, number | string | undefined>): string {
	return Object.keys(style).reduce((str, key) => {
		if (style[key] === undefined) return str;
		return str + `${key}:${style[key]};`;
	}, '');
}

export const srOnlyStyles = {
	position: 'absolute',
	width: '1px',
	height: '1px',
	padding: '0',
	margin: '-1px',
	overflow: 'hidden',
	clip: 'rect(0, 0, 0, 0)',
	whiteSpace: 'nowrap',
	borderWidth: '0'
};


================================================
File: /src/routes/+layout.svelte
================================================
<script lang="ts">
	import { ModeWatcher } from 'mode-watcher';
	import '../styles/globals.postcss';
	import '../styles/app.postcss';

	const title = '⌘K-sv';
	const description = 'Fast, composable, unstyled command menu for Svelte';
	const siteUrl = 'https://www.cmdk-sv.com';
</script>

<svelte:head>
	<link rel="shortcut icon" href="/favicon.svg" />
	<meta name="twitter:card" content="summary_large_image" />
	<title>{description} - {title}</title>
	<meta name="description" content={description} />
	<meta name="keywords" content={description} />
	<meta name="author" content="huntabyte" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://cmdk-sv.com" />
	<meta name="twitter:title" content={title} />
	<meta name="twitter:description" content={description} />
	<meta name="twitter:image" content="https://cmdk-sv.com/og.png" />
	<meta name="twitter:image:alt" content={title} />
	<meta name="twitter:creator" content="huntabyte" />
	<meta property="og:title" content={title} />
	<meta property="og:type" content="article" />
	<meta property="og:image" content="https://cmdk-sv.com/og.png" />
	<meta property="og:image:alt" content={title} />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta property="og:description" content={description} />
	<meta property="og:site_name" content={title} />
	<meta property="og:locale" content="EN_US" />
	<meta property="og:url" content={siteUrl} />
</svelte:head>

<ModeWatcher />

<slot />


================================================
File: /src/routes/+layout.ts
================================================
import type { LayoutLoad } from './$types.js';
import packageJSON from '../../package.json';

export const load: LayoutLoad = async () => {
	return {
		version: packageJSON.version
	};
};


================================================
File: /src/routes/+page.svelte
================================================
<script lang="ts">
	import {
		VersionBadge,
		InstallButton,
		GitHubButton,
		CMDKWrapper,
		ThemeSwitcher,
		CodeBlock,
		Footer
	} from '$docs/components/index.js';
	import { RaycastCMDK, LinearCMDK, VercelCMDK, FramerCMDK } from '$docs/components/cmdk/index.js';
	import type { Themes } from '$docs/types.js';

	let theme: Themes = 'raycast';
</script>

<main class="main">
	<div class="content">
		<div class="meta">
			<div class="info">
				<VersionBadge />
				<h1>⌘K-sv</h1>
				<p>Fast, composable, unstyled command menu for Svelte.</p>
			</div>
			<div class="buttons">
				<InstallButton />
				<GitHubButton />
			</div>
		</div>
		<div style:height="475px">
			{#if theme === 'raycast'}
				<CMDKWrapper>
					<RaycastCMDK />
				</CMDKWrapper>
			{:else if theme === 'linear'}
				<CMDKWrapper>
					<LinearCMDK />
				</CMDKWrapper>
			{:else if theme === 'vercel'}
				<CMDKWrapper>
					<VercelCMDK />
				</CMDKWrapper>
			{:else if theme === 'framer'}
				<CMDKWrapper>
					<FramerCMDK />
				</CMDKWrapper>
			{/if}
		</div>
		<ThemeSwitcher bind:theme />

		<div aria-hidden class="line"></div>
		<CodeBlock />
	</div>
	<Footer />
</main>


================================================
File: /src/routes/sink/+page.svelte
================================================
<script lang="ts">
	import { Command } from '$lib/index.js';

	// prettier-ignore
	const ten_first_names = ["John", "Doe", "Jane", "Smith", "Michael", "Brown", "William", "Johnson", "David", "Williams"];
	// prettier-ignore
	const ten_middle_names = ["James", "Lee", "Robert", "Michael", "David", "Joseph", "Thomas", "Charles", "Christopher", "Daniel"];
	// prettier-ignore
	const ten_last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"];

	const names = ten_first_names
		.map((first) => {
			return ten_middle_names.map((middle) => {
				return ten_last_names.map((last) => {
					return `${first} ${middle} ${last}`;
				});
			});
		})
		.flat(2)
		.slice(500);
</script>

<div style:padding="16px">
	<Command.Root loop>
		<Command.Input placeholder="Search items..." />
		<Command.Empty>No item found.</Command.Empty>

		<Command.List
			class="h-[var(--cmdk-list-height)]"
			style="height: 200px; overflow-y: auto; max-width: 300px;"
		>
			{#each names as txt (txt)}
				<Command.Item value={txt}>{txt}</Command.Item>
			{/each}
		</Command.List>
	</Command.Root>
</div>


================================================
File: /src/styles/app.postcss
================================================
.main {
	width: 100vw;
	min-height: 100vh;
	position: relative;
	display: flex;
	justify-content: center;
	padding: 120px 24px 160px 24px;

	&:before {
		background: radial-gradient(circle, rgba(2, 0, 36, 0) 0, var(--gray1) 100%);
		position: absolute;
		content: '';
		z-index: 2;
		width: 100%;
		height: 100%;
		top: 0;
	}

	&:after {
		content: '';
		background-image: url('/grid.svg');
		position: absolute;
		z-index: -1;
		top: 0;
		width: 100%;
		height: 100%;
		opacity: 0.2;
		filter: invert(1);
	}

	@media (prefers-color-scheme: dark) {
		&:after {
			filter: unset;
		}
	}

	& h1 {
		font-size: 32px;
		color: var(--gray12);
		font-weight: 600;
		letter-spacing: -2px;
		line-height: 40px;
	}

	& p {
		color: var(--gray11);
		margin-top: 8px;
		font-size: 16px;
	}
}

.content {
	height: fit-content;
	position: relative;
	z-index: 3;
	width: 100%;
	max-width: 640px;

	&:after {
		background-image: radial-gradient(at 27% 37%, hsla(215, 98%, 61%, 1) 0px, transparent 50%),
			radial-gradient(at 97% 21%, hsla(256, 98%, 72%, 1) 0px, transparent 50%),
			radial-gradient(at 52% 99%, hsla(354, 98%, 61%, 1) 0px, transparent 50%),
			radial-gradient(at 10% 29%, hsla(133, 96%, 67%, 1) 0px, transparent 50%),
			radial-gradient(at 97% 96%, hsla(38, 60%, 74%, 1) 0px, transparent 50%),
			radial-gradient(at 33% 50%, hsla(222, 67%, 73%, 1) 0px, transparent 50%),
			radial-gradient(at 79% 53%, hsla(343, 68%, 79%, 1) 0px, transparent 50%);
		position: absolute;
		content: '';
		z-index: 2;
		width: 100%;
		height: 100%;
		filter: blur(100px) saturate(150%);
		z-index: -1;
		top: 80px;
		opacity: 0.2;
		transform: translateZ(0);
	}

	@media (prefers-color-scheme: dark) {
		&:after {
			opacity: 0.1;
		}
	}
}

.meta {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 48px;
	flex-wrap: wrap;
	gap: 16px;
}

.buttons {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 12px;
	transform: translateY(12px);
}

.githubButton,
.installButton,
.switcher button {
	height: 40px;
	color: var(--gray12);
	border-radius: 9999px;
	font-size: 14px;
	transition-duration: 150ms;
	transition-property: background, color, transform;
	transition-timing-function: ease-in;
	will-change: transform;
}

.githubButton {
	width: 200px;
	padding: 0 12px;
	display: inline-flex;
	align-items: center;
	gap: 8px;
	font-weight: 500;

	&:hover {
		background: var(--grayA3);
	}

	&:active {
		background: var(--grayA5);
		transform: scale(0.97);
	}

	&:focus-visible {
		outline: 0;
		outline: 2px solid var(--gray7);
	}
}

.installButton {
	background: var(--grayA3);
	display: flex;
	align-items: center;
	gap: 16px;
	padding: 0px 8px 0 16px;
	cursor: copy;
	font-weight: 500;

	&:hover {
		background: var(--grayA4);

		& span {
			background: var(--grayA5);

			& svg {
				color: var(--gray12);
			}
		}
	}

	&:focus-visible {
		outline: 0;
		outline: 2px solid var(--gray7);
		outline-offset: 2px;
	}

	&:active {
		background: var(--gray5);
		transform: scale(0.97);
	}

	& span {
		width: 28px;
		height: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-left: auto;
		background: var(--grayA3);
		border-radius: 9999px;
		transition: background 150ms ease;

		& svg {
			size: 16px;
			color: var(--gray11);
			transition: color 150ms ease;
		}
	}
}

.switcher {
	display: grid;
	grid-template-columns: repeat(4, 100px);
	align-items: center;
	justify-content: center;
	gap: 4px;
	margin-top: 48px;
	position: relative;

	& button {
		height: 32px;
		line-height: 32px;
		display: flex;
		align-items: center;
		margin: auto;
		gap: 8px;
		padding: 0 16px;
		border-radius: 9999px;
		color: var(--gray11);
		font-size: 14px;
		cursor: pointer;
		user-select: none;
		position: relative;
		text-transform: capitalize;

		&:hover {
			color: var(--gray12);
		}

		&:active {
			transform: scale(0.96);
		}

		&:focus-visible {
			outline: 0;
			outline: 2px solid var(--gray7);
		}

		& svg {
			width: 14px;
			height: 14px;
		}

		&[data-selected='true'] {
			color: var(--gray12);

			&:hover .activeTheme {
				background: var(--grayA6);
			}

			&:active {
				transform: scale(0.96);

				.activeTheme {
					background: var(--grayA7);
				}
			}
		}
	}

	.activeTheme {
		background: var(--grayA5);
		border-radius: 9999px;
		height: 32px;
		width: 100%;
		top: 0;
		position: absolute;
		left: 0;
	}

	.arrow {
		color: var(--gray11);
		user-select: none;
		position: absolute;
	}
}

.header {
	position: absolute;
	left: 0;
	top: -64px;
	gap: 8px;
	background: var(--gray3);
	padding: 4px;
	display: flex;
	align-items: center;
	border-radius: 9999px;

	& button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		padding: 4px;
		border-radius: 9999px;
		color: var(--gray11);

		& svg {
			width: 16px;
			height: 16px;
		}

		&[aria-selected] {
			background: #ffffff;
			color: var(--gray12);
			box-shadow:
				0px 2px 5px -2px rgb(0 0 0 / 15%),
				0 1px 3px -1px rgb(0 0 0 / 20%);
		}
	}
}

.versionBadge {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	color: var(--grayA11);
	background: var(--grayA3);
	padding: 4px 8px;
	border-radius: 4px;
	font-weight: 500;
	font-size: 14px;
	margin-bottom: 8px;

	@media (prefers-color-scheme: dark) {
		background: var(--grayA2);
	}
}

.codeBlock {
	margin-top: 72px;
	position: relative;
}

.footer {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
	width: fit-content;
	margin: 32px auto;
	bottom: 16px;
	color: var(--gray11);
	font-size: 13px;
	z-index: 10;
	position: absolute;
	bottom: 0;

	& a {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		color: var(--gray12);
		font-weight: 500;
		border-radius: 9999px;
		padding: 4px;
		margin: 0 -2px;
		transition: background 150ms ease;

		&:hover,
		&:focus-visible {
			background: var(--grayA4);
			outline: 0;
		}
	}

	& img {
		width: 20px;
		height: 20px;
		border: 1px solid var(--gray5);
		border-radius: 9999px;
	}
}

.line {
	height: 20px;
	width: 180px;
	margin: 64px auto;
	background-image: url('/line.svg');
	filter: invert(1);
	mask-image: linear-gradient(90deg, transparent, #fff 4rem, #fff calc(100% - 4rem), transparent);

	@media (prefers-color-scheme: dark) {
		filter: unset;
	}
}

.line2 {
	height: 1px;
	width: 300px;
	background: var(--gray7);
	position: absolute;
	top: 0;
	mask-image: linear-gradient(90deg, transparent, #fff 4rem, #fff calc(100% - 4rem), transparent);
}

.line3 {
	height: 300px;
	width: calc(100% + 32px);
	position: absolute;
	top: -16px;
	left: -16px;

	border-radius: 16px 16px 0 0;
	--size: 1px;
	--gradient: linear-gradient(to top, var(--gray1), var(--gray7));

	&:before {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: inherit;
		padding: var(--size);
		background: linear-gradient(to top, var(--gray1), var(--gray7));
		mask:
			linear-gradient(black, black) content-box,
			linear-gradient(black, black);
		mask-composite: exclude;
		transform: translateZ(0);
	}

	@media (prefers-color-scheme: dark) {
		&:before {
			mask: none;
			mask-composite: none;
			opacity: 0.2;
			backdrop-filter: blur(20px);
		}
	}
}

.raunoSignature,
.pacoSignature {
	position: absolute;
	height: fit-content;
	color: var(--gray11);
	pointer-events: none;
}

.raunoSignature {
	width: 120px;
	stroke-dashoffset: 1;
	stroke-dasharray: 1;
	right: -48px;
}

.pacoSignature {
	width: 120px;
	stroke-dashoffset: 1;
	stroke-dasharray: 1;
	left: -8px;
}

.footerText {
	display: flex;
	display: flex;
	align-items: center;
	gap: 4px;
}

.footer[data-animate='true'] {
	.raunoSignature path {
		animation: drawRaunoSignature 1.5s ease forwards 0.5s;
	}

	.pacoSignature path {
		animation: drawPacoSignature 0.8s linear forwards 0.5s;
	}

	.footerText {
		animation: showFooter 1s linear forwards 3s;
	}
}

@keyframes drawPacoSignature {
	100% {
		stroke-dashoffset: 0;
	}
}

@keyframes drawRaunoSignature {
	100% {
		stroke-dashoffset: 0;
	}
}

@keyframes showFooter {
	100% {
		opacity: 1;
	}
}

@media (max-width: 640px) {
	.main {
		padding-top: 24px;
		padding-bottom: 120px;
	}

	.switcher {
		grid-template-columns: repeat(2, 100px);
		gap: 16px;

		.arrow {
			display: none;
		}
	}
}


================================================
File: /src/styles/code.postcss
================================================
.root {
	color: var(--gray12);
	border-radius: 12px;
	padding: 16px;
	backdrop-filter: blur(10px);
	border: 1px solid var(--gray6);
	position: relative;
	line-height: 16px;
	background: var(--lowContrast);
	white-space: pre-wrap;
	box-shadow: rgb(0 0 0 / 10%) 0px 5px 30px -5px;
	display: flex;
	flex-direction: column;

	@media (prefers-color-scheme: dark) {
		background: var(--grayA2);
	}

	& button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		background: var(--grayA3);
		border-radius: 8px;
		position: absolute;
		top: 12px;
		right: 12px;
		color: var(--gray11);
		cursor: copy;
		transition:
			color 150ms ease,
			background 150ms ease,
			transform 150ms ease;

		&:hover {
			color: var(--gray12);
			background: var(--grayA4);
		}

		&:active {
			color: var(--gray12);
			background: var(--grayA5);
			transform: scale(0.96);
		}
	}

	.token {
		padding-right: -1.25rem;
	}
}

@media (prefers-color-scheme: dark) {
	.shine {
		background: linear-gradient(
			90deg,
			rgba(56, 189, 248, 0),
			var(--gray5) 20%,
			var(--gray9) 67.19%,
			rgba(236, 72, 153, 0)
		);
		height: 1px;
		position: absolute;
		top: -1px;
		width: 97%;
		z-index: -1;
	}
}

@media (max-width: 640px) {
	.root {
		:global(.token-line) {
			font-size: 11px !important;
		}
	}
}

/**
 * a11y-dark theme for JavaScript, CSS, and HTML
 * Based on the okaidia theme: https://github.com/PrismJS/prism/blob/gh-pages/themes/prism-okaidia.css
 * @author ericwbailey
 */

/* Not Mine */

.token.class-name,
.token.function,
.token.tag {
	color: var(--gray12);
}

.token.selector,
.token.attr-name,
.token.string,
.token.char,
.token.builtin,
.token.inserted {
	color: var(--gray12);
}

.token.important,
.token.bold {
	font-weight: bold;
}

.token.italic {
	font-style: italic;
}

.token.entity {
	cursor: help;
}

/* Mine */
.token.comment {
	color: var(--gray9);
}

.token.atrule,
.token.keyword,
.token.attr-name,
.token.selector {
	color: var(--gray10);
}

.token.punctuation,
.token.operator {
	color: var(--gray9);
}


================================================
File: /src/styles/globals.postcss
================================================
@font-face {
	font-family: 'Inter';
	font-style: normal;
	font-weight: 100 900;
	font-display: optional;
	src: url(/inter-var-latin.woff2) format('woff2');
	unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F,
		U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

::selection {
	background: #eb5027;
	color: white;
}

html,
body {
	padding: 0;
	margin: 0;
	font-family: var(--font-sans);
}

body {
	background: var(--app-bg);
	overflow-x: hidden;
}

button {
	background: none;
	font-family: var(--font-sans);
	padding: 0;
	border: 0;
}

h1,
h2,
h3,
h4,
h5,
h6,
p {
	margin: 0;
}

a {
	color: inherit;
	text-decoration: none;
}

*,
*::after,
*::before {
	box-sizing: border-box;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}

:root {
	--font-sans: 'Inter', --apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu,
		Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
	--app-bg: var(--gray1);
	--cmdk-shadow: 0 16px 70px rgb(0 0 0 / 20%);

	--lowContrast: #ffffff;
	--highContrast: #000000;

	--gray1: hsl(0, 0%, 99%);
	--gray2: hsl(0, 0%, 97.3%);
	--gray3: hsl(0, 0%, 95.1%);
	--gray4: hsl(0, 0%, 93%);
	--gray5: hsl(0, 0%, 90.9%);
	--gray6: hsl(0, 0%, 88.7%);
	--gray7: hsl(0, 0%, 85.8%);
	--gray8: hsl(0, 0%, 78%);
	--gray9: hsl(0, 0%, 56.1%);
	--gray10: hsl(0, 0%, 52.3%);
	--gray11: hsl(0, 0%, 43.5%);
	--gray12: hsl(0, 0%, 9%);

	--grayA1: hsla(0, 0%, 0%, 0.012);
	--grayA2: hsla(0, 0%, 0%, 0.027);
	--grayA3: hsla(0, 0%, 0%, 0.047);
	--grayA4: hsla(0, 0%, 0%, 0.071);
	--grayA5: hsla(0, 0%, 0%, 0.09);
	--grayA6: hsla(0, 0%, 0%, 0.114);
	--grayA7: hsla(0, 0%, 0%, 0.141);
	--grayA8: hsla(0, 0%, 0%, 0.22);
	--grayA9: hsla(0, 0%, 0%, 0.439);
	--grayA10: hsla(0, 0%, 0%, 0.478);
	--grayA11: hsla(0, 0%, 0%, 0.565);
	--grayA12: hsla(0, 0%, 0%, 0.91);

	--blue1: hsl(206, 100%, 99.2%);
	--blue2: hsl(210, 100%, 98%);
	--blue3: hsl(209, 100%, 96.5%);
	--blue4: hsl(210, 98.8%, 94%);
	--blue5: hsl(209, 95%, 90.1%);
	--blue6: hsl(209, 81.2%, 84.5%);
	--blue7: hsl(208, 77.5%, 76.9%);
	--blue8: hsl(206, 81.9%, 65.3%);
	--blue9: hsl(206, 100%, 50%);
	--blue10: hsl(208, 100%, 47.3%);
	--blue11: hsl(211, 100%, 43.2%);
	--blue12: hsl(211, 100%, 15%);
}

.dark {
	--app-bg: var(--gray1);

	--lowContrast: #000000;
	--highContrast: #ffffff;

	--gray1: hsl(0, 0%, 8.5%);
	--gray2: hsl(0, 0%, 11%);
	--gray3: hsl(0, 0%, 13.6%);
	--gray4: hsl(0, 0%, 15.8%);
	--gray5: hsl(0, 0%, 17.9%);
	--gray6: hsl(0, 0%, 20.5%);
	--gray7: hsl(0, 0%, 24.3%);
	--gray8: hsl(0, 0%, 31.2%);
	--gray9: hsl(0, 0%, 43.9%);
	--gray10: hsl(0, 0%, 49.4%);
	--gray11: hsl(0, 0%, 62.8%);
	--gray12: hsl(0, 0%, 93%);

	--grayA1: hsla(0, 0%, 100%, 0);
	--grayA2: hsla(0, 0%, 100%, 0.026);
	--grayA3: hsla(0, 0%, 100%, 0.056);
	--grayA4: hsla(0, 0%, 100%, 0.077);
	--grayA5: hsla(0, 0%, 100%, 0.103);
	--grayA6: hsla(0, 0%, 100%, 0.129);
	--grayA7: hsla(0, 0%, 100%, 0.172);
	--grayA8: hsla(0, 0%, 100%, 0.249);
	--grayA9: hsla(0, 0%, 100%, 0.386);
	--grayA10: hsla(0, 0%, 100%, 0.446);
	--grayA11: hsla(0, 0%, 100%, 0.592);
	--grayA12: hsla(0, 0%, 100%, 0.923);

	--blue1: hsl(212, 35%, 9.2%);
	--blue2: hsl(216, 50%, 11.8%);
	--blue3: hsl(214, 59.4%, 15.3%);
	--blue4: hsl(214, 65.8%, 17.9%);
	--blue5: hsl(213, 71.2%, 20.2%);
	--blue6: hsl(212, 77.4%, 23.1%);
	--blue7: hsl(211, 85.1%, 27.4%);
	--blue8: hsl(211, 89.7%, 34.1%);
	--blue9: hsl(206, 100%, 50%);
	--blue10: hsl(209, 100%, 60.6%);
	--blue11: hsl(210, 100%, 66.1%);
	--blue12: hsl(206, 98%, 95.8%);
}


================================================
File: /src/styles/icons.postcss
================================================
.blurLogo {
	display: flex;
	align-items: center;
	justify-content: center;
	position: relative;
	border-radius: 4px;
	overflow: hidden;
	box-shadow: inset 0 0 1px 1px rgba(0, 0, 0, 0.015);

	.bg {
		display: flex;
		align-items: center;
		justify-content: center;
		position: absolute;
		z-index: 1;
		pointer-events: none;
		user-select: none;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		transform: scale(1.5) translateZ(0);
		filter: blur(12px) opacity(0.4) saturate(100%);
		transition: filter 150ms ease;
	}

	.inner {
		display: flex;
		align-items: center;
		justify-content: center;
		object-fit: cover;
		width: 100%;
		height: 100%;
		user-select: none;
		pointer-events: none;
		border-radius: inherit;
		z-index: 2;

		& svg {
			width: 14px;
			height: 14px;
			filter: drop-shadow(0 4px 4px rgba(0, 0, 0, 0.16));
			transition: filter 150ms ease;
		}
	}
}


================================================
File: /src/styles/cmdk/framer.postcss
================================================
.framer {
	[data-cmdk-root] {
		max-width: 640px;
		width: 100%;
		padding: 8px;
		background: #ffffff;
		border-radius: 16px;
		overflow: hidden;
		font-family: var(--font-sans);
		border: 1px solid var(--gray6);
		box-shadow: var(--cmdk-shadow);

		.dark & {
			background: var(--gray2);
		}
	}

	[data-cmdk-framer-header] {
		display: flex;
		align-items: center;
		gap: 8px;
		height: 48px;
		padding: 0 8px;
		border-bottom: 1px solid var(--gray5);
		margin-bottom: 12px;
		padding-bottom: 8px;

		& svg {
			width: 20px;
			height: 20px;
			color: var(--gray9);
			transform: translateY(1px);
		}
	}

	[data-cmdk-input] {
		font-family: var(--font-sans);
		border: none;
		width: 100%;
		font-size: 16px;
		outline: none;
		background: var(--bg);
		color: var(--gray12);

		&::placeholder {
			color: var(--gray9);
		}
	}

	[data-cmdk-item] {
		content-visibility: auto;

		cursor: pointer;
		border-radius: 12px;
		font-size: 14px;
		display: flex;
		align-items: center;
		gap: 12px;
		color: var(--gray12);
		padding: 8px 8px;
		margin-right: 8px;
		font-weight: 500;
		transition: all 150ms ease;
		transition-property: none;

		&[data-selected='true'] {
			background: var(--blue9);
			color: #ffffff;

			[data-cmdk-framer-item-subtitle] {
				color: #ffffff;
			}
		}

		&[data-disabled='true'] {
			color: var(--gray8);
			cursor: not-allowed;
		}

		& + [data-cmdk-item] {
			margin-top: 4px;
		}

		& svg {
			width: 16px;
			height: 16px;
			color: #ffffff;
		}
	}

	[data-cmdk-framer-icon-wrapper] {
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 32px;
		height: 32px;
		background: orange;
		border-radius: 8px;
	}

	[data-cmdk-framer-item-meta] {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	[data-cmdk-framer-item-subtitle] {
		font-size: 12px;
		font-weight: 400;
		color: var(--gray11);
	}

	[data-cmdk-framer-items] {
		min-height: 308px;
		display: flex;
	}

	[data-cmdk-framer-left] {
		width: 40%;
	}

	[data-cmdk-framer-separator] {
		width: 1px;
		border: 0;
		margin-right: 8px;
		background: var(--gray6);
	}

	[data-cmdk-framer-right] {
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		margin-left: 8px;
		width: 60%;

		& button {
			width: 120px;
			height: 40px;
			background: var(--blue9);
			border-radius: 6px;
			font-weight: 500;
			color: white;
			font-size: 14px;
		}

		& input[type='text'] {
			height: 40px;
			width: 160px;
			border: 1px solid var(--gray6);
			background: #ffffff;
			border-radius: 6px;
			padding: 0 8px;
			font-size: 14px;
			font-family: var(--font-sans);
			box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.08);

			&::placeholder {
				color: var(--gray9);
			}
		}

		[data-cmdk-framer-radio] {
			display: flex;
			align-items: center;
			gap: 4px;
			color: var(--gray12);
			font-weight: 500;
			font-size: 14px;
			accent-color: var(--blue9);

			& input {
				width: 20px;
				height: 20px;
			}
		}

		& img {
			width: 40px;
			height: 40px;
			border-radius: 9999px;
			border: 1px solid var(--gray6);
		}

		[data-cmdk-framer-container] {
			width: 100px;
			height: 100px;
			background: var(--blue9);
			border-radius: 16px;
		}

		[data-cmdk-framer-badge] {
			background: var(--blue3);
			padding: 0 8px;
			height: 28px;
			font-size: 14px;
			line-height: 28px;
			color: var(--blue11);
			border-radius: 9999px;
			font-weight: 500;
		}

		[data-cmdk-framer-slider] {
			height: 20px;
			width: 200px;
			background: linear-gradient(90deg, var(--blue9) 40%, var(--gray3) 0%);
			border-radius: 9999px;

			& div {
				width: 20px;
				height: 20px;
				background: #ffffff;
				border-radius: 9999px;
				box-shadow: 0 1px 3px -1px rgba(0, 0, 0, 0.32);
				transform: translateX(70px);
			}
		}
	}

	[data-cmdk-list] {
		overflow: auto;
	}

	[data-cmdk-separator] {
		height: 1px;
		width: 100%;
		background: var(--gray5);
		margin: 4px 0;
	}

	[data-cmdk-group-heading] {
		user-select: none;
		font-size: 12px;
		color: var(--gray11);
		padding: 0 8px;
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}

	[data-cmdk-empty] {
		font-size: 14px;
		padding: 32px;
		white-space: pre-wrap;
		color: var(--gray11);
	}
}

@media (max-width: 640px) {
	.framer {
		[data-cmdk-framer-icon-wrapper] {
		}

		[data-cmdk-framer-item-subtitle] {
			display: none;
		}
	}
}

@media (prefers-color-scheme: dark) {
	.framer {
		[data-cmdk-framer-right] {
			& input[type='text'] {
				background: var(--gray3);
			}
		}
	}
}


================================================
File: /src/styles/cmdk/linear.postcss
================================================
.linear {
	[data-cmdk-root] {
		max-width: 640px;
		width: 100%;
		background: #ffffff;
		border-radius: 8px;
		overflow: hidden;
		padding: 0;
		font-family: var(--font-sans);
		box-shadow: var(--cmdk-shadow);

		.dark & {
			background: linear-gradient(136.61deg, rgb(39, 40, 43) 13.72%, rgb(45, 46, 49) 74.3%);
		}
	}

	[data-cmdk-linear-badge] {
		height: 24px;
		padding: 0 8px;
		font-size: 12px;
		color: var(--gray11);
		background: var(--gray3);
		border-radius: 4px;
		width: fit-content;
		display: flex;
		align-items: center;
		margin: 16px 16px 0;
	}

	[data-cmdk-linear-shortcuts] {
		display: flex;
		margin-left: auto;
		gap: 8px;

		& kbd {
			font-family: var(--font-sans);
			font-size: 13px;
			color: var(--gray11);
		}
	}

	[data-cmdk-input] {
		font-family: var(--font-sans);
		border: none;
		width: 100%;
		font-size: 18px;
		padding: 20px;
		outline: none;
		background: var(--bg);
		color: var(--gray12);
		border-bottom: 1px solid var(--gray6);
		border-radius: 0;
		caret-color: #6e5ed2;
		margin: 0;

		&::placeholder {
			color: var(--gray9);
		}
	}

	[data-cmdk-item] {
		content-visibility: auto;

		cursor: pointer;
		height: 48px;
		font-size: 14px;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 0 16px;
		color: var(--gray12);
		user-select: none;
		will-change: background, color;
		transition: all 150ms ease;
		transition-property: none;
		position: relative;

		&[data-selected='true'] {
			background: var(--gray3);

			svg {
				color: var(--gray12);
			}

			&:after {
				content: '';
				position: absolute;
				left: 0;
				z-index: 123;
				width: 3px;
				height: 100%;
				background: #5f6ad2;
			}
		}

		&[data-disabled='true'] {
			color: var(--gray8);
			cursor: not-allowed;
		}

		&:active {
			transition-property: background;
			background: var(--gray4);
		}

		& + [data-cmdk-item] {
			margin-top: 4px;
		}

		& svg {
			width: 16px;
			height: 16px;
			color: var(--gray10);
		}
	}

	[data-cmdk-list] {
		height: min(300px, var(--cmdk-list-height));
		max-height: 400px;
		overflow: auto;
		overscroll-behavior: contain;
		transition: 100ms ease;
		transition-property: height;
	}

	[data-cmdk-group-heading] {
		user-select: none;
		font-size: 12px;
		color: var(--gray11);
		padding: 0 8px;
		display: flex;
		align-items: center;
	}

	[data-cmdk-empty] {
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 64px;
		white-space: pre-wrap;
		color: var(--gray11);
	}
}


================================================
File: /src/styles/cmdk/raycast.postcss
================================================
.raycast {
	[data-cmdk-root] {
		max-width: 640px;
		width: 100%;
		background: var(--gray1);
		border-radius: 12px;
		padding: 8px 0;
		font-family: var(--font-sans);
		box-shadow: var(--cmdk-shadow);
		border: 1px solid var(--gray6);
		position: relative;

		.dark & {
			background: var(--gray2);
			border: 0;

			&:after {
				content: '';
				background: linear-gradient(
					to right,
					var(--gray6) 20%,
					var(--gray6) 40%,
					var(--gray10) 50%,
					var(--gray10) 55%,
					var(--gray6) 70%,
					var(--gray6) 100%
				);
				z-index: -1;
				position: absolute;
				border-radius: 12px;
				top: -1px;
				left: -1px;
				width: calc(100% + 2px);
				height: calc(100% + 2px);
				animation: shine 3s ease forwards 0.1s;
				background-size: 200% auto;
			}

			&:before {
				content: '';
				z-index: -1;
				position: absolute;
				border-radius: 12px;
				top: -1px;
				left: -1px;
				width: calc(100% + 2px);
				height: calc(100% + 2px);
				box-shadow: 0 0 0 1px transparent;
				animation: border 1s linear forwards 0.5s;
			}
		}

		& kbd {
			font-family: var(--font-sans);
			background: var(--gray3);
			color: var(--gray11);
			height: 20px;
			width: 20px;
			border-radius: 4px;
			padding: 0 4px;
			display: flex;
			align-items: center;
			justify-content: center;

			&:first-of-type {
				margin-left: 8px;
			}
		}
	}

	[data-cmdk-input] {
		font-family: var(--font-sans);
		border: none;
		width: 100%;
		font-size: 15px;
		padding: 8px 16px;
		outline: none;
		background: var(--bg);
		color: var(--gray12);

		&::placeholder {
			color: var(--gray9);
		}
	}

	[data-cmdk-raycast-top-shine] {
		.dark & {
			background: linear-gradient(
				90deg,
				rgba(56, 189, 248, 0),
				var(--gray5) 20%,
				var(--gray9) 67.19%,
				rgba(236, 72, 153, 0)
			);
			height: 1px;
			position: absolute;
			top: -1px;
			width: 100%;
			z-index: -1;
			opacity: 0;
			animation: showTopShine 0.1s ease forwards 0.2s;
		}
	}

	[data-cmdk-raycast-loader] {
		--loader-color: var(--gray9);
		border: 0;
		width: 100%;
		width: 100%;
		left: 0;
		height: 1px;
		background: var(--gray6);
		position: relative;
		overflow: visible;
		display: block;
		margin-top: 12px;
		margin-bottom: 12px;

		&:after {
			content: '';
			width: 50%;
			height: 1px;
			position: absolute;
			background: linear-gradient(90deg, transparent 0%, var(--loader-color) 50%, transparent 100%);
			top: -1px;
			opacity: 0;
			animation-duration: 1.5s;
			animation-delay: 1s;
			animation-timing-function: ease;
			animation-name: loading;
		}
	}

	[data-cmdk-item] {
		content-visibility: auto;

		cursor: pointer;
		height: 40px;
		border-radius: 8px;
		font-size: 14px;
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 0 8px;
		color: var(--gray12);
		user-select: none;
		will-change: background, color;
		transition: all 150ms ease;
		transition-property: none;

		&[data-selected='true'] {
			background: var(--gray4);
			color: var(--gray12);
		}

		&[data-disabled='true'] {
			color: var(--gray8);
			cursor: not-allowed;
		}

		&:active {
			transition-property: background;
			background: var(--gray4);
		}

		&:first-child {
			margin-top: 8px;
		}

		& + [data-cmdk-item] {
			margin-top: 4px;
		}

		& svg {
			width: 18px;
			height: 18px;
		}
	}

	[data-cmdk-raycast-meta] {
		margin-left: auto;
		color: var(--gray11);
		font-size: 13px;
	}

	[data-cmdk-list] {
		padding: 0 8px;
		height: 393px;
		overflow: auto;
		overscroll-behavior: contain;
		scroll-padding-block-end: 40px;
		transition: 100ms ease;
		transition-property: height;
		padding-bottom: 40px;
	}

	[data-cmdk-raycast-open-trigger],
	[data-cmdk-raycast-subcommand-trigger] {
		color: var(--gray11);
		padding: 0px 4px 0px 8px;
		border-radius: 6px;
		font-weight: 500;
		font-size: 12px;
		height: 28px;
		letter-spacing: -0.25px;
	}

	[data-cmdk-raycast-clipboard-icon],
	[data-cmdk-raycast-hammer-icon] {
		width: 20px;
		height: 20px;
		border-radius: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #ffffff;

		& svg {
			width: 14px;
			height: 14px;
		}
	}

	[data-cmdk-raycast-clipboard-icon] {
		background: linear-gradient(to bottom, #f55354, #eb4646);
	}

	[data-cmdk-raycast-hammer-icon] {
		background: linear-gradient(to bottom, #6cb9a3, #2c6459);
	}

	[data-cmdk-raycast-open-trigger] {
		display: flex;
		align-items: center;
		color: var(--gray12);
	}

	[data-cmdk-raycast-subcommand-trigger] {
		display: flex;
		align-items: center;
		gap: 4px;
		right: 8px;
		bottom: 8px;

		& svg {
			width: 14px;
			height: 14px;
		}

		& hr {
			height: 100%;
			background: var(--gray6);
			border: 0;
			width: 1px;
		}

		&[aria-expanded='true'],
		&:hover {
			background: var(--gray4);

			& kbd {
				background: var(--gray7);
			}
		}
	}

	[data-cmdk-separator] {
		height: 1px;
		width: 100%;
		background: var(--gray5);
		margin: 4px 0;
	}

	& *:not([hidden]) + [data-cmdk-group] {
		margin-top: 8px;
	}

	[data-cmdk-group-heading] {
		user-select: none;
		font-size: 12px;
		color: var(--gray11);
		padding: 0 8px;
		display: flex;
		align-items: center;
	}

	[data-cmdk-raycast-footer] {
		display: flex;
		height: 40px;
		align-items: center;
		width: 100%;
		position: absolute;
		background: var(--gray1);
		bottom: 0;
		padding: 8px;
		border-top: 1px solid var(--gray6);
		border-radius: 0 0 12px 12px;
		z-index: 2;

		& svg {
			width: 20px;
			height: 20px;
			filter: grayscale(1);
			margin-right: auto;
		}

		& hr {
			height: 12px;
			width: 1px;
			border: 0;
			background: var(--gray6);
			margin: 0 4px 0px 12px;
		}
	}

	[data-cmdk-dialog] {
		z-index: var(--layer-portal);
		position: fixed;
		left: 50%;
		top: var(--page-top);
		transform: translateX(-50%);

		[data-cmdk] {
			width: 640px;
			transform-origin: center center;
			animation: dialogIn var(--transition-fast) forwards;
		}

		&[data-state='closed'] [data-cmdk] {
			animation: dialogOut var(--transition-fast) forwards;
		}
	}

	[data-cmdk-empty] {
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 64px;
		white-space: pre-wrap;
		color: var(--gray11);
	}
}

@keyframes loading {
	0% {
		opacity: 0;
		transform: translateX(0);
	}

	50% {
		opacity: 1;
		transform: translateX(100%);
	}

	100% {
		opacity: 0;
		transform: translateX(0);
	}
}

@keyframes shine {
	to {
		background-position: 200% center;
		opacity: 0;
	}
}

@keyframes border {
	to {
		box-shadow: 0 0 0 1px var(--gray6);
	}
}

@keyframes showTopShine {
	to {
		opacity: 1;
	}
}

.raycast-submenu {
	z-index: 50;

	[data-cmdk-root] {
		display: flex;
		flex-direction: column;
		width: 320px;
		border: 1px solid var(--gray6);
		background: var(--gray2);
		border-radius: 8px;
	}

	[data-cmdk-list] {
		padding: 8px;
		overflow: auto;
		overscroll-behavior: contain;
		transition: 100ms ease;
		transition-property: height;
	}

	[data-cmdk-item] {
		height: 40px;

		cursor: pointer;
		height: 40px;
		border-radius: 8px;
		font-size: 13px;
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 0 8px;
		color: var(--gray12);
		user-select: none;
		will-change: background, color;
		transition: all 150ms ease;
		transition-property: none;

		&[aria-selected='true'] {
			background: var(--gray5);
			color: var(--gray12);

			[data-cmdk-raycast-submenu-shortcuts] kbd {
				background: var(--gray7);
			}
		}

		&[aria-disabled='true'] {
			color: var(--gray8);
			cursor: not-allowed;
		}

		& svg {
			width: 16px;
			height: 16px;
		}

		[data-cmdk-raycast-submenu-shortcuts] {
			display: flex;
			margin-left: auto;
			gap: 2px;

			& kbd {
				font-family: var(--font-sans);
				background: var(--gray5);
				color: var(--gray11);
				height: 20px;
				width: 20px;
				border-radius: 4px;
				padding: 0 4px;
				font-size: 12px;
				display: flex;
				align-items: center;
				justify-content: center;

				&:first-of-type {
					margin-left: 8px;
				}
			}
		}
	}

	[data-cmdk-group-heading] {
		text-transform: capitalize;
		font-size: 12px;
		color: var(--gray11);
		font-weight: 500;
		margin-bottom: 8px;
		margin-top: 8px;
		margin-left: 4px;
	}

	[data-cmdk-input] {
		padding: 12px;
		font-family: var(--font-sans);
		border: 0;
		border-top: 1px solid var(--gray6);
		font-size: 13px;
		background: transparent;
		margin-top: auto;
		width: 100%;
		outline: 0;
		border-radius: 0;
	}

	animation-duration: 0.2s;
	animation-timing-function: ease;
	animation-fill-mode: forwards;
	transform-origin: var(--radix-popover-content-transform-origin);

	&[data-state='open'] {
		animation-name: slideIn;
	}

	&[data-state='closed'] {
		animation-name: slideOut;
	}

	[data-cmdk-empty] {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 64px;
		white-space: pre-wrap;
		font-size: 14px;
		color: var(--gray11);
	}
}

@keyframes slideIn {
	0% {
		opacity: 0;
		transform: scale(0.96);
	}

	100% {
		opacity: 1;
		transform: scale(1);
	}
}

@keyframes slideOut {
	0% {
		opacity: 1;
		transform: scale(1);
	}

	100% {
		opacity: 0;
		transform: scale(0.96);
	}
}

@media (max-width: 640px) {
	.raycast {
		[data-cmdk-input] {
			font-size: 16px;
		}
	}
}

@media (prefers-color-scheme: dark) {
	.raycast {
		[data-cmdk-raycast-footer] {
			background: var(--gray2);
		}
	}
}


================================================
File: /src/styles/cmdk/vercel.postcss
================================================
.vercel {
	[data-cmdk-root] {
		max-width: 640px;
		width: 100%;
		padding: 8px;
		background: #ffffff;
		border-radius: 12px;
		overflow: hidden;
		font-family: var(--font-sans);
		border: 1px solid var(--gray6);
		box-shadow: var(--cmdk-shadow);
		transition: transform 100ms ease;

		.dark & {
			background: rgba(22, 22, 22, 0.7);
		}
	}

	[data-cmdk-input] {
		font-family: var(--font-sans);
		border: none;
		width: 100%;
		font-size: 17px;
		padding: 8px 8px 16px 8px;
		outline: none;
		background: var(--bg);
		color: var(--gray12);
		border-bottom: 1px solid var(--gray6);
		margin-bottom: 16px;
		border-radius: 0;

		&::placeholder {
			color: var(--gray9);
		}
	}

	[data-cmdk-vercel-badge] {
		height: 20px;
		background: var(--grayA3);
		display: inline-flex;
		align-items: center;
		padding: 0 8px;
		font-size: 12px;
		color: var(--grayA11);
		border-radius: 4px;
		margin: 4px 0 4px 4px;
		user-select: none;
		text-transform: capitalize;
		font-weight: 500;
	}

	[data-cmdk-item] {
		content-visibility: auto;

		cursor: pointer;
		height: 48px;
		border-radius: 8px;
		font-size: 14px;
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 0 16px;
		color: var(--gray11);
		user-select: none;
		will-change: background, color;
		transition: all 150ms ease;
		transition-property: none;

		&[data-selected='true'] {
			background: var(--grayA3);
			color: var(--gray12);
		}

		&[data-disabled='true'] {
			color: var(--gray8);
			cursor: not-allowed;
		}

		&:active {
			transition-property: background;
			background: var(--gray4);
		}

		& + [data-cmdk-item] {
			margin-top: 4px;
		}

		svg {
			width: 18px;
			height: 18px;
		}
	}

	[data-cmdk-list] {
		height: min(330px, calc(var(--cmdk-list-height)));
		max-height: 400px;
		overflow: auto;
		overscroll-behavior: contain;
		transition: 100ms ease;
		transition-property: height;
	}

	[data-cmdk-vercel-shortcuts] {
		display: flex;
		margin-left: auto;
		gap: 8px;

		& kbd {
			font-family: var(--font-sans);
			font-size: 12px;
			min-width: 20px;
			padding: 4px;
			height: 20px;
			border-radius: 4px;
			color: var(--gray11);
			background: var(--gray4);
			display: inline-flex;
			align-items: center;
			justify-content: center;
			text-transform: uppercase;
		}
	}

	[data-cmdk-separator] {
		height: 1px;
		width: 100%;
		background: var(--gray5);
		margin: 4px 0;
	}

	*:not([hidden]) + [data-cmdk-group] {
		margin-top: 8px;
	}

	[data-cmdk-group-heading] {
		user-select: none;
		font-size: 12px;
		color: var(--gray11);
		padding: 0 8px;
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}

	[data-cmdk-empty] {
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 48px;
		white-space: pre-wrap;
		color: var(--gray11);
	}
}


================================================
File: /static/robots.txt
================================================
User-agent: *
Disallow:


================================================
File: /tests/test.ts
================================================
import { expect, test } from '@playwright/test';

test('index page has expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { name: 'Welcome to SvelteKit' })).toBeVisible();
});


================================================
File: /.changeset/README.md
================================================
# Changesets

Hello and welcome! This folder has been automatically generated by `@changesets/cli`, a build tool that works
with multi-package repos, or single-package repos to help you version and publish your code. You can
find the full documentation for it [in our repository](https://github.com/changesets/changesets)

We have a quick list of common questions to get you started engaging with this project in
[our documentation](https://github.com/changesets/changesets/blob/main/docs/common-questions.md)


================================================
File: /.changeset/config.json
================================================
{
	"$schema": "https://unpkg.com/@changesets/config@2.3.1/schema.json",
	"changelog": ["@svitejs/changesets-changelog-github-compact", { "repo": "huntabyte/cmdk-sv" }],
	"commit": false,
	"fixed": [],
	"linked": [],
	"access": "public",
	"baseBranch": "main",
	"updateInternalDependencies": "patch",
	"ignore": []
}


================================================
File: /.github/FUNDING.yml
================================================
# These are supported funding model platforms

github: [huntabyte]
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective username
ko_fi: huntabyte
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
custom: # Replace with up to 4 custom sponsorship URLs e.g., ['link1', 'link2']


================================================
File: /.github/workflows/ci.yml
================================================
name: CI

on:
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.event.number || github.sha }}
  cancel-in-progress: true

jobs:
  check:
    name: Run svelte-check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Run svelte-check
        run: pnpm check

  lint:
    runs-on: ubuntu-latest
    name: Lint
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: pnpm

      - name: Install dependencies
        run: pnpm install

      - run: pnpm lint


================================================
File: /.github/workflows/release.yml
================================================
name: Release

on:
  push:
    branches:
      - main

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    permissions:
      contents: write # to create release (changesets/action)
      pull-requests: write # to create pull request (changesets/action)
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4
        with:
          # This makes Actions fetch all Git history so that Changesets can generate changelogs with the correct commits
          fetch-depth: 0
      - uses: pnpm/action-setup@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: pnpm

      - run: pnpm install

      - name: Create Release Pull Request or Publish to npm
        id: changesets
        uses: changesets/action@v1
        with:
          publish: pnpm release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}


