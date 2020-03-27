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

    publicFunction(arg) {
        // do stuff
    }

    _privateFunction(args) {
        // not actually private just convention
    }
}