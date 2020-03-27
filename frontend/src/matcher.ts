import WebRTCConnection from './webrtcConnect.js'

export default class API {
    public static MATCH_URL = 'https://api.watercooler.express/match';

    constructor() {
    }

    private async _match(offer: object): Promise<string> {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.addEventListener("load", (e) => {
                console.log('Loaded: ' + xhr.status);
                console.log(xhr.response);
                console.log();
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

            xhr.open("POST", API.MATCH_URL);
            xhr.withCredentials = true;
            xhr.responseType = "json"
            xhr.send(JSON.stringify({offer: offer}));
        });
    }

    private wait(timeout_ms: number): Promise<void> {
        return new Promise((resolve, reject)=>{
            setTimeout(()=>resolve(), timeout_ms)
        })
    }

    // Return a promise that completes on match
    public async match(offer: object): Promise<string> {
        while(true){
            var wait_ms : number = 0;
            try{
                await this.wait(wait_ms);
                return await this._match(offer);
            } catch(e) {
                if(e.timeout_ms){
                    wait_ms = e.timeout_ms;
                    console.log("Wait timeout updated to " + wait_ms.toString())
                }
            }
        }
    }
}