import {
    LitElement,
    css,
    svg,
    html,
    TemplateResult,
    SVGTemplateResult,
} from "lit";
import { customElement } from "lit/decorators.js";
import { classMap } from "lit/directives/class-map.js";
import {
    Link,
    Node,
    NodeLink,
    DAGNode,
    nodeLinkToDAG,
    traverseNodes,
} from "./graph_utils";
import Tooltip from "../utils/tooltip";
import { dataTooltipHandler } from "../utils/tooltip";

interface Coords {
    x: number;
    y: number;
}

interface BoxBound {
    left: Coords;
    right: Coords;
}

interface BoxBounds {
    [index: string]: BoxBound;
}

type Column = { vals: string[]; colname: string }[];
type ColumnLinks = Record<string, { links: Link[]; bound: BoxBounds }>;

/**
 * Lit Element, responsible for rendering the network visualization and
 * fetching the node-link data from the API.
 */
@customElement("oncodash-explainer")
class ExplainerView extends LitElement {
    private dag: Map<string, DAGNode> = new Map();
    private highlightedNodePaths: Set<Node> = new Set();
    private highlightedLinks: Set<Link> = new Set();
    private tooltip: Tooltip = new Tooltip(document.body);

    /**
     * @param graph
     * @param {number} [svgWidth=1024] - Width of the svg canvas.
     * @param {number} [svgHeight=480] - Width of the svg canvas.
     * @param {number} [boxHeight=16] - Width of the svg canvas.
     */
    constructor(
        private graph?: NodeLink,
        private svgWidth: number = 1024,
        private svgHeight: number = 480,
        private boxHeight: number = 16
    ) {
        super();
    }

    static styles = css`
        :host {
            position: relative;
        }

        .explainerview-canvas {
            fill: white;
        }

        .label-group:hover .labelbox {
            stroke: #0055d4;
            stroke-width: 2.5px;
        }

        .labelbox {
            fill: #f2f2f2;
            rx: 0.5em;
            ry: 0.5em;
            stroke: black;
            stroke-width: 1px;
            transition: stroke 0.15s, stroke-width 0.15s;
        }

        .label-text {
            color: black;
            font-size: 1ex;
            text-anchor: middle;
            text-align: center;
        }

        .column-label {
            color: black;
            font-size: 1ex;
            font-style: italic;
            text-anchor: middle;
            text-align: center;
        }

        .column-line {
            stroke: #ccc;
            stroke-width: 0.5px;
        }

        .link {
            stroke-width: 1px;
            fill: #0055d4;
            transition: fill 0.15s;
        }

        .link.active {
            fill: firebrick;
        }

        .link-group:hover .link {
            stroke: #0055d4;
            stroke-width: 2.5px;
        }
    `;

