class webrtcConnection {
    constructor() {
        const configuration = {
            iceServers: [{
                urls: 'stun:stun.l.google.com:19302'
            }]
        };
        let pc = new RTCPeerConnection(configuration)
    }
}
