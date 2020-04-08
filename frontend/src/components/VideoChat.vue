<template>
  <div>
    <span title="localVideo">
      <video alt="local" bind:this="{local}" ref="local" autoplay muted></video>
    </span>
    <span title="remoteVideo">
      <video alt="remote" bind:this="{remote}" ref="remote" autoplay></video>
    </span>
    <b-progress :value="progressBarTime" :max="CHAT_DURATION"></b-progress>
    {{ countdownValue }}
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Timer, TimeCounter } from 'easytimer.js';
import ChatInteraction from '../lib/ChatInteraction';
import RtcPair from '../lib/RtcPair';

@Component
export default class VideoChat extends Vue {
  $refs!: {
    local: HTMLMediaElement;
    remote: HTMLMediaElement;
  };

  readonly CHAT_DURATION = 60;

  activeRTCPair?: RtcPair;

  timer = new Timer();

  progressBarTime = 0;

  countdownValue = this.CHAT_DURATION;

  public async connectUser() {
    return new ChatInteraction('NoOne').getRtcInitialized().then((rtc) => {
      rtc.getStreams().then((streams) => {
        this.$refs.local.srcObject = streams.local;
        this.$refs.remote.srcObject = streams.remote;
        this.activeRTCPair = rtc;
        this.startTimer();
      });
    });
  }

  public startTimer() {
    console.log('Starting timers');
    this.timer.start({
      precision: 'secondTenths',
      startValues: { seconds: 0 },
      target: { seconds: this.CHAT_DURATION },
    });
    this.timer.addEventListener('secondTenthsUpdated', () => {
      this.updateProgress(this.timer.getTimeValues());
    });
    this.timer.addEventListener('targetAchieved', () => {
      this.disconnectUser();
      this.progressBarTime = 0;
      this.countdownValue = this.CHAT_DURATION;
    });
  }

  public updateProgress(timeValues: TimeCounter) {
    this.progressBarTime = timeValues.secondTenths * 0.1 + timeValues.seconds;
    this.countdownValue = this.CHAT_DURATION - timeValues.seconds;
    console.log(`Progress bar time: ${this.progressBarTime}, Countdown Value: ${this.countdownValue}`);
  }

  public disconnectUser() {
    if (this.activeRTCPair) {
      this.activeRTCPair.close();
      this.activeRTCPair = undefined;
    }
  }
}
</script>

<style scoped>
video {
  width: 45%;
  outline-width: 1px;
  outline-color: black;
  outline-style: solid;
  margin: 3px;
}
</style>