    /**
     * Draws the <svg> nodes and links from the input data.
     * @param {NodeLink} graphData - Input graph in node-link-format.
     * @returns {SVGTemplateResult[]} - An array containing <svg>-elems for nodes and links.
     */
    private addSvgNodesAndLinks(graphData: NodeLink): SVGTemplateResult[] {
        // Compute widths for the node columns
        const colData = _getColNodeData(graphData);
        const colWidth = this.svgWidth / Object.keys(colData).length;
        const boxWidth = colWidth / 2;

        // draw the columns of the network
        const linkData: ColumnLinks = {};
        const nodeSvgData: TemplateResult[] = [];
        for (const i of Object.keys(colData)) {
            // compute x-coords for the column start and for the column-label and line
            const colX = (+i - 1 + 0.25) * colWidth;
            const labX = colX + boxWidth / 2;

            // Add a column label and background vertical line
            const colLabel = colData[+i].colname;
            nodeSvgData.push(
                svg`<text class="column-label" x="${labX}" y="20">${colLabel}</text>`
            );
            nodeSvgData.push(svg`
                <line class="column-line"
                    x1="${labX}"
                    x2="${labX}"
                    y1="20"
                    y2="${this.svgHeight}">
                </line>
            `);

            // Add all the nodes of the column to the svg and set up link data to be drawn
            const boxLabels = colData[+i].vals;
            const colBounds: BoxBounds = {};
            const colLinks: Link[] = [];
            for (let j = 0; j < boxLabels.length; j++) {
                // Extract the link data for each of the boxes in current column
                const boxLinks: string[] = [];
                for (const link of graphData.spec.links) {
                    if (link.source === boxLabels[j]) {
                        boxLinks.push(`${link.source}-${link.target}`);
                        colLinks.push(link);
                    }
                }

                // width of the boxes
                const span = this.svgHeight / boxLabels.length / 2;

                // starting y-coords of the svg elems
                const boxY =
                    20 + span + (this.svgHeight / boxLabels.length) * j;
                const textY =
                    span +
                    this.boxHeight +
                    (this.svgHeight / boxLabels.length) * j +
                    15;

                // start coords of the links of the current node
                const linkY = boxY + this.boxHeight / 2;
                const linkX = colX + boxWidth;

                nodeSvgData.push(svg`
                    <g id="${colLabel}-${j}"
                        class="label-group"
                        @mouseover="${(e: MouseEvent) => this.mouseOverNode(e)}"
                        @mouseleave="${(e: MouseEvent) =>
                            this.mouseLeaveElem(e)}">
                        <rect id="${boxLabels[j]}"
                            class="labelbox"
                            width="${boxWidth}"
                            height="${this.boxHeight}"
                            x="${colX}" y="${boxY}"
                            opacity="0.7"
                            data-links="${boxLinks}">
                        </rect>
                        <text id="${boxLabels[j]}"
                            class="label-text"
                            x="${labX}"
                            y="${textY}"
                            opacity="1.0">${boxLabels[j]}
                        </text>
                    </g>
                `);

                // Add box bound coords
                colBounds[boxLabels[j]] = {
                    left: { x: colX, y: linkY },
                    right: { x: linkX, y: linkY },
                };
            }

            linkData[colData[+i].colname] = {
                links: colLinks,
                bound: colBounds,
            };
        }

        // draw the links of the network
        const linkSvgData: SVGTemplateResult[] = [];
        for (let i = 1; i < Object.keys(colData).length; i++) {
            const colCurr = colData[i].colname;
            const colNext = colData[i + 1].colname;

            const links = linkData[colCurr].links;
            const boundsLeft = linkData[colCurr].bound;
            const boundsRight = linkData[colNext].bound;

            for (const link of links) {
                // Start- and end-coordinates
                const x1 = boundsLeft[link.source].right.x;
                const y1 = boundsLeft[link.source].right.y;
                const x2 = boundsRight[link.target].left.x;
                const y2 = boundsRight[link.target].left.y;

                // length and height
                const l = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
                const h = this.boxHeight * link.strength;

                const b: number = h / 2;
                const c: number = h / 4;
                const a: number = l - b - c;

                const shape = `M 0 0 v ${h} h ${a} v ${1 * c} l ${c + b} ${
                    -1 * (c + b)
                } l ${-1 * (b + c)} ${-1 * (b + c)} v ${1 * c} h ${-1 * a}`;

                const angle = (Math.asin((y2 - y1) / l) * 180) / Math.PI;
                const blurLevel = Math.round(((1 - link.certainty) * 10) / 10);

                linkSvgData.push(svg`
                    <g class="link-group">
                        <path id="${link.source}-${link.target}"
                            class="${classMap({
                                link: true,
                                active: this.highlightedLinks.has(link),
                            })}"
                            d="${shape}"
                            transform="translate(${x1} ${y1 - h / 2})
                                        rotate(${angle} 0 ${h / 2})"
                            opacity="${0.2 + link.certainty * 0.4}"
                            filter="url(#blur-${blurLevel})"
                            @mouseover="${this.mouseOverLink}"
                            @mouseleave="${this.mouseLeaveElem}">
                        </path>
                    </g>`);
            }
        }

        // Nodes on top of arrows, hence after in the z-order.
        const links = svg`<g id="links">${linkSvgData}</g>`;
        const nodes = svg`<g id="nodes">${nodeSvgData}</g>`;

        return [links, nodes];
    }

