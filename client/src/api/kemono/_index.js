import { favorites } from "./favorites";
import { posts } from "./posts";
import { api } from "./api";

export { fetchArtists } from "./fetch-artists.js";
export { banArtist, unbanArtist, fetchBannedArtists, fetchAllBannedArtists } from "./artists.js";
export { fetchAccountInfo } from "./account.js";

/**
 * @type {KemonoAPI}
 */
export const kemonoAPI = {
  favorites,
  posts,
  api
};
