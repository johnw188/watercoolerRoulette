<div>
	<video bind:this={video} autoplay="true" id="videoElement">
	</video>
</div>

<style>
    div {
        width: 100%;
        height: 100%;
        overflow: hidden;
        -webkit-filter: blur(15px);
        -moz-filter: blur(15px);
        -o-filter: blur(15px);
        -ms-filter: blur(15px);
        filter: blur(15px);
    }
    video {
        width: 100%;
    }
</style>

<script>
import onMount from 'svelte';

let video;

onMount(() => {
  console.log("Video: "  + video)
  if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function (stream) {
        video.srcObject = stream;
      })
      .catch(function (err) {
        console.log("Something went wrong!" + err);
      });
  }
})
</script>