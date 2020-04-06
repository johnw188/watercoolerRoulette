<template>
  <div id="app">
    <div v-if="!loggedIn">
      <a href="https://slack.com/oauth/authorize?scope=users.profile:read,users:read,users:read.email,identify&client_id=241546863697.1005448378753&redirect_uri=https%3A%2F%2Fapi.watercooler.express%2Fauth"><img alt="Sign in with Slack" height="40" width="172" src="https://platform.slack-edge.com/img/sign_in_with_slack.png" srcset="https://platform.slack-edge.com/img/sign_in_with_slack.png 1x, https://platform.slack-edge.com/img/sign_in_with_slack@2x.png 2x" /></a>
    </div>
    <div v-else>
      <h1>Watercooler Roulette</h1>

      <h2> Offerer Streams: </h2>
      <span title="offererLocal">
        <video alt="local" bind:this={offererLocal} ref="offererLocal" autoplay muted></video>
      </span>
      <span title="offererRemote">
        <video alt="remote" bind:this={offererRemote} ref="offererRemote" autoplay></video>
      </span>

      <h2> Ansewerer Streams: </h2>
      <span title="answererLocal">
        <video bind:this={answererLocal} ref="answererLocal" autoplay muted></video>
      </span>
      <span title="answererRemote">
        <video bind:this={answererRemote} ref="answererRemote" autoplay></video>
      </span>
      <p>
        <button v-on:click="runRTCTest">RTC TEST</button>
        <button v-on:click="runMatchTest">MATCH TEST</button>
      </p>
    </div>
  </div>
</template>

<script lang="ts">

import { Component, Vue } from 'vue-property-decorator';
import jwtDecode from 'jwt-decode';
import cookies from 'js-cookie';

import API from './lib/Api';
import ChatInteraction from './lib/ChatInteraction';
import RtcPair from './lib/RtcPair';

@Component({
  components: {},
})
export default class App extends Vue {
  displayState = 'PREINIT';

  loggedIn = false;

  $refs!: {
    offererLocal: HTMLMediaElement;
    offererRemote: HTMLMediaElement;
    answererLocal: HTMLMediaElement;
    answererRemote: HTMLMediaElement;
  };

  public mounted() {
    this.checkLogin();
  }

  public checkLogin() {
    const token = cookies.get('token');
    if (token != null) {
      if (jwtDecode(token) !== null) {
        this.loggedIn = true;
      }
    } else {
      // Shim for dev mode, where I can't see my cookie, but the API can retrieve userinfo
      API.userInfo().then(() => {
        this.loggedIn = true;
      }).catch(() => {
        this.loggedIn = false;
      });
    }
  }

  public async runRTCTest(): Promise<void> {
    const offerer = new RtcPair('Offerer');
    const answerer = new RtcPair('Answerer');

    console.log('Offer');
    const offerIce = await offerer.getOfferIce();
    console.log('Answer');
    const answerIce = await answerer.offerIceToAnswerIce(offerIce);
    console.log('Set Answer');
    await offerer.setAnswerIce(answerIce);
    console.log('Setup done');

    const offererStreamsLive = offerer.getStreams().then((pair) => {
      this.$refs.offererLocal.srcObject = pair.local;
      this.$refs.offererRemote.srcObject = pair.remote;
      console.log('O streams assigned');
    });

    const answererStreamsLive = answerer.getStreams().then((pair) => {
      this.$refs.answererLocal.srcObject = pair.local;
      this.$refs.answererLocal.srcObject = pair.remote;
      console.log('A streams assigned');
    });

    await Promise.all([offererStreamsLive, answererStreamsLive]);
  }

  public runMatchTest() {
    new ChatInteraction('NoOne').getStreams().then((pair) => {
      this.$refs.offererLocal.srcObject = pair.local;
      this.$refs.offererRemote.srcObject = pair.remote;
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

video {
  width: 45%;
  outline-width: 1px;
  outline-color: black;
  outline-style: solid;
  margin: 3px;
}
</style>
