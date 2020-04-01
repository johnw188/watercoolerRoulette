import {AnswerIce, OfferIce} from "./interfaces"

interface MatchResult {
    partner: string,
    offer: OfferIce,
    offerer: boolean
}


export default class API {
    public static MATCH_URL = 'https://api.watercooler.express/match';
    public static ANSWER_URL = 'https://api.watercooler.express/answer';
    public static USER_URL = 'https://api.watercooler.express/user';

    constructor() { }

    private async _xhr_promise(method: string, url: string, data: object): Promise<XMLHttpRequest> {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.addEventListener('load', () => {
          console.log('Loaded: ' + xhr.status);
          console.log(xhr.response);
          console.log();
          if (xhr.status == 200) {
            // If successful
            resolve(xhr);
          } else {
            reject(xhr);
          }
        });

        xhr.open(method, url);
        xhr.withCredentials = true;
        xhr.responseType = 'json';
        xhr.send(JSON.stringify(data));
      });
    }

    private async _match(offer: object): Promise<MatchResult> {
      return new Promise((resolve, reject)=>{
        const xhr_promise: Promise<XMLHttpRequest> = this._xhr_promise('POST', API.MATCH_URL, {offer: offer});

        xhr_promise.then((xhr)=>resolve(xhr.response));
        xhr_promise.catch((xhr)=>{
          if (xhr.status == 408) {
            console.log('Timeout during matching');
            reject({timeout_ms: xhr.response.timeout_ms});
          } else {
            console.log('Unhandled fail :(');
            // If failed
            reject({
              status: xhr.status,
              statusText: xhr.statusText,
              response: xhr.response,
            });
          }
        });
      });
    }

    private wait(timeout_ms: number): Promise<void> {
      return new Promise((resolve, reject)=>{
        setTimeout(()=>resolve(), timeout_ms);
      });
    }

    // Return a promise that completes on match
    public async match(offer: object): Promise<MatchResult> {
      while(true) {
        try {
          return await this._match(offer);
        } catch (e) {
          if (e.timeout_ms) {
            await this.wait(e.timeout_ms);
            console.log('Waiting ' + e.timeout_ms + 'ms');
          } else {
            throw (e);
          }
        }
      }
    }

    public async post_answer(answer: object): Promise<void> {
      this._xhr_promise('POST', API.ANSWER_URL, {answer: answer});
    }

    public async get_answer(): Promise<AnswerIce> {
      return new Promise((resolve, reject)=>{
        this._xhr_promise('GET', API.ANSWER_URL, null).then(
            (xhr: XMLHttpRequest)=>resolve(xhr.response.answer),
        );
      });
    }

    public async get_user_info(user: string): Promise<object> {
      return new Promise((resolve, reject)=>{
        let url = API.USER_URL;
        url = user ? url + '/' + user: url;
        this._xhr_promise('GET', url, null).then(
            (xhr: XMLHttpRequest)=>resolve(xhr.response),
        );
      });
    }
}
