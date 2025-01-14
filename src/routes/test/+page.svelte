<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { cn } from '$lib/utils';
	import { createNoise3D } from 'simplex-noise';

	export let colors: string[] = ['#38bdf8', '#818cf8', '#c084fc', '#e879f9', '#22d3ee'];
	export let waveWidth: number | undefined = undefined;
	export let backgroundFill: string | undefined = undefined;
	export let blur: number = 10;
	export let speed: 'slow' | 'fast' = 'fast';
	export let waveOpacity: number = 0.5;
	export let containerClassName: string | undefined = undefined;
	export let className: string | undefined = undefined;

	let canvas: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D;
	let w: number;
	let h: number;
	let nt = 0;
	let animationId: number;
	let isSafari = false;

	const noise = createNoise3D();

	const getSpeed = () => {
		switch (speed) {
			case 'slow':
				return 0.001;
			case 'fast':
				return 0.002;
			default:
				return 0.001;
		}
	};

	const drawWave = (n: number) => {
		nt += getSpeed();
		for (let i = 0; i < n; i++) {
			ctx.beginPath();
			ctx.lineWidth = waveWidth || 50;
			ctx.strokeStyle = colors[i % colors.length];
			for (let x = 0; x < w; x += 5) {
				const y = noise(x / 800, 0.3 * i, nt) * 100;
				ctx.lineTo(x, y + h * 0.5);
			}
			ctx.stroke();
			ctx.closePath();
		}
	};

	const render = () => {
		ctx.fillStyle = backgroundFill || 'black';
		ctx.globalAlpha = waveOpacity;
		ctx.fillRect(0, 0, w, h);
		drawWave(5);
		animationId = requestAnimationFrame(render);
	};

	const init = () => {
		ctx = canvas.getContext('2d')!;
		w = ctx.canvas.width = window.innerWidth;
		h = ctx.canvas.height = window.innerHeight;
		ctx.filter = `blur(${blur}px)`;
		nt = 0;
		render();
	};

	const handleResize = () => {
		w = ctx.canvas.width = window.innerWidth;
		h = ctx.canvas.height = window.innerHeight;
		ctx.filter = `blur(${blur}px)`;
	};

	onMount(() => {
		init();
		window.addEventListener('resize', handleResize);

		// Safari detection
		isSafari =
			typeof window !== 'undefined' &&
			navigator.userAgent.includes('Safari') &&
			!navigator.userAgent.includes('Chrome');
	});

	onDestroy(() => {
		if (animationId) {
			cancelAnimationFrame(animationId);
		}
	//	window.removeEventListener('resize', handleResize);
	});
</script>

<div class={cn('h-screen flex flex-col items-center justify-center', containerClassName)}>
	<canvas
		class="absolute inset-0 z-0"
		bind:this={canvas}
		id="canvas"
		style={isSafari ? `filter: blur(${blur}px)` : ''}
	>
    </canvas>
	<div class={cn('relative z-10', className)}>
		<slot />
	</div>
</div>
