import WebRTCConnection from './webrtcConnect.js'

export default class Matcher {
    public static MATCH_URL = 'https://api.watercooler.express/match';

    constructor() {
    }

    private async _match(offer: object): Promise<string> {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.addEventListener("load", (e) => {
                console.log('Loaded: ' + xhr.status);
                console.log(xhr.response);

                if (xhr.status == 200) {
                    // If successful
                    resolve(xhr.response);
                } else if (xhr.status == 408) {
                    console.log("Timeout during matching")
                    reject({timeout_ms: xhr.response.timeout_ms})
                } else {
                    console.log("Unhandled fail :(")
                    // If failed
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText
                    });
                };
            });

            xhr.open("POST", Matcher.MATCH_URL);
            xhr.withCredentials = true;
            xhr.send(JSON.stringify({offer: offer}));
        });
    }

    private callDeferred<T>(timeout_ms: number, call: ()=> T): Promise<T> {

        return new Promise((resolve, reject)=>{
            setTimeout(()=>{
                resolve(call())
            }, timeout_ms)
        })
    }

    // Return a promise that completes on match
    public async match(offer: object): Promise<string> {
        while(true){
            try{
                return await this._match(offer);
            } catch(e) {
                console.log(e)
            }
        }
        return this._match(offer);
    }
}