import API from './api';
import RtcHelpers from './RtcHelpers';

interface StreamPair{
  local: MediaStream;
  remote: MediaStream;
}

export default class ChatInteraction {
    private rtcHelpers: RtcHelpers;

    constructor(ident: string) {
      this.rtcHelpers = new RtcHelpers(ident);
    }

    public async getStreams(updateCB?: (stage: string) => void): Promise<StreamPair> {
      const update = updateCB || console.log;

      const offerIce = await this.rtcHelpers.getOfferIce();
      update('Created Offer');
      const match = await API.match(offerIce);
      update('Got matched');
      if (match.offerer) {
        update('Match is using my offer, waiting for their answer');
        const answerIce = await API.getAnswerIce();
        update('Answer received.');
        await this.rtcHelpers.setAnswerIce(answerIce);
        update('Setup complete, waiting on remote stream to start');
      } else {
        this.rtcHelpers = new RtcHelpers('foo');
        update('Using their offer, crafting my answer');
        const answerIce = await this.rtcHelpers.offerIceToAnswerIce(match.offer);
        update('Posting answer');
        await API.postAnswerIce(answerIce);
        update('Answer posted waiting on remote stream to start');
      }

      const local = await this.rtcHelpers.getLocalVideoStream();
      const remote = await this.rtcHelpers.getRemoteVideoStream();

      return { local, remote };
    }

    public static async runRTCTest(
      statusCB?: (status: string) => void,
    ): Promise<StreamPair> {
      const update = statusCB || console.log;
      const rtc1 = new RtcHelpers('RTC1');
      const rtc2 = new RtcHelpers('RTC2');

      const offer = await rtc1.getOfferIce();
      update('OFFER');

      const answer = await rtc2.offerIceToAnswerIce(offer);
      update('ANSWER');

      await rtc1.setAnswerIce(answer);
      update('WAITING');

      const remote = await rtc2.getRemoteVideoStream();
      update('VIDEO!');

      const local = await rtc1.getLocalVideoStream();

      return { local, remote };
    }
}
