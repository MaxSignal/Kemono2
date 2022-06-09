import { IS_DEVELOPMENT } from "@wp/env/derived-vars.js";

export const paysiteList = [
  "patreon",
  "fanbox",
  "gumroad",
  "subscribestar",
  "dlsite",
  "discord",
  "fantia",
  IS_DEVELOPMENT && "kemono-dev"
];

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
      profile: (userID) => `https://fantia.jp/fanclubs/${userID}`
    },
    post: {}
  },
};

if (IS_DEVELOPMENT) {
  paysites["kemono-dev"] = {
    title: "Kemono Dev",
    user: {
      profile: (artistID) => `/artist/${artistID}`
    },
    post: {}
  };
}
