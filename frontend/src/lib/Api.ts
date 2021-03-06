import { AnswerIce, OfferIce } from './Interfaces';

import TimeoutException from './TimeoutException';

interface MatchResult {
    partner: string;
    offer: OfferIce;
    offerer: boolean;
    match_id: string;
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
          if (xhr.status === 200 && xhr.response.ok) {
            resolve(xhr.response);
          } else if (xhr.status === 200 && !xhr.response.ok && xhr.response.timeout_ms) {
            reject(new TimeoutException(xhr.response.message, xhr.response.timeout_ms));
          } else {
            /* eslint-disable */
            console.error('Unhandled exception in matchAttempt');
            console.log(xhr);
            /* eslint-enable */
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
          } else {
            throw (e);
          }
        }
      }
      /* eslint-enable */
    }

    public static async postAnswerIce(match_id: string, answer: AnswerIce): Promise<void> {
      API.xhrPromise('POST', API.ANSWER_URL, { match_id,  answer });
    }

    public static async getAnswerIceAttempt(match_id: string): Promise<AnswerIce> {
      return new Promise((resolve) => {
        API.xhrPromise('GET', API.ANSWER_URL + "/" + match_id).then((xhr: XMLHttpRequest) => {
          resolve(xhr.response.answer);
        });
      });
    }

    public static async getAnswerIce(match_id: string, timeoutMS = 10000): Promise<AnswerIce> {
      let answer = await this.getAnswerIceAttempt(match_id);

      const startTime = +new Date();

      /* eslint-disable */
      while(answer === null) {
        if((+new Date() - startTime) > timeoutMS) {
          throw new Error("Timeout while awaiting answer.")
        }
        await API.wait(555);
        answer = await this.getAnswerIceAttempt(match_id);
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
