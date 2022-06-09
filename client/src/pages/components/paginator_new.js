import { createComponent } from "@wp/js/component-factory.js";
import { Button } from "@wp/components";

/**
 * @typedef IPaginatorClientProps
 * @property { import("api/kemono/api.js").IPagination } pagination
 * @property {(page: number) => void} onPageChange
 */

/**
 * This paginator is rendered client-only,
 * therefore no need for initialization
 * off a DOM element.
 * @param {IPaginatorClientProps} props
 */
export function PaginatorClient({ pagination, onPageChange }) {
  const { current_page, limit, total_count, total_pages } = pagination;
  const isFirstPage = current_page === 1;
  const isLastPage = current_page === total_pages;
  const currentMin = (current_page - 1) * limit;
  const currentMax = isLastPage ? total_count : currentMin + limit;
  const info = `${currentMin}-${currentMax} out of ${total_count}`;

  /**
   * @type {HTMLDivElement}
   */
  const component = createComponent("paginator-client");
  /**
   * @type {HTMLParagraphElement}
   */
  const infoElement = component.querySelector(".paginator-client__info");
  /**
   * @type {HTMLUListElement}
   */
  const pages = component.querySelector(".paginator-client__pages");
  /**
   * @type {HTMLLIElement[]}
   */
  const [first, prev, current, next, last] = Array.from(pages.children);

  infoElement.textContent = info;

  if (isFirstPage) {
    first.textContent = String(1);
  } else {
    const button = Button({
      textContent: String(1),
      value: String(1)
    });
    first.appendChild(button);
  }

  if (current_page - 1 > 1) {
    const button = Button({
      textContent: String(current_page - 1),
      value: String(current_page - 1)
    });
    prev.appendChild(button);
  } else {
    prev.textContent = "...";
  }

  current.appendChild(
    SelectedPage({ pagination, onPageChange })
  );

  if (current_page + 1 < total_pages) {
    const button = Button({
      textContent: String(current_page + 1),
      value: String(current_page + 1)
    });
    next.appendChild(button);
  } else {
    next.textContent = "...";
  }

  if (isLastPage) {
    last.textContent = String(total_pages);
  } else {
    const button = Button({
      textContent: String(total_pages),
      value: String(total_pages)
    });
    last.appendChild(button);
  }

  // doing it this way to avoid memory leaks
  component.onclick = handlePageChange;

  /**
   * @param {MouseEvent} event
   */
  function handlePageChange(event) {
    event.stopPropagation();
    /**
     * @type {HTMLButtonElement}
     */
    const button = event.target;
    const isButton = button.tagName === "BUTTON" && button.classList.contains("button");

    if (!isButton) {
      return;
    }

    const newPage = Number(button.value);

    if (newPage === current_page) {
      return;
    }

    onPageChange(newPage);
  }

  return component;
}

/**
 * @typedef {IPaginatorClientProps}ISelectedPageProps
 *
 */

/**
 * @param {ISelectedPageProps} props
 */
function SelectedPage({ pagination, onPageChange }) {
  const { current_page, total_pages } = pagination;
  /**
   * @type {HTMLFormElement}
   */
  const component = createComponent("form paginator-client__selected-page");
  /**
   * @type {[HTMLLabelElement, HTMLButtonElement, HTMLButtonElement]}
   */
  const [label, subtract, increase] = Array.from(component.children).map(
    (section) => section.firstElementChild
  );
  /**
   * @type {HTMLInputElement}
   */
  const selected = label.nextElementSibling;
  const maxNumberLength = String(total_pages).length;

  // ensure the width doesn't change between page switches
  // but also can fit the max possible value
  component.style.setProperty("--local-width", `${maxNumberLength + 2}em`);
  selected.min = "1";
  selected.max = String(total_pages);
  selected.step = "1";
  selected.value = String(current_page);

  subtract.onclick = () => {
    selected.stepDown();
  };

  increase.onclick = () => {
    selected.stepUp();
  };

  component.onclick = (event) => {
    event.stopPropagation();
  };

  component.onsubmit = (event) => {
    event.preventDefault();
    /**
     * @type {HTMLFormElement}
     */
    const form = event.target;
    /**
     * @type {HTMLInputElement}
     */
    const input = form.elements["selected_page"];
    const selectedPage = Number(input.value);

    if (selectedPage === pagination.current_page) {
      return;
    }

    onPageChange(selectedPage);
  };

  return component;
}
