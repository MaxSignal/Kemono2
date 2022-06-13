import { KemonoError } from "./base.js";

const errorList = {
  0: "Could not connect to server.",
  1: "Could not favorite post.",
  2: "Could not unfavorite post.",
  3: "Could not favorite artist.",
  4: "Could not unfavorite artist.",
  5: "There might already be a flag here.",
  6: "Could not retrieve the list of bans.",
  7: "Could not retrieve banned artist.",
  8: "Could not retrieve artists.",
  9: "Could not retrieve import logs.",
  10: "Could not ban artist.",
  11: "Could not unban artist.",
  12: "Could not get account info."
};

export class KemonoAPIError extends KemonoError {
  /**
   * @param {number} code
   */
  constructor(code) {
    super();
    this.code = String(code).padStart(3, "0");
    this.message = `${this.code}: ${errorList[code]}`;
  }
}
