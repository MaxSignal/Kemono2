import { kemonoFetch } from "./kemono-fetch";
import { KemonoError } from "@wp/utils";


export const posts = {
  attemptFlag
};

/**
 * @param {string} service
 * @param {string} user
 * @param {string} post_id
 */
async function attemptFlag(service, user, post_id) {
  try {
    const response = await kemonoFetch(`/api/${service}/user/${user}/post/${post_id}/flag`, { method: "POST" });

    if (!response || !response.ok) {

      alert(new KemonoError(5));
      return false;
    }

    return true;

  } catch (error) {
    console.error(error);
  }
}