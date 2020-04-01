import {AnswerIce, OfferIce} from "./interfaces"

export default class RtcHelpers {
    private _identity: string
    private _rtc: RTCPeerConnection;
    private _dcSend: RTCDataChannel;
    private _dcRecv: RTCDataChannel;
    private _iceWaiter: Promise<Array<RTCIceCandidate>>;
    private _channelsSetup: Promise<void>;
    private _remoteStreamWaiter: Promise<Array<MediaStream>>;
    private _webcamWaiter: Promise<MediaStream>;

    constructor(identity: string) {
      this._identity = identity;

      const configuration = {
        iceServers: [{
          urls: 'stun:stun.l.google.com:19302',
        }],
      };

      this._rtc = new RTCPeerConnection(configuration);

      // This promise resolved after ICE candidate transmission is done
      this._iceWaiter = new Promise((resolve, reject)=>{
        const _localIce = new Array<RTCIceCandidate>();
        this._rtc.onicecandidate = (e)=>{
          if (e.candidate !== null) {
            _localIce.push(e.candidate);
          } else {
            resolve(_localIce);
          }
        };
      });

      // Text signaling data channel
      // Setup data channel and configs for when channel is established
      this._channelsSetup = new Promise((resolve, reject)=>{
        const dcConfig = {};
        this._dcSend = this._rtc.createDataChannel('test-wcr', dcConfig);
        this._dcSend.onmessage = (event)=>this.log('Message SEND:', event);
        // this._dcSend.onopen = (event)=>this.log("Open SEND:", event);
        this._dcSend.onclose = (event) => this.log('Close SEND:', event);

        this._rtc.ondatachannel = (event) => {
          this._dcRecv = event.channel;
          this._dcRecv.onmessage = (event)=> this.log('Message RECV', event);
          this._dcRecv.onopen = (event)=>{
            this.log(' Open RECV:' + event);
            resolve();
          };
          this._dcRecv.onclose = (event) => this.log('Close RECV:', event);
        };
      });

      // This promise comes live after receiving a remote stream
      this._remoteStreamWaiter = new Promise((resolve, reject)=>{
        this._rtc.ontrack = (event) => resolve(event.streams.slice(0, event.streams.length));
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
      this._webcamWaiter = navigator.mediaDevices.getUserMedia(mediaConstraints);
    }

    private log(...args: any[]) {
      console.log('Identity:' + this._identity);
      args.map(console.log);
    }

    public async getOfferIce(): Promise<OfferIce> {
      // Must complete before ice init
      await this._beginRTCVideoStream();

      const offer = await this._rtc.createOffer();
      await this._rtc.setLocalDescription(offer);
      const ice = await this._iceWaiter;
      return {offer, ice};
    }

    private async addAllIceCandidates(candidates: Array<RTCIceCandidate>): Promise<void> {
      await Promise.all(candidates.map((ic)=>{
        this._rtc.addIceCandidate(ic).catch(this.log);
      }));
    }

    public async offerIceToAnswerIce(offerIce: OfferIce): Promise<AnswerIce> {
      await this._rtc.setRemoteDescription(offerIce.offer);
      await this.addAllIceCandidates(offerIce.ice);
      await this._beginRTCVideoStream();

      const answer = await this._rtc.createAnswer();
      await this._rtc.setLocalDescription(answer);
      const ice = await this._iceWaiter;
      return {answer, ice};
    }

    public async setAnswerIce(answerIce: AnswerIce): Promise<void> {
      await this._rtc.setRemoteDescription(answerIce.answer);
      await this.addAllIceCandidates(answerIce.ice);
    }

    public async sendMessage(message: string): Promise<void> {
      await this._channelsSetup;
      this._dcSend.send(message);
    }

    public async getRemoteVideoStream(): Promise<MediaStream> {
      const streams = await this._remoteStreamWaiter;
      return streams[0];
    }

    private async _beginRTCVideoStream(): Promise<void> {
      const webcamStream = await this.getLocalVideoStream();
      webcamStream.getTracks().forEach(
          (track) => this._rtc.addTransceiver(track, {streams: [webcamStream]}));
    }

    public async getLocalVideoStream(): Promise<MediaStream> {
      return this._webcamWaiter;
    }
}
