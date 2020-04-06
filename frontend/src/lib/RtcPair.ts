import { AnswerIce, OfferIce, StreamPair } from './Interfaces';
import WebRtcWrapper from './WebRtcWrapper';

export default class RtcPair {
    private pcOffer: WebRtcWrapper

    private pcAnswer: WebRtcWrapper;

    private pc: WebRtcWrapper | null;

    private identity: string;

    constructor(identity: string) {
      this.identity = identity;

      this.pcOffer = new WebRtcWrapper(`O-${this.identity}`);
      this.pcAnswer = new WebRtcWrapper(`A-${this.identity}`);

      this.pc = null;
    }

    /* eslint-disable */
    private log(...args: any[]) {
      console.log(`Identity:${this.identity}`);
      args.map(console.log);
    }
    /* eslint-enable */

    public async getOfferIce(): Promise<OfferIce> {
      this.pcAnswer.close();
      this.pc = this.pcOffer;
      return this.pcOffer.getOfferIce();
    }

    public async offerIceToAnswerIce(offerIce: OfferIce): Promise<AnswerIce> {
      // If this is called, I am the answerer
      this.pcOffer.close();
      const answerIce = await this.pcAnswer.offerIceToAnswerIce(offerIce);

      this.pc = this.pcAnswer;
      return answerIce;
    }

    public async setAnswerIce(answerIce: AnswerIce): Promise<void> {
      // If this is called I am the offerer
      await this.requirePC().setAnswerIce(answerIce);
      this.pc = this.pcOffer;
    }

    private requirePC(): WebRtcWrapper {
      if (this.pc) {
        return this.pc;
      }
      throw new Error('Not setup yet');
    }

    public async sendMessage(message: string): Promise<void> {
      return this.requirePC().sendMessage(message);
    }

    public async getStreams(): Promise<StreamPair> {
      return this.requirePC().getStreams();
    }

    public async close(): Promise<void> {
      this.pcOffer.close();
      this.pcAnswer.close();
    }
}
