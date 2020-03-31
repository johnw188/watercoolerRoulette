<script>
	import SignIn from './SignIn.svelte';
	import SelfVideo from './SelfVideo.svelte';
	import WebRTCConnection from './webrtcConnect.js'
	import API from './api.ts'
	import RtcHelpers from './RtcHelpers.ts'

	let localVideo;
	let remoteVideo;

	let rtc1 = new RtcHelpers("RTC1");
	let rtc2 = new RtcHelpers("RTC2");

	let display = "testing testing"

	rtc1.getOfferIce().then((offer)=>{
		display = "OFFER"
		console.log(offer)
		rtc2.offerIceToAnswerIce(offer).then((answer)=>{
			display = "ANSWER";
			rtc1.setAnswerIce(answer).then(()=>{
				display = "PRESEND";
				rtc1.sendMessage("Foo");
				rtc2.sendMessage("Bar");
			});
		})
	});

	function handleClick(event) {
		rtc1.sendMessage("Foo");
		rtc2.sendMessage("Bar");
	};
	
	rtc1.beginLocalVideoStream().then((localStream) => {
		localVideo.srcObject = localStream
	})

</script>

<div class="mainContainer">
<div class="video">
</div>
<main>
	<h1>Watercooler Roulette</h1>
	<SignIn on:click={handleClick}/>
	<video bind:this={localVideo} id="localVideo" autoplay muted></video>
	<video bind:this={remoteVideo} id="remoteVideo" autoplay></video>
	<p>{display}</p>
</main>
</div>

<style>
	.mainContainer {
		/* background-color: #333333; */
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
		/* color: #ffffff; */
		font-size: 4em;
		font-weight: 600;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>