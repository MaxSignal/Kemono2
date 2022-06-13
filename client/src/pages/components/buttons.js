import { isAdministrator, isLoggedIn } from "@wp/lib/account.js";
import { createComponent } from "@wp/js/component-factory.js";
import { banArtist, unbanArtist } from "@wp/api";
import { isArtistBanned } from "@wp/lib";

/**
 * @typedef {Partial<HTMLButtonElement> & { element?: HTMLButtonElement }} IButtonProps
 */

/**
 * @param {IButtonProps} props
 */
export function Button({ ...buttonProps }) {
  /**
   * @type {HTMLButtonElement}
   */
  const component = createComponent("button");

  Object.assign(component, buttonProps);

  return component;
}

/**
 * @param {IButtonProps} props
 */
export async function ButtonArtistBan({ element }) {
  const isAdmin = await isAdministrator();

  if (!isAdmin) {
    return element;
  }

  const { service, artistId } = element.dataset;

  const isBanned = await isArtistBanned(artistId, service);

  element.classList.add(
    isBanned
      ? "artist-ban--unban"
      : "artist-ban--ban"
  );

  element.addEventListener("click", async (event) => {
    if (element.classList.contains("artist-ban--ban")) {
      await banArtist(artistId, service);
      element.classList.toggle("artist-ban--ban");
      element.classList.toggle("artist-ban--unban");
      return;
    }

    await unbanArtist(artistId, service);
    element.classList.toggle("artist-ban--unban");
    element.classList.toggle("artist-ban--ban");
  });

  return element;
}
