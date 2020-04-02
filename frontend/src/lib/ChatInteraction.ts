import API from './Api';
import RtcHelpers from './RtcHelpers';

interface StreamPair{
  local: MediaStream;
  remote: MediaStream;
}

export default class ChatInteraction {
    private rtc?: RtcHelpers;

    private ident: string;
    // private rtcHelpers: RtcHelpers;

    constructor(ident: string) {
      this.ident = ident;
    }

    public async getStreams(updateCB?: (stage: string) => void): Promise<StreamPair> {
      const offerRTC = new RtcHelpers(`Offer${this.ident}`);
      const answerRTC = new RtcHelpers(`Answer${this.ident}`);

      const update = updateCB || console.log;

      const offerIce = await offerRTC.getOfferIce();
      update('Created Offer');
      const match = await API.match(offerIce);
      update('Got matched');
      if (match.offerer) {
        update('Match is using my offer, waiting for their answer');
        await API.wait(200); // They have to post first
        const answerIce = await API.getAnswerIce();
        update('Answer received.');
        await offerRTC.setAnswerIce(answerIce);
        update('Setup complete, waiting on remote stream to start');
        this.rtc = offerRTC;
      } else {
        update('Using their offer, crafting my answer');
        const answerIce = await answerRTC.offerIceToAnswerIce(match.offer);
        update('Posting answer');
        await API.postAnswerIce(answerIce);
        update('Answer posted waiting on remote stream to start');
        this.rtc = answerRTC;
      }

      update('Getting local video hook');
      const local = await this.rtc.getLocalVideoStream();

      update('Getting remote video hook');
      const remote = await this.rtc.getRemoteVideoStream();

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

      // await rtc2.getOfferIce();
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