    /**
     * Draws the whole graph from input node-link data.
     * @param {NodeLink} graphData - Input graph in node-link-format.
     * @returns {TemplateResult} - An array containing <svg>-elems for nodes and links.
     */
    private drawSvgGraph(graphData: NodeLink): TemplateResult {
        const canvas = html`<div class="oncowidget">
            <svg
                id="explainerview"
                viewBox="0 0 ${this.svgWidth} ${this.svgHeight}"
            >
                <rect
                    class="explainerview-canvas"
                    width="100%"
                    height="100%"
                ></rect>
                ${_addSvgBlurFilters()} ${this.addSvgNodesAndLinks(graphData)}
            </svg>
        </div>`;

        return canvas;
    }

    private addNodePaths(target: string): void {
        // Stash all the children and parent nodes and links of `target`-node
        const paths = this.dag.get(target)!;
        const fwd_links = traverseNodes(paths, "forward", "node");
        const bwd_links = traverseNodes(paths, "backward", "node");
        this.highlightedLinks = new Set<Link>([
            ...bwd_links.keys(),
            ...fwd_links.keys(),
        ]);

        this.highlightedNodePaths = new Set<Node>([
            ...bwd_links.values(),
            ...fwd_links.values(),
        ]);
    }

    private addLinkPaths(source: string, target: string): void {
        // Stash all the children nodes and links of `target`-node
        const paths = this.dag.get(target)!;
        const links = traverseNodes(paths, "forward", "link", source);

        this.highlightedNodePaths = new Set<Node>([...links.values()]);
        this.highlightedLinks = new Set<Link>([...links.keys()]);
    }

    private mouseOverNode(e: MouseEvent): void {
        const target = e.target as HTMLElement;
        this.addNodePaths(target.id);

        this.tooltip.updateWithDatum(
            this.dag.get(target.id)?.node,
            dataTooltipHandler
        );

        this.requestUpdate();
    }

    private mouseOverLink(e: MouseEvent): void {
        const target = e.target as HTMLElement;
        const nodes = target.id.split("-");
        this.addLinkPaths(nodes[0], nodes[1]);

        // Get the correct Link for tooltip
        const links = this.dag.get(nodes[0])?.children;
        if (links) {
            for (const child of links) {
                if (child.link.target === nodes[1]) {
                    this.tooltip.updateWithDatum(
                        child.link,
                        dataTooltipHandler
                    );
                }
            }
        }

        this.requestUpdate();
    }

    private mouseLeaveElem(e: MouseEvent): void {
        this.highlightedLinks.clear();
        this.highlightedNodePaths.clear();
        this.tooltip.clear();
        this.requestUpdate();
    }

    private async fetchNetworkData(id: number) {
        const apiUrl = `http://127.0.0.1:8888/api/explainer/networks/${id}/`;
        const response = await fetch(apiUrl);
        const jsonData = await (response.json() as Promise<NodeLink>);
        this.graph = jsonData;
        this.dag = nodeLinkToDAG(this.graph);
        this.requestUpdate();
    }

    connectedCallback(): void {
        super.connectedCallback();
        this.fetchNetworkData(3); // TODO: idx arg as user input
    }

    render(): TemplateResult {
        const nodeLink = this.graph as NodeLink;
        return this.graph
            ? this.drawSvgGraph(nodeLink)
            : html`<p>Loading...</p>`;
    }
}

function _addSvgBlurFilters(blurMax = 4): TemplateResult<2> {
    //Add svg filter defs for blur-values.
    const filters: TemplateResult[] = [];
    for (let b = 0; b <= 1; b += 0.1) {
        const blur = Math.round(b * 10) / 10;
        const filter = svg`
            <filter id="blur-${blur}">
                <feGaussianBlur
                    in="SourceGraphic"
                    stdDeviation="${blurMax * blur}">
                </feGaussianBlur>
            </filter>`;
        filters.push(filter);
    }

    return svg`<defs>${filters}</defs>`;
}

function _getColNodeData(graphData: NodeLink) {
    // morph the column node data from node-link into
    // ordered array of dicts for easier svg drawing
    const colData: Column = [];
    for (const node of graphData.spec.nodes) {
        colData[node.order] = { vals: [], colname: node.group };
    }

    for (const node of graphData.spec.nodes) {
        colData[node.order].vals.push(node.id);
    }

    return colData;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-explainer": ExplainerView;
    }
}
