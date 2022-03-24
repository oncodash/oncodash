import * as d3 from "d3";
import { LitElement, css } from "lit";
import {customElement, property} from 'lit/decorators.js';

// Interfaces for the graph query data
interface Node {
    id: string;
    group: string;
    order: number;
}

interface Link {
    source: string;
    target: string;
    certainty: number;
    strength: number;
}

interface NodeLink {
    id: number;
    patient: string;
    spec: {
        directed: boolean;
        multigraph: boolean;
        graph: Record<string, unknown>;
        nodes: Node[];
        links: Link[];
    };
}

// `drawColumn()` specific interfaces (return data)
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

// `drawGraph()` specific type
type Column = { vals: string[]; colname: string }[];

// `drawLinks() specific type`
type ColumnLinks = Record<string, { links: Link[]; bound: BoxBounds }>;

/**
 * Draws one column from given input data.
 * @param svg Reference svg object that will be rendered.
 * @param labels The column values.
 * @param id The Column name.
 * @param columnX The starting x-coordinate of the column.
 * @param labelBoxWidth Width (in pixels) of any column value box
 * @param labelBoxHeight Height (in pixels) of any column value box
 * @param svgHeight Height (in pixels) of the reference svg object
 * @returns x- and y-bounds of the svg-column
 */
function drawColumn(
    svg: any, // HTMLElement & SVGElement,
    labels: string[],
    id: string,
    columnX: number,
    labelBoxWidth: number,
    labelBoxHeight: number,
    svgHeight: number
): BoxBounds {
    // Column header
    svg.append("text")
        .attr("class", "column-label")
        .attr("x", columnX + labelBoxWidth / 2)
        .attr("y", 20)
        .text(id);

    // strike-through line
    svg.append("line")
        .attr("class", "column-line")
        .attr("x1", columnX + labelBoxWidth / 2)
        .attr("x2", columnX + labelBoxWidth / 2)
        .attr("y1", 20)
        .attr("y2", svgHeight);

    // draw the columns
    const bounds: BoxBounds = {};
    for (let i = 0; i < labels.length; i++) {
        const s = svg.append("g").attr("id", `${id}-${i}`);
        const span = svgHeight / labels.length / 2;
        const boxY = 20 + span + (svgHeight / labels.length) * i;

        bounds[labels[i]] = {
            left: { x: columnX, y: boxY + labelBoxHeight / 2 },
            right: { x: columnX + labelBoxWidth, y: boxY + labelBoxHeight / 2 },
        };

        s.append("rect")
            .attr("class", "label-box")
            .attr("width", labelBoxWidth)
            .attr("height", labelBoxHeight)
            .attr("x", columnX)
            .attr("y", boxY)
            .text(""); // FIXME only way to close the tag?

        s.append("text")
            .attr("class", "label-text")
            .attr("x", columnX + labelBoxWidth / 2)
            .attr(
                "y",
                span + labelBoxHeight + (svgHeight / labels.length) * i + 15
            )
            .text(labels[i]);
    }

    return bounds;
}

/**
 * Draws one column from given input data.
 * @param svg Reference svg object that will be rendered.
 * @param link The link data in node-link format.
 * @param boundsLeft An object containing the link start xy-coords.
 * @param boundsRight An object containing the link end xy-coords.
 * @param labelBoxHeight Height (in pixels) of any column value box
 */
function drawLinks(
    svg: any,
    links: Link[],
    boundsLeft: BoxBounds,
    boundsRight: BoxBounds,
    labelBoxHeight: number
) {
    for (const link of links) {
        // Start- and end-coordinates
        const x1 = boundsLeft[link.source].right.x;
        const y1 = boundsLeft[link.source].right.y;
        const x2 = boundsRight[link.target].left.x;
        const y2 = boundsRight[link.target].left.y;

        // length and height
        const l = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const h = labelBoxHeight * link.strength;

        const b:number = h / 2;
        const c:number = h / 4;
        const a:number = l - b - c;

        const shape = `M 0 0 v ${h} h ${a} v ${1*c} l ${c+b} ${-1*(c+b)} l ${-1*(b+c)} ${-1*(b+c)} v ${1*c} h ${-1*a}`;

        // draw the link
        svg.append("path")
            .attr("class", "link")
            .attr("d", shape)
            .attr(
                "transform",
                `translate(${x1} ${y1 - h / 2})
               rotate(${(Math.asin((y2 - y1) / l) * 180) / Math.PI} 0 ${h / 2})`
            )
            .attr("opacity", 0.2 + link.certainty * 0.4)
            .attr(
                "filter",
                `url(#blur-${Math.round(((1 - link.certainty) * 10) / 10)})`
            );
    }
}

