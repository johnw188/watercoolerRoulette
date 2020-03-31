export default class WebRTCConnection {
    constructor() {
        const configuration = {
            iceServers: [{
                urls: 'stun:stun.l.google.com:19302'
            }]
        };
        this._offer = null
        this._answer = null
        this._offerListener = function(offer) {}
        this._answerListener = function(answer) {}
        this._isOfferer = true
        this._remoteStreamListener = function(event) {}
        this._offerPeerConnection = new RTCPeerConnection(configuration)
        this._offerPeerConnection.onicecandidate = (event) => {
            if (event.candidate == null) {
                this.offer = this._offerPeerConnection.localDescription
            }
        }
        this._offerPeerConnection.ontrack = (event) => {
            this._remoteStreamListener(event)
        }

        this._answerPeerConnection = new RTCPeerConnection(configuration)
        this._answerPeerConnection.onicecandidate = (event) => {
            if (event.candidate == null) {
                this.answer = this._answerPeerConnection.localDescription
            }
        }
        this._answerPeerConnection.ontrack = (event) => {
            this._remoteStreamListener(event)
        }
    }

    get peerConnection() {
        if (this._isOfferer) {
            return this._offerPeerConnection
        } else {
            return this._answerPeerConnection
        }
    }

    get offerListener() {
        return this._offerListener
    }

    set offerListener(listener) {
        this._offerListener = listener
    }

    get answerListener() {
        return this._answerListener
    }

    set answerListener(listener) {
        this._answerListener = listener
    }

    get offer() {
        return this._offer
    }

    set offer(offer) {
        this._offer = offer
        this._offerListener(offer)
    }

    get answer() {
        return this._answer
    }

    set answer(answer) {
        this._answer = answer
        this._answerListener(answer)
    }

    set remoteStreamListener(remoteStreamListener) {
        this._remoteStreamListener = remoteStreamListener
    }

    createOffer() {
        this._offerDC = this._offerPeerConnection.createDataChannel('test-wcr', {reliable: true})
        this._offerPeerConnection.createOffer().then((desc) => {
            this._offerPeerConnection.setLocalDescription(desc)
        })
    }

    // Accept an answer to our offer
    acceptAnswer(answer) {
        let answerDescription = new RTCSessionDescription(answer)
        this._offerPeerConnection.setRemoteDescription(answerDescription)
    }

    _disableOfferStream() {

    }

    answerOffer(offer) {
        this._isOfferer = false
        let offerDescription = new RTCSessionDescription(offer)
        this._answerPeerConnection.setRemoteDescription(offerDescription)
        this._answerPeerConnection.createAnswer().then((desc) => {
            return this._offerPeerConnection.setLocalDescription(desc)
        }).then(() => {})
    }

}
