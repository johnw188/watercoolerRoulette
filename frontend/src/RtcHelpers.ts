interface OfferIce{
    offer: RTCSessionDescriptionInit,
    ice: Array<RTCIceCandidate>
}

interface AnswerIce {
    answer: RTCSessionDescriptionInit,
    ice: Array<RTCIceCandidate>
}

export default class RtcHelpers {
    private _identity: string
    private _rtc: RTCPeerConnection;
    private _dcSend: RTCDataChannel;
    private _dcRecv: RTCDataChannel;
    private _iceWaiter: Promise<Array<RTCIceCandidate>>;
    private _channelsSetup: Promise<void>;

    constructor(identity: string) {
        this._identity = identity;

        const configuration = {
            iceServers: [{
                urls: 'stun:stun.l.google.com:19302'
            }]
        };

        this._rtc = new RTCPeerConnection(configuration);
        
        this._iceWaiter = new Promise((resolve, reject)=>{
            let _localIce = new Array<RTCIceCandidate>();
            this._rtc.onicecandidate = (e)=>{
                console.log(e.candidate);
                if(e.candidate !== null)
                    _localIce.push(e.candidate);
                else {
                    resolve(_localIce);
                }
            };    
        });

        // Setup data channel and configs for when channel is established
        this._channelsSetup = new Promise((resolve, reject)=>{
            const dcConfig = {};
            this._dcSend = this._rtc.createDataChannel('test-wcr', dcConfig);
            this._dcSend.onmessage = (event)=>this.log(" Message SEND:", event);
            this._dcSend.onopen = (event)=>this.log(" Open SEND:", event);
            this._dcSend.onclose = (event) => this.log("Close SEND:", event);
    
            this._rtc.ondatachannel = (event) => {
                console.log("ODC");
                this._dcRecv = event.channel;
                this._dcRecv.onmessage = (event)=> this.log("Message RECV", event)
                this._dcRecv.onopen = (event)=>{
                    this.log(" Open RECV:" + event);
                    resolve();
                };
                this._dcRecv.onclose = (event) => this.log("Close RECV:", event);
            }
        }); 
    }

    private log(...args: any[]) {
        console.log("Identity:" + this._identity)
        args.map(console.log);
    }

    public async getOfferIce(): Promise<OfferIce> {      
        let offer = await this._rtc.createOffer()
        await this._rtc.setLocalDescription(offer);
        let ice = await this._iceWaiter;
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

        let answer = await this._rtc.createAnswer();
        await this._rtc.setLocalDescription(answer);
        let ice = await this._iceWaiter;
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
}
