import { initShell } from "@wp/components";
import { initComponentFactory } from "./component-factory";

/**
 * Initialises the scripts on the page.
 * @param {Map<string, (section: HTMLElement) => void>} pages The map of page names and their callbacks.
 */
export function initSections(pages) {
  const sidebar = document.querySelector(".global-sidebar");
  const main = document.querySelector("main");
  /**
   * @type {HTMLElement}
   */
  const footer = document.querySelector(".global-footer");
  /**
   * @type {NodeListOf<HTMLElement>}
   */
  const sections = main.querySelectorAll("main > .site-section");

  initComponentFactory(footer);
  initShell(sidebar);
  sections.forEach(section => {
    const sectionName = /site-section--([a-z\-]+)/i.exec(section.className)[1];

    if (pages.has(sectionName)) {
      const sectionCallback = pages.get(sectionName);
      sectionCallback(section);
    }
  });

}
