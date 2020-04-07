import { AnswerIce, OfferIce, StreamPair } from './Interfaces';

export default class WebRtcWrapper {
    private identity: string

    private pc: RTCPeerConnection;

    private dcSend?: RTCDataChannel;

    private dcRecv?: RTCDataChannel;

    private iceWaiter: Promise<Array<RTCIceCandidate>>;

    private channelsSetup: Promise<void>;

    private remoteStreamWaiter: Promise<Array<MediaStream>>;

    private webcamWaiter: Promise<MediaStream>;

    private transceivers: Array<RTCRtpTransceiver>;

    constructor(identity: string) {
      this.identity = identity;

      const configuration = {
        iceServers: [{
          urls: 'stun:stun.l.google.com:19302',
        }],
      };

      this.pc = new RTCPeerConnection(configuration);

      this.transceivers = [];

      // This promise resolved after ICE candidate transmission is done
      this.iceWaiter = new Promise((resolve) => {
        const iceOptions = new Array<RTCIceCandidate>();
        this.pc.onicecandidate = (e) => {
          if (e.candidate !== null) {
            iceOptions.push(e.candidate);
          } else {
            this.log(`Completed Gathering candidates:${iceOptions.length}`);
            resolve(iceOptions);
          }
        };
      });

      // Text signaling data channel
      // Setup data channel and configs for when channel is established
      this.channelsSetup = new Promise((resolve) => {
        const dcConfig = {};
        this.dcSend = this.pc.createDataChannel('test-wcr', dcConfig);
        this.dcSend.onmessage = (e) => this.log('Message SEND:', e);
        // this._dcSend.onopen = (event)=>this.log("Open SEND:", event);
        this.dcSend.onclose = (e) => this.log('Close SEND:', e);

        this.pc.ondatachannel = (channelEvent) => {
          this.dcRecv = channelEvent.channel;
          this.dcRecv.onmessage = (e) => this.log('Message RECV', e);
          this.dcRecv.onopen = (e) => {
            this.log(` Open RECV:${e}`);
            resolve();
          };
          this.dcRecv.onclose = (e) => this.log('Close RECV:', e);
        };
      });

      // This promise comes live after receiving a remote stream
      this.remoteStreamWaiter = new Promise((resolve) => {
        this.pc.ontrack = (event) => {
          this.log('ONTRACK', event.streams);
          resolve(event.streams.slice(0, event.streams.length));
        };
      });

      const mediaConstraints = {
        audio: true, // We want an audio track
        video: {
          facingMode: { ideal: 'user' },
          aspectRatio: { ideal: 1.333333 }, // 3:2 aspect is preferred
        },
      };

      // Putting this here gets the user prompt up as soon as the module is loaded
      this.webcamWaiter = navigator.mediaDevices.getUserMedia(mediaConstraints);
    }

    /* eslint-disable */
    private log(...args: any[]) {
      console.log(`Identity:${this.identity}`);
      args.map(console.log);
    }
    /* eslint-enable */

    public async getOfferIce(): Promise<OfferIce> {
      // Must complete before ice init
      await this.beginRTCVideoStream();

      const offer = await this.pc.createOffer();
      await this.pc.setLocalDescription(offer);
      const ice = await this.iceWaiter;
      return { offer, ice };
    }

    private async addAllIceCandidates(candidates: Array<RTCIceCandidate>): Promise<void> {
      await Promise.all(candidates.map((ic) => this.pc.addIceCandidate(ic).catch(this.log)));
    }

    public async offerIceToAnswerIce(offerIce: OfferIce): Promise<AnswerIce> {
      await this.pc.setRemoteDescription(offerIce.offer);
      await this.addAllIceCandidates(offerIce.ice);
      await this.beginRTCVideoStream();

      const answer = await this.pc.createAnswer();
      await this.pc.setLocalDescription(answer);
      const ice = await this.iceWaiter;
      return { answer, ice };
    }

    public async setAnswerIce(answerIce: AnswerIce): Promise<void> {
      await this.pc.setRemoteDescription(answerIce.answer);
      await this.addAllIceCandidates(answerIce.ice);
    }

    public async sendMessage(message: string): Promise<void> {
      await this.channelsSetup;
      if (this.dcSend) this.dcSend.send(message);
    }

    public async getStreams(): Promise<StreamPair> {
      const local = await this.webcamWaiter;
      this.log('Got local stream');

      const remote = (await this.remoteStreamWaiter)[0];
      this.log('got remote stream');
      return { local, remote };
    }

    private async beginRTCVideoStream(): Promise<void> {
      const webcamStream = await this.webcamWaiter;
      webcamStream.getTracks().forEach(
        (track) => this.pc.addTrack(track, webcamStream),
      );
    }

    public async close(): Promise<void> {
      this.pc.getTransceivers().forEach(this.log);
      // this.pc.getTransceivers().forEach((tx) => tx.stop());
      this.pc.close();
    }
}
