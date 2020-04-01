export default class TimeoutException extends Error {
    private timeoutMS: number;

    constructor(m: string, timeoutMS: number) {
      super(m);
      Object.setPrototypeOf(this, TimeoutException.prototype);
      this.timeoutMS = timeoutMS;
    }

    public getTimeoutMS(): number {
      return this.timeoutMS;
    }
}
