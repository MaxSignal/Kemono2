import { createComponent } from "@wp/js/component-factory";

/**
 * @param {HTMLElement} element
 * @param {string} url
 * @param {string} text
 * @param {boolean} isNoop
 * @param {string} className
 */
export function FancyLink(
  element = null,
  url,
  text = url,
  isNoop = true,
  className = undefined
) {
  /**
   * @type {HTMLAnchorElement}
   */
  const fancyLink = element
    ? initFromElement(element)
    : initFromScratch(url, text, isNoop, className);

  return fancyLink;
}

/**
 * @param {HTMLAnchorElement}
 */
function initFromElement(element) {
  return element;
}

/**
 * @param {string} url
 * @param {string} text
 * @param {boolean} isNoop
 * @param {string} className
 * @returns
 */
function initFromScratch(url, text, isNoop, className) {
  /**
   * @type {HTMLAnchorElement}
   */
  const fancyLink = createComponent("fancy-link");

  fancyLink.href = url;
  fancyLink.textContent = text;

  if (className) {
    fancyLink.classList.add(className);
  }

  if (isNoop) {
    fancyLink.target = "_blank";
    fancyLink.rel = "noopener noreferrer";
  }

  return fancyLink;
}

/**
 * @typedef AntiscraperLinkProps
 * @property {string} url
 * @property {string} [text]
 */

/**
 * @param {AntiscraperLinkProps} props
 */
export function AntiscraperLink({ url, text = url }) {
  const anchour = document.createElement("a");
  const endURL = new URL(KEMONO_SITE);

  endURL.pathname = "/antiscraper";
  endURL.searchParams.set("antiscraper-url", url);
  anchour.className = "fancy-link fancy-link--antiscraper";
  anchour.href = endURL.toString();
  anchour.textContent = text;

  return anchour;
}