/**
 * Draws the Graph from input node-link data.
 * @param graphData Input graph in node-link-format
 * @returns a <div> container containing the svg visualization
 */
function drawGraph(graphData: NodeLink): HTMLElement {
    // General parameters
    const svgWidth = 1024;
    const svgHeight = 480;
    const labelBoxHeight = 16;
    const blurMax = 4;

    // shadow-DOM container
    const div = document.createElement("div");
    const container = d3.select(div).attr("id", "oncowidget");

    // Canvas
    const svg = container
        .append("svg")
        .attr("id", "explainerview")
        .attr("viewBox", `0 0 ${svgWidth} ${svgHeight}`);

    svg.append("rect")
        .attr("class", "explainerview-canvas")
        .attr("width", "100%")
        .attr("height", "100%");

    // Filters
    const defs = svg.append("defs");

    for (let b = 0; b <= 1; b += 0.1) {
        const blur = Math.round(b * 10) / 10;
        defs.append("filter")
            .attr("id", `blur-${blur}`)
            .append("feGaussianBlur")
                .attr("in","SourceGraphic")
                .attr("stdDeviation", blurMax * blur);
    }

    const links = svg.append("g").attr("id", "links");
    // Nodes on top of arrows, hence after in the z-order.
    const nodes = svg.append("g").attr("id", "nodes");

    // wrangle the column nodes data-structure for `drawColumn()`
    const colData: Column = [];
    for (const node of graphData.spec.nodes) {
        colData[node.order] = { vals: [], colname: node.group };
    }

    for (const node of graphData.spec.nodes) {
        colData[node.order].vals.push(node.id);
    }

    // Draw the columns and wrangle link data for `drawLinks()`
    const columnWidth = svgWidth / Object.keys(colData).length;
    const labelBoxWidth = columnWidth / 2;
    const linkData: ColumnLinks = {};
    for (const i of Object.keys(colData)) {
        const colBounds = drawColumn(
            nodes,
            colData[+i].vals,
            colData[+i].colname,
            (+i - 1 + 0.25) * columnWidth,
            labelBoxWidth,
            labelBoxHeight,
            svgHeight
        );

        const colLinks: Link[] = [];
        for (const k of Object.keys(colBounds)) {
            for (const link of graphData.spec.links) {
                if (link.source === k) {
                    colLinks.push(link);
                }
            }
            linkData[colData[+i].colname] = {
                links: colLinks,
                bound: colBounds,
            };
        }
    }

    // draw the links
    for (let i = 1; i < Object.keys(colData).length; i++) {
        const colCurr = colData[i].colname;
        const colNext = colData[i + 1].colname;

        drawLinks(
            links,
            linkData[colCurr].links,
            linkData[colCurr].bound,
            linkData[colNext].bound,
            labelBoxHeight
        );
    }

    return div;
}

/**
 * Lit Element, responsible for rendering the network visualization and
 * fetching the node-link data from the API.
 */
@customElement("oncodash-explainer")
class ExplainerView extends LitElement {
    constructor(private graph?: NodeLink) {
        super();
    }

    static styles = css`
        .ExplainerView {
        }

        .explainerview-canvas {
            fill: white;
        }

        .label-box {
            fill: #f2f2f2;
            rx: 0.5em;
            ry: 0.5em;
            stroke: black;
            stroke-width: 1px;
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
        }
    `;

    connectedCallback(): void {
        super.connectedCallback();
        this.fetchNetworkData(3); // TODO: idx arg as user input
    }

    render(): HTMLElement {
        const data = this.graph as NodeLink;
        return drawGraph(data);
    }

    private fetchNetworkData(id: number) {
        const apiUrl = `http://127.0.0.1:8888/api/explainer/networks/${id}/`;
        return fetch(apiUrl)
            .then((response) => response.json() as Promise<NodeLink>)
            .then((jsonData) => {
                this.graph = jsonData;
                this.requestUpdate();
            });
    }
}

export default ExplainerView;
customElements.define("oncodash-explainer", ExplainerView);
