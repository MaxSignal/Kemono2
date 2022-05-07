export { KemonoError, KemonoAPIError, KemonoValidationError } from "./kemono-error/_index.js";

const defaultDelay = parseInt(document.documentElement.style.getPropertyValue("--duration-global"));

/**
 * @param {string} name
 * @param {string} url
 * @returns
 */
function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[[]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
  var results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

/**
 * @param {() => void} func
 * @param {number} wait
 * @param {boolean} immediate
 * @returns {void}
 */
function debounce(func, wait, immediate) {
  let timeout;
  return function () {
    var context = this;
    var args = arguments;
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);

    function later() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    }
  };
}

/**
 * @param {number} time
 * @returns
 */
export function setTimeoutAsync(time = defaultDelay) {
  const timeOut = new Promise((resolve) => {
    setTimeout(resolve, time);
  });
  return timeOut;
}

/**
 * Iterate over the list of images
 * and add `image_link` class
 * if they are a descendant of an `a` element
 * and don't have that class already.
 * @param {HTMLImageElement[] | HTMLCollectionOf<HTMLImageElement>} imageElements
 */
export function fixImageLinks(imageElements) {
  const images = Array.from(imageElements);

  images.forEach((image) => {
    const link = image.closest("a");

    if (
      link
      // && !image.nextSibling
      // && !image.previousSibling
      // TODO: fix this later
      && !link.classList.contains("user-header__profile")
      && !link.classList.contains("image-link")
    ) {
      link.classList.add("image-link");
    }
  });
};

export const paysiteList = [
  "patreon",
  "fanbox",
  "gumroad",
  "subscribestar",
  "dlsite",
  "discord",
  "fantia"
]

/**
 * @type {{[paysite:string]: {title: string, user: { profile: (userID: string) => string }, post: {}}}}
 */
export const paysites = {
  patreon: {
    title: "Patreon",
    user: {
      profile: (userID) => `https://www.patreon.com/user?u=${userID}`
    },
    post: {}
  },
  fanbox: {
    title: "Pixiv Fanbox",
    user: {
      profile: (userID) => `https://www.pixiv.net/fanbox/creator/${userID}`
    },
    post: {}
  },
  subscribestar: {
    title: "SubscribeStar",
    user: {
      profile: (userID) => `https://subscribestar.adult/${userID}`
    },
    post: {}
  },
  gumroad: {
    title: "Gumroad",
    user: {
      profile: (userID) => `https://gumroad.com/${userID}`
    },
    post: {}
  },
  discord: {
    title: "Discord",
    user: {
      profile: (userID) => ``
    },
    post: {}
  },
  dlsite: {
    title: "DLsite",
    user: {
      profile: (userID) => `https://www.dlsite.com/eng/circle/profile/=/maker_id/${userID}`
    },
    post: {}
  },
  fantia: {
    title: "Fantia",
    user: {
      profile: (userID) => `user_id: f"https://fantia.jp/fanclubs/${userID}`
    },
    post: {}
  },
};

export const freesites = {
  kemono: {
    title: "Kemono",
    user: {
      /**
       * @param {string} service
       * @param {string} artistID
       */
      profile: (service, artistID) => `/${service}/${service === 'discord' ? 'server' : 'user'}/${artistID}`,
      /**
       * @param {string} service
       * @param {string} artistID
       */
      icon: (service, artistID) => `/icons/${service}/${artistID}`,
    },
    post: {
      /**
       * @param {string} service
       * @param {string} userID
       * @param {string} postID
       * @returns
       */
      link: (service, userID, postID) => `/${service}/user/${userID}/post/${postID}`
    }

  }
}

/**
 * @param {number} time
 */
export function waitAsync(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

/**
 * @param {string} str
 */
export function isLowerCase(str) {
  return Boolean(str.match(/[0-9a-z]+/i))
}
