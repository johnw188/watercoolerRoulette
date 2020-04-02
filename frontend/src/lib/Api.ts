import { AnswerIce, OfferIce } from './Interfaces';

import TimeoutException from './TimeoutException';

interface MatchResult {
    partner: string;
    offer: OfferIce;
    offerer: boolean;
}


export default class API {
    public static MATCH_URL = 'https://api.watercooler.express/match';

    public static ANSWER_URL = 'https://api.watercooler.express/answer';

    public static USER_URL = 'https://api.watercooler.express/user';

    private static async xhrPromise(
      method: string,
      url: string,
      data?: object,
    ): Promise<XMLHttpRequest> {
      return new Promise((resolve) => {
        const xhr = new XMLHttpRequest();

        xhr.addEventListener('load', () => {
          console.log(typeof xhr.response);
          resolve(xhr);
        });

        xhr.open(method, url);
        xhr.withCredentials = true;
        xhr.responseType = 'json';
        if (data) xhr.send(JSON.stringify(data));
        else xhr.send();
      });
    }

    private static async matchAttempt(offer: OfferIce): Promise<MatchResult> {
      return new Promise((resolve, reject) => {
        API.xhrPromise('POST', API.MATCH_URL, { offer }).then((xhr) => {
          if (xhr.status === 200) {
            resolve(xhr.response);
          } else if (xhr.status === 408) {
            reject(new TimeoutException(xhr.response.message, xhr.response.timeout_ms));
          } else {
            console.error('Unhandled exception in matchAttempt');
            console.log(xhr);
            reject();
          }
        });
      });
    }

    public static wait(timeoutMS: number): Promise<void> {
      return new Promise((resolve) => {
        setTimeout(() => resolve(), timeoutMS);
      });
    }

    // Return a promise that completes on match
    public static async match(offer: OfferIce): Promise<MatchResult> {
      /* eslint-disable */
      while (true) {
        try {
          return await API.matchAttempt(offer);
        } catch (e) {
          if (e instanceof TimeoutException) {
            const timeoutMS = e.getTimeoutMS();
            await API.wait(timeoutMS);
            console.log(`Waiting ${timeoutMS}ms`);
          } else {
            console.log();
            throw (e);
          }
        }
      }
      /* eslint-enable */
    }

    public static async postAnswerIce(answer: AnswerIce): Promise<void> {
      API.xhrPromise('POST', API.ANSWER_URL, { answer });
    }

    public static async getAnswerIceAttempt(): Promise<AnswerIce> {
      return new Promise((resolve) => {
        API.xhrPromise('GET', API.ANSWER_URL).then((xhr: XMLHttpRequest) => {
          resolve(xhr.response.answer);
        });
      });
    }

    public static async getAnswerIce(): Promise<AnswerIce> {
      let answer = await this.getAnswerIceAttempt();
      /* eslint-disable */
      while (answer === null) {
        await API.wait(555);
        answer = await this.getAnswerIceAttempt();
      }
      /* eslint-enable */
      return answer;
    }

    public static async userInfo(user?: string): Promise<object> {
      return new Promise((resolve, reject) => {
        let url = API.USER_URL;
        url = user ? `${url}/${user}` : url;
        API.xhrPromise('GET', url).then(
          (xhr: XMLHttpRequest) => {
            if (xhr.status === 200) {
              resolve(xhr.response);
            } else {
              reject();
            }
          },
        );
      });
    }
}
