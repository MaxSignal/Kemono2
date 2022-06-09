import { createComponent } from "@wp/js/component-factory.js";

/**
 * @typedef {Partial<HTMLButtonElement>} IButtonProps
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
