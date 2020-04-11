<template>
  <div id="app">
    <div v-if="!loggedIn">
      <a
        href="https://slack.com/oauth/authorize?scope=users.profile:read,identify&client_id=241546863697.1005448378753&redirect_uri=https%3A%2F%2Fapi.watercooler.express%2Fauth"
      >
        <img
          alt="Sign in with Slack"
          height="40"
          width="172"
          src="https://platform.slack-edge.com/img/sign_in_with_slack.png"
          srcset="https://platform.slack-edge.com/img/sign_in_with_slack.png 1x, https://platform.slack-edge.com/img/sign_in_with_slack@2x.png 2x"
        />
      </a>
    </div>
    <div v-else>
      <h1>Watercooler Express: Totally super working</h1>

      <div v-if="matching">
        <Spinner />
        <p>Matching...</p>
      </div>
      <VideoChat v-show="matched" ref="videoChat" />

      <p>
        <b-button v-if="!matching" v-on:click="runMatch">Match me!</b-button>
      </p>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import jwtDecode from 'jwt-decode';
import cookies from 'js-cookie';

import API from './lib/Api';

import Spinner from './components/Spinner.vue';
import VideoChat from './components/VideoChat.vue';

@Component({
  components: { Spinner, VideoChat },
})
export default class App extends Vue {
  displayState = 'PREINIT';

  loggedIn = false;

  matching = false;

  matched = false;

  $refs!: {
    videoChat: VideoChat;
  }

  public mounted() {
    this.checkLogin();
  }

  public checkLogin() {
    const token = cookies.get('token');
    if (token != null) {
      if (jwtDecode(token) !== null) {
        this.loggedIn = true;
      }
    } else if (window.location.hostname === 'localhost') {
      // Shim for dev mode, where I can't see my cookie, but the API can retrieve userinfo
      API.userInfo()
        .then(() => {
          this.loggedIn = true;
        })
        .catch(() => {
          this.loggedIn = false;
        });
    } else {
      this.loggedIn = false;
    }
  }

  public runMatch() {
    this.matching = true;
    this.$refs.videoChat.connectUser().then(() => {
      this.matched = true;
      this.matching = false;
    });
    this.$refs.videoChat.onDisconnect = () => {
      this.matched = false;
      // this.runMatch();
    };
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
