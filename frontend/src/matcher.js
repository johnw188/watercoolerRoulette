import WebRTCConnection from './webrtcConnect.js'

export default class Matcher {
    constructor() {
        this._privateVar = "lol string"
        this._connection = new WebRTCConnection()
        
    }

    get privateVar() {
        return this._privateVar
    }
    
    set privateVar(value) {
        this._privateVar = value
    }


    _match(offer){
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const url='https://api.watercooler.express/match';

            xhr.addEventListener("load", (e) => {
                console.log('LOADING: ', xhr.status);
                console.log(xhr.response);
                if(xhr.response.ok){
                    resolve(xhr.response);
                } else {
                    reject(xhr.response.timeout_ms);
                }
            });

            xhr.open("POST", url);
            xhr.withCredentials = true;
            xhr.send(JSON.stringify({offer: offer}));
        });
    }

    // Return a promise that completes on match
    match(offer) {
        var _this = this;
        var retryDeferred = function(timeout_ms) {
            console.log(timeout_ms)
            return new Promise((resolve, reject) => {
                setTimeout(()=>{
                        console.log("I was here");
                        _this._match(offer).then(resolve, retryDeferred);
                    },
                    timeout_ms
                )});
        };
        return retryDeferred(0);
    }

    _privateFunction(args) {
        // not actually private just convention
    }
}