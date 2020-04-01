import API from './api';
import RtcHelpers from './RtcHelpers';

export default class ChatInteraction {
    private _api: API;
    private _rtcHelpers: RtcHelpers;

    constructor() {
        this._api = new API();
        this._rtcHelpers = new RtcHelpers("myidentity");
    }


    public async doTheWork(): Promise<Array<MediaStream>> {
        let offerIce = await this._rtcHelpers.getOfferIce()
        let match = await this._api.match(offerIce);
        if(match.offerer) {
            let answerIce = await this._api.get_answer();
            await this._rtcHelpers.setAnswerIce(answerIce);
        } else {
            let answerIce = await this._rtcHelpers.offerIceToAnswerIce(match.offer);
            await this._api.post_answer(answerIce);
        }

        let localStream = await this._rtcHelpers.getLocalVideoStream();
        let remoteStream = await this._rtcHelpers.getRemoteVideoStream();

        return [localStream, remoteStream];
    }
}
