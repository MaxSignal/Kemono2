import { createComponent } from "@wp/js/component-factory";
import { ImageLink, FancyLink, Timestamp } from "@wp/components";
import { freesites, paysites } from "@wp/utils";

/**
 * @param {HTMLElement} element
 * @param {KemonoAPI.Post} post
 */
export function PostCard(element = null, post = {}) {
  const postCard = element
    ? initFromElement(element)
    : initFromScratch(post);

  const view = postCard.postCardElement.querySelector(".post-card__view");

  if (view) {
    /**
     * @type {HTMLButtonElement}
     */
    const button = view.querySelector(".post-card__button");
    /**
     * @type {HTMLAnchorElement}
     */
    const link = postCard.postCardElement.querySelector(".post-card__link");

    button.addEventListener("click", handlePostView(link));
  }

  return postCard;
};

/**
 * @param {HTMLElement} element
 */
function initFromElement(element) {
  const { id, service, user } = element.dataset;
  return {
    postCardElement: element,
    postID: id,
    service,
    userID: user
  }
}

/**
 * @param {KemonoAPI.Post} post
 */
function initFromScratch(post) {
  /**
   * @type {HTMLElement}
   */
  const postCardElement = createComponent("post-card");

  return {
    postCardElement,
    postID: post.id,
    service: post.service,
    userID: post.user
  }
}

/**
 * @param {HTMLAnchorElement} link
 * @returns {(event: MouseEvent) => void}
 */
function handlePostView(link) {
  return (event) => {
    link.focus();
  }
}

/**
 * @param {HTMLElement | null} element
 * @param {KemonoAPI.Artist} user
 * @param {boolean} isCount
 * @param {boolean} isDate
 * @param {string} className
 */
export function UserCard(
  element,
  user = {},
  isCount = false,
  isDate = false,
  className=null
) {
  const userCard = element
    ? initUserCardFromElement(element)
    : initUserCardFromScratch(user, isCount, isDate, className);

  return userCard;
}

/**
 * @param {HTMLElement} element
 */
function initUserCardFromElement(element) {
  const userCard = element;

  return userCard;
}

/**
 * @param {KemonoAPI.Artist} user
 * @param {boolean} isCount
 * @param {boolean} isDate
 * @param {string} className
 */
function initUserCardFromScratch(user, isCount, isDate, className) {
  const profileIcon = freesites.kemono.user.icon(user.service, user.id)
  const profileLink = freesites.kemono.user.profile(user.service, user.id);
  /**
   * @type {HTMLElement}
   */
  const userCard = createComponent("user-card");
  const imageLink = ImageLink(null,
    profileLink,
    profileIcon,
    "",
    profileIcon,
    true,
    true,
    'user-card__user-icon'
  );
  const fancyLink = FancyLink(null,
    profileLink,
    user.name
  );
  const userIcon = userCard.querySelector(".user-card__icon");
  const userName = userCard.querySelector(".user-card__name");
  const userService = userCard.querySelector(".user-card__service");
  const userCount = userCard.querySelector(".user-card__count");
  const userUpdated = userCard.querySelector(".user-card__updated");

  userIcon.appendChild(imageLink);
  userName.appendChild(fancyLink);
  userService.textContent = paysites[user.service].title;


  if (className) {
    userCard.classList.add(className);
  }

  if (isCount) {
    userCount.textContent = user.count
  } else {
    userCount.remove();
  }

  if (isDate) {
    const timestamp = Timestamp(null, user.updated);
    userUpdated.appendChild(timestamp);
  } else {
    userUpdated.remove();
  }

  return userCard;
}
