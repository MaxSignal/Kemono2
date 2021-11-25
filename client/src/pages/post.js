import { kemonoAPI } from "@wp/api";
import { addFavouritePost, removeFavouritePost, findFavouritePost } from "@wp/js/favorites";
import { LoadingIcon, registerMessage, showTooltip } from "@wp/components";
import { createComponent } from "@wp/js/component-factory";
import { isLoggedIn } from "@wp/js/account";

const meta = {
  service: null,
  user: null,
  postID: null,
};

/**
 * @param {HTMLElement} section
 */
export async function postPage(section) {
  /**
   * @type {HTMLElement}
   */
  const buttonPanel = section.querySelector(".post__actions");

  meta.service = document.head.querySelector("[name='service']").content;
  meta.user = document.head.querySelector("[name='user']").content;
  meta.postID = document.head.querySelector("[name='id']").content;
  const postBody = section.querySelector(".post__body");

  section.addEventListener('click', Expander);

  cleanupBody(postBody);
  await initButtons(buttonPanel);
}

/**
 * Apply some fixes to the content of the post.
 * @param {HTMLElement} postBody
 */
function cleanupBody(postBody) {
  const postContent = postBody.querySelector(".post__content");
  const isNoPostContent = !postContent || (!postContent.childElementCount && !postContent.childNodes.length);

  // content is empty
  if (isNoPostContent) {
    return;
  }

  // pixiv post
  if (meta.service === "fanbox") {
    // its contents is a text node
    if (!postContent.childElementCount && postContent.childNodes.length === 1) {
      // wrap the text node into `<pre>`
      const [textNode] = Array.from(postContent.childNodes);
      const pre = document.createElement("pre");
      textNode.after(pre);
      pre.appendChild(textNode);
    }

    // remove paragraphs with only `<br>` in them
    const paragraphs = postContent.querySelectorAll("p");
    paragraphs.forEach((para) => {
      if (para.childElementCount === 1 && para.firstElementChild.tagName === "BR" ) {
        para.remove();
      }
    });
  }

  Array.from(document.links).forEach((link) => {
    // remove links to fanbox from the post
    if (link.href.startsWith("https://downloads.fanbox.cc")) {
      link.remove();
    }
  });

  // Remove needless spaces and empty paragraphs.
  /**
   * @type {NodeListOf<HTMLParagraphElement}
   */
  const paragraphs = postContent.querySelectorAll("p:empty");
  Array.from(paragraphs).forEach((paragraph) => {
    if (paragraph.nextElementSibling && paragraph.nextElementSibling.tagName === "BR") {
      paragraph.nextElementSibling.remove();
      paragraph.remove();
    } else {
      paragraph.remove();
    }
  });
}

/**
 * @param {HTMLElement} buttonPanel
 */
async function initButtons(buttonPanel) {
  /**
   * @type {HTMLButtonElement}
   */
  const flagButton = buttonPanel.querySelector(".post__flag");
  /**
   * @type {HTMLButtonElement}
   */
  const favButton = createComponent("post__fav");
  const isFavorited = isLoggedIn && await findFavouritePost(meta.service, meta.user, meta.postID);

  if (isFavorited) {
    const [icon, text] = favButton.children;
    favButton.classList.add("post__fav--unfav");
    icon.textContent = "★";
    text.textContent = "Unfavorite";
  }

  if (!flagButton.classList.contains("post__flag--flagged")) {
    flagButton.addEventListener(
      "click",
      handleFlagging(
        meta.service,
        meta.user,
        meta.postID
      )
    );
  }

  favButton.addEventListener(
    "click",
    handleFavouriting(
      meta.service,
      meta.user,
      meta.postID
    )
  );

  buttonPanel.appendChild(favButton);
}

/**
 * @param {string} service
 * @param {string} user
 * @param {string} postID
 * @returns {(event: MouseEvent) => Promise<void>}
 */
function handleFlagging(service, user, postID) {
  return async (event) => {
    /**
     * @type {HTMLButtonElement}
     */
    const button = event.target;
    const [icon, text] = button.children;
    const loadingIcon = LoadingIcon();
    const isConfirmed = confirm('Are you sure you want to flag this post for reimport? Only do this if data in the post is broken/corrupted/incomplete.\nThis is not a deletion button.');

    button.classList.add("post__flag--loading");
    button.disabled = true;
    button.insertBefore(loadingIcon, text);


    try {
      if (isConfirmed) {
        const isFlagged = await kemonoAPI.posts.attemptFlag(service, user, postID);

        if (isFlagged) {
          const parent = button.parentElement;
          const newButton = createComponent("post__flag post__flag--flagged");

          parent.insertBefore(newButton, button);
          button.remove();
        }
      }

    } catch (error) {
      console.error(error);

    } finally {
      loadingIcon.remove();
      button.disabled = false;
      button.classList.remove("post__flag--loading");
    }
  }
}

/**
 * @param {string} service
 * @param {string} user
 * @param {string} postID
 * @returns {(event: MouseEvent) => Promise<void>}
 */
function handleFavouriting(service, user, postID) {
  return async (event) => {
    /**
     * @type {HTMLButtonElement}
     */
    const button = event.currentTarget;
    const isLoggedIn = localStorage.getItem("logged_in") === "yes";

    if (!isLoggedIn) {
      showTooltip(button, registerMessage(null, "Favorites"));
      return;
    }

    const [icon, text] = button.children;
    const loadingIcon = LoadingIcon();

    button.disabled = true;
    button.classList.add("post__fav--loading");
    button.insertBefore(loadingIcon, text);

    try {
      if (button.classList.contains("post__fav--unfav")) {
        const isUnfavorited = await removeFavouritePost(service, user, postID);

        if (isUnfavorited) {
          button.classList.remove("post__fav--unfav");
          icon.textContent = "☆";
          text.textContent = "Favorite";
        }

      } else {
        const isFavorited = await addFavouritePost(service, user, postID);

        if (isFavorited) {
          button.classList.add("post__fav--unfav");
          icon.textContent = "★";
          text.textContent = "Unfavorite";
        }
      }

    } catch (error) {
      console.error(error);

    } finally {
      loadingIcon.remove();
      button.disabled = false;
      button.classList.remove("post__fav--loading");
    }
  }
}

// expander.js
function Expand(c, t) {
  if (!c.naturalWidth) {
    return setTimeout(Expand, 10, c, t);
  }
  c.style.maxWidth = '100%';
  c.style.display = '';
  t.style.display = 'none';
  t.style.opacity = '';
};

/**
 * @param {MouseEvent} e
 */
function Expander(e) {
  /**
   * @type {HTMLElement}
   */
  var t = e.target;
  if (t.parentNode.classList.contains('fileThumb')) {
    e.preventDefault();
    if (t.hasAttribute('data-src')) {
      var c = document.createElement('img');
      c.setAttribute('src', t.parentNode.getAttribute('href'));
      c.style.display = 'none';
      t.parentNode.insertBefore(c, t.nextElementSibling);
      t.style.opacity = '0.75';
      setTimeout(Expand, 10, c, t);
    } else {
      var a = t.parentNode;
      a.firstChild.style.display = '';
      a.removeChild(t);
      a.offsetTop < window.pageYOffset && a.scrollIntoView({ top: 0, behavior: 'smooth' });
    }
  }
};
