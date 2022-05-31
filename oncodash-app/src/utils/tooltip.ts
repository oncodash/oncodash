// Adapted from:
// https://github.com/genome-spy/genome-spy/blob/master/packages/core/src/utils/ui/tooltip.js
import { html, render, TemplateResult } from "lit";

export const SUPPRESS_TOOLTIP_CLASS_NAME = "gs-suppress-tooltip";

/**
 * Converts a datum to tooltip (HTMLElement or lit's TemplateResult).
 */
export type TooltipHandler = (
    datum: Record<string, any>
) => Promise<string | TemplateResult | HTMLElement>;

export default class Tooltip {
    private container: HTMLElement;
    private element: HTMLDivElement;
    private _visible: boolean;
    private _previousTooltipDatum: any;
    private enabledStack: boolean[];
    private _penaltyUntil: number;
    private _lastCoords: [number, number];
    private _previousMove: number;
    private mouseCoords: [number, number];
    private _usePenalty: boolean;

    constructor(container: HTMLElement, usePenalty = false) {
        this.container = container;
        this._usePenalty = usePenalty;

        this.element = document.createElement("div");
        this.element.className = "tooltip";
        this.element.style.position = "absolute";
        this._visible = true;
        this.container.appendChild(this.element);

        this._previousTooltipDatum = undefined;

        this.enabledStack = [true];

        this._penaltyUntil = 0;
        this._lastCoords = [0, 0];
        this.mouseCoords = [0, 0];

        this._previousMove = 0;

        this.clear();

        this.container.addEventListener("mousemove", (event) =>
            this.handleMouseMove(event)
        );
    }

    set visible(visible: boolean) {
        if (visible != this._visible) {
            this.element.style.display = visible ? "block" : "none";
            this._visible = visible;
        }
    }

    get visible() {
        return this._visible;
    }

    get enabled() {
        return this.enabledStack.at(-1) ?? true;
    }

    pushEnabledState(enabled: boolean) {
        this.enabledStack.push(enabled);
        if (!enabled) {
            this.visible = false;
        }
    }

    popEnabledState() {
        this.enabledStack.pop();
    }

    handleMouseMove(mouseEvent: MouseEvent) {
        this.mouseCoords = clientPoint(this.container, mouseEvent);

        const now = performance.now();

        // Prevent the tooltip from flashing briefly before it becomes penalized
        // because of a quickly moving mouse pointer
        if (this._usePenalty) {
            if (
                !this.visible &&
                !this._isPenalty() &&
                now - this._previousMove > 500
            ) {
                this._penaltyUntil = now + 70;
            }

            // Disable the tooltip for a while if the mouse is being moved very quickly.
            // Makes the tooltip less annoying.
            // TODO: Should calculate speed: pixels per millisecond or something
            if (
                this._lastCoords &&
                distance(this.mouseCoords, this._lastCoords) > 20
            ) {
                this._penaltyUntil = now + 400;
            }
        }

        this._lastCoords = this.mouseCoords;

        if (this.visible) {
            this.updatePlacement();
        }

        this._previousMove = now;
    }

    updatePlacement() {
        /** Space between pointer and tooltip box */
        const spacing = 20;

        const [mouseX, mouseY] = this.mouseCoords;

        let x = mouseX + spacing;
        if (x > this.container.clientWidth - this.element.offsetWidth) {
            x = mouseX - spacing - this.element.offsetWidth;
        }
        this.element.style.left = x + "px";

        this.element.style.top =
            Math.min(
                mouseY + spacing,
                this.container.clientHeight - this.element.offsetHeight
            ) + "px";
    }

    setContent(content: string | TemplateResult | HTMLElement | undefined) {
        if (!content || !this.enabled || this._isPenalty()) {
            if (this.visible) {
                render("", this.element);
                this.visible = false;
            }
            this._previousTooltipDatum = undefined;
            return;
        }

        render(content, this.element);

        this.visible = true;

        this.updatePlacement();
    }

    clear() {
        this._previousTooltipDatum = undefined;
        this.setContent(undefined);
    }

    /**
     * Updates the tooltip if the provided datum differs from the previous one.
     * Otherwise this is nop.
     */
    updateWithDatum<T>(datum: T, converter?: TooltipHandler) {
        if (datum !== this._previousTooltipDatum) {
            this._previousTooltipDatum = datum;
            if (!converter) {
                converter = (d) =>
                    Promise.resolve(html` ${JSON.stringify(d)} `);
            }

            converter(datum)
                .then((result) => this.setContent(result))
                .catch((error) => {
                    if (error !== "debounced") {
                        throw error;
                    }
                });
        }
    }

    private _isPenalty() {
        return this._penaltyUntil && this._penaltyUntil > performance.now();
    }
}

/**
 * Calculate euclidean distance
 *
 * @param {number[]} a
 * @param {number[]} b
 */
function distance(a: number[], b: number[]): number {
    let sum = 0;
    for (let i = 0; i < a.length; i++) {
        sum += (a[i] - b[i]) ** 2;
    }
    return Math.sqrt(sum);
}

/**
 * Get mouse coordinates.
 * Adapted from: https://github.com/d3/d3-selection/blob/master/src/point.js
 *
 * @param {HTMLElement} node
 * @param {MouseEvent} event
 * @returns {[number, number]}
 */
function clientPoint(node: HTMLElement, event: MouseEvent): [number, number] {
    const rect = node.getBoundingClientRect();
    return [
        event.clientX - rect.left - node.clientLeft,
        event.clientY - rect.top - node.clientTop,
    ];
}

/*
 * Default data handler for the tooltip. Formats the object into an html-table.
 */
export async function dataTooltipHandler<T>(datum: T) {
    const table = html`
        <table>
            ${Object.entries(datum)
                .filter(([key, value]) => !key.startsWith("_"))
                .map(
                    ([key, value]) => html`
                        <tr>
                            <th>${key}</th>
                            <td>${value}</td>
                        </tr>
                    `
                )}
        </table>
    `;

    return html`${table}`;
}
