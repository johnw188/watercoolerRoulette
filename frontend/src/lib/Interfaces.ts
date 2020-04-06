export interface OfferIce {
    offer: RTCSessionDescriptionInit;
    ice: Array<RTCIceCandidate>;
}

export interface AnswerIce {
    answer: RTCSessionDescriptionInit;
    ice: Array<RTCIceCandidate>;
}

export interface StreamPair{
    local: MediaStream;
    remote: MediaStream;
  }
