export default class API {
    public static MATCH_URL = 'https://api.watercooler.express/match';
    public static ANSWER_URL = 'https://api.watercooler.express/answer';
    public static USER_URL = 'https://api.watercooler.express/answer';


    constructor() {

    }

    private async _xhr_promise(method: string, url: string, data: object): Promise<XMLHttpRequest> {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.addEventListener("load", (e) => {
                console.log('Loaded: ' + xhr.status);
                console.log(xhr.response);
                console.log();
                if (xhr.status == 200) {
                    // If successful
                    resolve(xhr);
                } else {
                    reject(xhr)
                };
            });

            xhr.open(method, url);
            xhr.withCredentials = true;
            xhr.responseType = "json"
            xhr.send(JSON.stringify(data));
        });
    }

    private async _match(offer: object): Promise<string> {
        return new Promise((resolve, reject)=>{
            var xhr_promise: Promise<XMLHttpRequest> = this._xhr_promise("POST", API.MATCH_URL, {offer: offer});

            xhr_promise.then((xhr)=>resolve(xhr.response.match_id));
            xhr_promise.catch((xhr)=>{
                if (xhr.status == 408) {
                    console.log("Timeout during matching")
                    reject({timeout_ms: xhr.response.timeout_ms})
                } else {
                    console.log("Unhandled fail :(")
                    // If failed
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText,
                        response: xhr.response
                    });
                }
            });
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
                    console.log("Wait timeout updated to " + wait_ms.toString());
                }
            }
        }
    }

    public async post_answer(answer: object): Promise<void>{
        this._xhr_promise("POST", API.ANSWER_URL, {answer: answer});
    }

    public async get_answer(): Promise<object> {
        return new Promise((resolve, reject)=>{
            this._xhr_promise("GET", API.ANSWER_URL, null).then(
                    (xhr: XMLHttpRequest)=>resolve(xhr.response.answer)
            )
        });
    }

    public async get_user_info(user: string): Promise<object> {
        return new Promise((resolve, reject)=>{
            var url = API.USER_URL
            url = user ? url + "/" + user: url;
            this._xhr_promise("GET", url, null).then(
                    (xhr: XMLHttpRequest)=>resolve(xhr.response)
            );
        });
    }
}
