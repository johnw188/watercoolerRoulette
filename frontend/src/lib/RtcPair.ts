import { AnswerIce, OfferIce, StreamPair } from './Interfaces';
import WebRtcWrapper from './WebRtcWrapper';

/**
 * This module initializes a pair of RTCPeerConnections to support the slightly
 * strange practice of generating an Rtc Offer and possibly discarding it in favor
 * the other parties offer.
 *
 * @export
 * @class RtcPair
 */
export default class RtcPair {
    private pcOffer: WebRtcWrapper

    private pcAnswer: WebRtcWrapper;

    private pc?: WebRtcWrapper;

    private isOffer?: boolean;

    private identity: string;


    /**
     *Creates an instance of RtcPair.
     * @param {string} identity
     * @memberof RtcPair
     */
    constructor(identity: string) {
      this.identity = identity;

      this.pcOffer = new WebRtcWrapper(`O-${this.identity}`);
      this.pcAnswer = new WebRtcWrapper(`A-${this.identity}`);
    }


    /**
     * Get an offer + ice candidates.
     *
     * @returns {Promise<OfferIce>}
     * @memberof RtcPair
     */
    public async getOfferIce(): Promise<OfferIce> {
      return this.pcOffer.getOfferIce();
    }


    /**
     * Commit to being the answering party in the conversion.
     *
     * Uses the `OfferIce` passed in to produce a corresponding
     * `AnswerIce` on promise maturation.
     *
     * @param {OfferIce} offerIce
     * @returns {Promise<AnswerIce>}
     * @memberof RtcPair
     */
    public async offerIceToAnswerIce(offerIce: OfferIce): Promise<AnswerIce> {
      // If this is called, I am the answerer
      const answerIce = await this.pcAnswer.offerIceToAnswerIce(offerIce);

      this.pc = this.pcAnswer;
      this.isOffer = false;
      return answerIce;
    }


    /**
     * Commit to being the offering party in the conversation.
     *
     * Use `AnswerIce` instance to complete the RTC handshaking process.
     *
     * @param {AnswerIce} answerIce
     * @returns {Promise<void>}
     * @memberof RtcPair
     */
    public async setAnswerIce(answerIce: AnswerIce): Promise<void> {
      // If this is called I am the offerer
      await this.pcOffer.setAnswerIce(answerIce);
      this.pc = this.pcOffer;
      this.isOffer = true;
    }


    /**
     * Used for methods that require commitment to a role in the Rtc process
     * Returns the active `RtcPeerConnection` that this instance should be using
     *
     * @private
     * @returns {WebRtcWrapper}
     * @memberof RtcPair
     */
    private requirePC(): WebRtcWrapper {
      if (this.pc) {
        return this.pc;
      }
      throw new Error('Not setup yet');
    }


    public async getClosePromise(): Promise<void> {
      this.requirePC().getClosePromise();
    }

    /**
     * Send a message to the peer that will be handled by the function
     * setup using `setOnMessage()`
     *
     * @param {string} message
     * @returns {Promise<void>}
     * @memberof RtcPair
     */
    public async sendMessage(message: string): Promise<void> {
      return this.requirePC().sendMessage(message);
    }


    /**
     * Set the callback to be run with the peer calls `sendMessage()`.
     * This handler will be called with the raw `MessageEvent` instance:
     * {@link https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent}
     *
     * @param {(event: MessageEvent) => void} handler
     * @memberof RtcPair
     */
    public setOnMessage(handler: (event: MessageEvent) => void): void {
      this.requirePC().setOnMessage(handler);
    }

    public async getStreams(): Promise<StreamPair> {
      return this.requirePC().getStreams();
    }

    public isOfferer(): boolean {
      if (this.isOffer !== undefined) {
        return this.isOffer;
      }
      throw new Error('Not setup yet!!');
    }

    public close(): void {
      this.pcOffer.close();
      this.pcAnswer.close();
    }
}
