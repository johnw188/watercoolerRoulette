import API from './Api';
import RtcPair from './RtcPair';

export default class ChatInteraction {
    private ident: string;
    // private rtcHelpers: RtcHelpers;

    constructor(ident: string) {
      this.ident = ident;
    }

    public async getRtcInitialized(): Promise<RtcPair> {
      const rtcPair = new RtcPair(`Offer-${this.ident}`);

      /* eslint-disable */
      const update = console.log;
      /* eslint-enable */

      const offerIce = await rtcPair.getOfferIce();
      update('Created Offer');
      const match = await API.match(offerIce);
      update('Got matched');
      if (match.offerer) {
        update('Match is using my offer, waiting for their answer');
        await API.wait(200); // They have to post first
        const answerIce = await API.getAnswerIce(match.match_id);
        update('Answer received.');
        await rtcPair.setAnswerIce(answerIce);
        update('Setup complete, waiting on remote stream to start');
      } else {
        update('Using their offer, crafting my answer');
        const answerIce = await rtcPair.offerIceToAnswerIce(match.offer);
        update('Posting answer');
        await API.postAnswerIce(match.match_id, answerIce);
        update('Answer posted waiting on remote stream to start');
      }

      return rtcPair;
    }
}
