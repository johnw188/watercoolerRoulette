<script>
	import SignIn from './SignIn.svelte';
	import SelfVideo from './SelfVideo.svelte';
</script>

<div class="mainContainer">
<div class="video">
	<SelfVideo/>
</div>
<main>
	<h1>Watercooler Roulette</h1>
	<SignIn/>
</main>
</div>

<style>
	.mainContainer {
		background-color: #333333;
		position: relative;
		width: 100%;
		height: 100%;
		overflow: hidden;
	}
	.video {
		position: absolute;
		top: 0;
		width: 100%;
	}

	main {
		position: absolute;
		top: 0;
		width: 100%;
		text-align: center;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ffffff;
		font-size: 4em;
		font-weight: 600;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>