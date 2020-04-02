import { AnswerIce, OfferIce } from './interfaces';

export default class RtcHelpers {
    private identity: string

    private pc: RTCPeerConnection;

    private dcSend?: RTCDataChannel;

    private dcRecv?: RTCDataChannel;

    private iceWaiter: Promise<Array<RTCIceCandidate>>;

    private channelsSetup: Promise<void>;

    private remoteStreamWaiter: Promise<Array<MediaStream>>;

    private webcamWaiter: Promise<MediaStream>;

    constructor(identity: string) {
      this.identity = identity;

      const configuration = {
        iceServers: [{
          urls: 'stun:stun.l.google.com:19302',
        }],
      };

      this.pc = new RTCPeerConnection(configuration);

      // This promise resolved after ICE candidate transmission is done
      this.iceWaiter = new Promise((resolve) => {
        const iceOptions = new Array<RTCIceCandidate>();
        this.pc.onicecandidate = (e) => {
          if (e.candidate !== null) {
            iceOptions.push(e.candidate);
          } else {
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
        this.pc.ontrack = (event) => resolve(event.streams.slice(0, event.streams.length));
      });

      const mediaConstraints = {
        audio: true, // We want an audio track
        video: {
          aspectRatio: {
            ideal: 1.333333, // 3:2 aspect is preferred
          },
        },
      };

      // Putting this here gets the user prompt up as soon as the module is loaded
      this.webcamWaiter = navigator.mediaDevices.getUserMedia(mediaConstraints);
    }

    private log(...args: any[]) {
      console.log(`Identity:${this.identity}`);
      args.map(console.log);
    }

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
      console.log(offerIce);
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

    public async getRemoteVideoStream(): Promise<MediaStream> {
      const streams = await this.remoteStreamWaiter;
      return streams[0];
    }

    private async beginRTCVideoStream(): Promise<void> {
      const webcamStream = await this.getLocalVideoStream();
      webcamStream.getTracks().forEach(
        (track) => this.pc.addTransceiver(track, { streams: [webcamStream] }),
      );
    }

    public async getLocalVideoStream(): Promise<MediaStream> {
      return this.webcamWaiter;
    }
}
