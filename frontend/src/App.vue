<template>
  <div id="app">
    <div v-if="!loggedIn">
      <a href="https://slack.com/oauth/authorize?scope=users.profile:read,users:read,users:read.email,identify&client_id=241546863697.1005448378753&redirect_uri=https%3A%2F%2Fapi.watercooler.express%2Fauth"><img alt="Sign in with Slack" height="40" width="172" src="https://platform.slack-edge.com/img/sign_in_with_slack.png" srcset="https://platform.slack-edge.com/img/sign_in_with_slack.png 1x, https://platform.slack-edge.com/img/sign_in_with_slack@2x.png 2x" /></a>
    </div>
    <div v-else>
      <h1>Watercooler Roulette</h1>
      <video bind:this={localVideo} id="localVideo" ref="localVideo" autoplay muted></video>
      <video bind:this={remoteVideo} id="remoteVideo" ref="remoteVideo" autoplay></video>
      <p>{{displayState}}</p>

    <button v-on:click="runRTCTest">RTC TEST</button>
    <button v-on:click="runMatchTest">MATCH TEST</button>

    </div>
  </div>
</template>

<script lang="ts">

import { Component, Vue } from 'vue-property-decorator';
import jwtDecode from 'jwt-decode';
import cookies from 'js-cookie';

import API from './lib/api';
import RtcHelpers from './lib/RtcHelpers';
import ChatInteraction from './lib/interaction';

@Component({
  components: {},
})
export default class App extends Vue {
  displayState = 'PREINIT';

  loggedIn = false;

  $refs!: {
    remoteVideo: HTMLMediaElement;
    localVideo: HTMLMediaElement;
  };

  public mounted() {
    console.log('I AM ALIVE');
    this.checkLogin();
  }

  // TODO(meawoppl) call me
  public checkLogin() {
    const token = cookies.get('token');
    if (token != null) {
      if (jwtDecode(token) !== null) {
        this.loggedIn = true;
      }
    } else {
      // Shim for dev mode, where I can't see my cookie, but the API can
      API.userInfo().then(() => {
        this.loggedIn = true;
      }).catch(() => {
        this.loggedIn = false;
      });
    }
  }

  public runRTCTest() {
    ChatInteraction.runRTCTest().then((pair) => {
      this.$refs.localVideo.srcObject = pair.local;
      this.$refs.remoteVideo.srcObject = pair.remote;
    });
  }

  public runMatchTest() {
    new ChatInteraction('NoOne').getStreams().then((pair) => {
      this.$refs.localVideo.srcObject = pair.local;
      this.$refs.remoteVideo.srcObject = pair.remote;
    });
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
