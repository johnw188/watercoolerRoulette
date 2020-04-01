import API from './api';
import RtcHelpers from './RtcHelpers';

interface StreamPair{
  local: MediaStream;
  remote: MediaStream;
}

export default class ChatInteraction {
    private rtcHelpers: RtcHelpers;

    constructor() {
      this.rtcHelpers = new RtcHelpers('myidentity');
    }

    public async getStreams(stateCB?: (stage: string) => void): Promise<StreamPair> {
      stateCB = stateCB || console.log;

      const offerIce = await this.rtcHelpers.getOfferIce();
      stateCB('Created Offer');
      const match = await API.match(offerIce);
      stateCB('Got matched');
      if (match.offerer) {
        stateCB('Match is using my offer, waiting for their answer');
        const answerIce = await API.getAnswerIce();
        stateCB('Answer received.');
        await this.rtcHelpers.setAnswerIce(answerIce);
        stateCB('Setup complete, waiting on remote stream to start');
      } else {
        stateCB('Using their offer, crafting my answer');
        const answerIce = await this.rtcHelpers.offerIceToAnswerIce(match.offer);
        stateCB('Posting answer');
        await API.postAnswerIce(answerIce);
        stateCB('Answer posted waiting on remote stream to start');
      }

      const local = await this.rtcHelpers.getLocalVideoStream();
      const remote = await this.rtcHelpers.getRemoteVideoStream();

      return { local, remote };
    }
}
