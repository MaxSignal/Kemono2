import { favorites } from "./favorites";
import { posts } from "./posts";
import { api } from "./api";

export { fetchArtists } from "./fetch-artists.js";
/**
 * @type {KemonoAPI}
 */
export const kemonoAPI = {
  favorites,
  posts,
  api
};
