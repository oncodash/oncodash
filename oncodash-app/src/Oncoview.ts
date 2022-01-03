import * as d3 from 'd3';
import { LitElement, html, css } from 'lit';
import { property } from 'lit/decorators.js';
import { get, post } from './util/rest'


// Types
interface Link {
  from: string;
  to: string;
  /** Certainty in ] 0,1] */
  certainty: number;
  /** Strength  in [-1,1] */
  strength: number;
}

interface OncoData {
  samples: string[];
  lines: string[];
  alterations: string[];
  cancers: string[];
  drugs: string[];
  effects: string[];

  samplesLines: Link[];
  linesAlterations: Link[];
  alterationsCancers: Link[];
  cancersDrugs: Link[];
  drugsEffects: Link[];
}

// Data
const data: OncoData = {
  // Labels
  samples: ['Ascites', 'Peritoneum', 'Tuba 1', 'Mesenterium 1'],
  lines: ['KMM-1', '293A', 'A549'],
  alterations: ['FANCA del', 'CDKN1B del'],
  cancers: ['High-grade', 'Low-grade'],
  drugs: ['PARP', 'CDK2/4', 'CDK4/6'],
  effects: [
    'Platelet drop',
    'Blood drop',
    'Vomiting',
    'Stomach',
    'Nausea',
    'Fatigue',
  ],

  // Links
  samplesLines: [
    { from: 'Ascites', to: 'KMM-1', certainty: 0.5, strength: 0.5 },
    { from: 'Peritoneum', to: '293A', certainty: 0.8, strength: 0.2 },
    { from: 'Tuba 1', to: 'KMM-1', certainty: 0.1, strength: 0.1 },
    { from: 'Mesenterium 1', to: '293A', certainty: 0.9, strength: 0.1 },
    { from: 'Ascites', to: 'A549', certainty: 0.5, strength: 0.5 },
    { from: 'Tuba 1', to: 'A549', certainty: 0.5, strength: 0.5 },
    { from: 'Mesenterium 1', to: 'KMM-1', certainty: 0.1, strength: 0.9 },
  ],
  linesAlterations: [
    { from: 'KMM-1', to: 'FANCA del', certainty: 0.8, strength: 0.1 },
    { from: 'KMM-1', to: 'CDKN1B del', certainty: 0.4, strength: 0.3 },
    { from: '293A', to: 'CDKN1B del', certainty: 0.8, strength: 1.0 },
    { from: 'A549', to: 'FANCA del', certainty: 0.2, strength: 0.9 },
  ],
  alterationsCancers: [
    { from: 'FANCA del', to: 'High-grade', certainty: 1.0, strength: 0.9 },
    { from: 'FANCA del', to: 'Low-grade', certainty: 0.1, strength: 0.5 },
    { from: 'CDKN1B del', to: 'High-grade', certainty: 0.3, strength: 0.3 },
  ],
  cancersDrugs: [
    { from: 'High-grade', to: 'PARP', certainty: 0.8, strength: 0.2 },
    { from: 'Low-grade', to: 'PARP', certainty: 0.8, strength: 0.2 },
    { from: 'High-grade', to: 'CDK2/4', certainty: 0.2, strength: 0.1 },
    { from: 'Low-grade', to: 'CDK2/4', certainty: 0.4, strength: 0.8 },
    { from: 'High-grade', to: 'CDK4/6', certainty: 0.8, strength: 0.2 },
    { from: 'Low-grade', to: 'CDK4/6', certainty: 0.9, strength: 0.6 },
  ],
  drugsEffects: [
    { from: 'PARP', to: 'Platelet drop', certainty: 0.2, strength: 0.3 },
    { from: 'CDK2/4', to: 'Platelet drop', certainty: 0.1, strength: 0.9 },
    { from: 'CDK4/6', to: 'Platelet drop', certainty: 0.8, strength: 0.2 },
    { from: 'PARP', to: 'Blood drop', certainty: 0.2, strength: 0.4 },
    { from: 'CDK2/4', to: 'Blood drop', certainty: 0.1, strength: 0.1 },
    { from: 'CDK4/6', to: 'Blood drop', certainty: 0.8, strength: 0.3 },
    { from: 'PARP', to: 'Vomiting', certainty: 0.4, strength: 0.7 },
    { from: 'CDK2/4', to: 'Vomiting', certainty: 0.5, strength: 0.6 },
    { from: 'CDK4/6', to: 'Vomiting', certainty: 0.1, strength: 0.8 },
    { from: 'PARP', to: 'Stomach', certainty: 0.7, strength: 0.2 },
    { from: 'CDK2/4', to: 'Stomach', certainty: 0.4, strength: 0.1 },
    { from: 'CDK4/6', to: 'Stomach', certainty: 0.3, strength: 0.05 },
    { from: 'PARP', to: 'Nausea', certainty: 0.9, strength: 0.95 },
    { from: 'CDK2/4', to: 'Nausea', certainty: 0.1, strength: 0.8 },
    { from: 'CDK4/6', to: 'Nausea', certainty: 0.2, strength: 0.2 },
    { from: 'PARP', to: 'Fatigue', certainty: 0.1, strength: 0.45 },
    { from: 'CDK2/4', to: 'Fatigue', certainty: 0.9, strength: 0.2 },
    { from: 'CDK4/6', to: 'Fatigue', certainty: 0.9, strength: 0.1 },
  ],
};

interface Coords {
  x: number;
  y: number;
}

interface BoxBound {
  left: Coords;
  right: Coords;
}

interface BoxBounds {
  // Maps labels to box bounds
  [index: string]: BoxBound;
}

function drawColumn(
  labels: string[],
  id: string,
  svg: any,
  columnX: number,
  labelBoxWidth: number,
  labelBoxHeight: number,
  svgWidth: number,
  svgHeight: number
): BoxBounds {
  const bounds: BoxBounds = {};

  // Column header
  svg
    .append('text')
    .attr('class', 'column_label')
    .attr('x', columnX + labelBoxWidth / 2)
    .attr('y', 20)
    .text(id);

  svg
    .append('line')
    .attr('class', 'column_line')
    .attr('x1', columnX + labelBoxWidth / 2)
    .attr('x2', columnX + labelBoxWidth / 2)
    .attr('y1', 20)
    .attr('y2', svgHeight);

  // for(let i in labels) { // FIXME how come this doesn't work?
  for (let i = 0; i < labels.length; i++) {
    const s = svg.append('g').attr('id', id + '_' + i);

    const span = svgHeight / labels.length / 2;
    const boxY = 20 + span + (svgHeight / labels.length) * i;
    bounds[labels[i]] = {
      left: { x: columnX, y: boxY + labelBoxHeight / 2 },
      right: { x: columnX + labelBoxWidth, y: boxY + labelBoxHeight / 2 },
    };

    s.append('rect')
      .attr('class', 'label_box')
      .attr('width', labelBoxWidth)
      .attr('height', labelBoxHeight)
      .attr('x', columnX)
      .attr('y', boxY)
      .text(''); // FIXME only way to close the tag?

    s.append('text')
      .attr('class', 'label_text')
      .attr('x', columnX + labelBoxWidth / 2)
      .attr('y', span + labelBoxHeight + (svgHeight / labels.length) * i + 15)
      .text(labels[i]);
  }

  return bounds;
}

function drawLinks(
  links: Link[],
  boundsLeft: BoxBounds,
  boundsRight: BoxBounds,
  svg: any,
  labelBoxHeight: number
) {
  for (const link of links) {
    const x1 = boundsLeft[link.from].right.x;
    const y1 = boundsLeft[link.from].right.y;
    const x2 = boundsRight[link.to].left.x;
    const y2 = boundsRight[link.to].left.y;

    const l = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    const h = labelBoxHeight * link.strength;
    const c = link.certainty;
    const shape = `M 0 0 v ${h} h ${l - h / 2} l ${h / 2} ${(-1 * h) / 2} l ${
      (-1 * h) / 2
    } ${(-1 * h) / 2} h ${-1 * (l - h / 2)}`;

    // let place : any = d3.transform() // FIXME Attempted import error: 'transform' is not exported from 'd3' (imported as 'd3').
    //     .translate([10,10])
    //     .rotate(30);

    const arrow = svg
      .append('path')
      .attr('class', 'arrow')
      .attr('d', shape)
      // .attr('transform', place)
      .attr(
        'transform',
        `translate(${x1} ${y1 - h / 2}) rotate(${
          (Math.asin((y2 - y1) / l) * 180) / Math.PI
        } 0 ${h / 2})`
      )
      .attr('opacity', 0.2 + c * 0.8)
      .attr('filter', `url(#blur_${Math.round((1 - c) * 10) / 10})`);
  }
}

function draw() {
  // General parameters
  const svgWidth = 1024;
  const svgHeight = 480;
  const columnWidth = svgWidth / 5.5;
  const labelBoxWidth = columnWidth / 2;
  const labelBoxHeight = 20;
  const blurMax = 3;

  const div = document.createElement("div");
  const container = d3.select(div)
    .attr("id","oncowidget");

  // Canvas
  container.append('p').text('Oncoview');
  const svg = container.append("svg")
    .attr("id","oncoview")
    .attr('viewBox', '0 0 ' + svgWidth.toString() + " " + svgHeight.toString());

  svg
    .append('rect')
    .attr('class', 'oncoview_canvas')
    .attr('width', '100%')
    .attr('height', '100%');

  // Filters
  const defs = svg.append('defs');

  for (let b = 0; b <= 1; b += 0.1) {
    const blur = Math.round(b * 10) / 10;
    defs
      .append('filter')
      .attr('id', `blur_${blur}`)
      .append('feGaussianBlur')
      .attr('stdDeviation', blurMax * blur);
  }

  // Draw links under items
  const links = svg.append('g').attr('id', 'links');
  const items = svg.append('g').attr('id', 'items');

  // Draw labels
  const samples = drawColumn(
    data.samples,
    'Sample',
    items,
    0 * columnWidth,
    labelBoxWidth,
    labelBoxHeight,
    svgWidth,
    svgHeight
  );
  const lines = drawColumn(
    data.lines,
    'Line',
    items,
    1 * columnWidth,
    labelBoxWidth,
    labelBoxHeight,
    svgWidth,
    svgHeight
  );
  const alterations = drawColumn(
    data.alterations,
    'Alteration',
    items,
    2 * columnWidth,
    labelBoxWidth,
    labelBoxHeight,
    svgWidth,
    svgHeight
  );
  const cancers = drawColumn(
    data.cancers,
    'Cancer',
    items,
    3 * columnWidth,
    labelBoxWidth,
    labelBoxHeight,
    svgWidth,
    svgHeight
  );
  const drugs = drawColumn(
    data.drugs,
    'Drug',
    items,
    4 * columnWidth,
    labelBoxWidth,
    labelBoxHeight,
    svgWidth,
    svgHeight
  );
  const effects = drawColumn(
    data.effects,
    'Effect',
    items,
    5 * columnWidth,
    labelBoxWidth,
    labelBoxHeight,
    svgWidth,
    svgHeight
  );

  drawLinks(data.samplesLines, samples, lines, links, labelBoxHeight);
  drawLinks(data.linesAlterations, lines, alterations, links, labelBoxHeight);
  drawLinks(
    data.alterationsCancers,
    alterations,
    cancers,
    links,
    labelBoxHeight
  );
  drawLinks(data.cancersDrugs, cancers, drugs, links, labelBoxHeight);
  drawLinks(data.drugsEffects, drugs, effects, links, labelBoxHeight);

  return div;
}

class Oncoview extends LitElement {
  static styles = css`
    .Oncoview {
    }

    .oncoview_canvas {
      fill: white;
    }

    .label_box {
      fill: #f2f2f2;
      rx: 0.5em;
      ry: 0.5em;
      stroke: black;
      stroke-width: 1px;
    }

    .label_text {
      color: black;
      font-size: 1ex;
      text-anchor: middle;
      text-align: center;
    }

    .column_label {
      color: black;
      font-size: 1ex;
      font-style: italic;
      text-anchor: middle;
      text-align: center;
    }

    .column_line {
      stroke: #ccc;
      stroke-width: 0.5px;
    }

    .arrow {
      stroke-width: 1px;
      fill: #0055d4;
    }
  `;

  render() {
    return draw();
  }
}

export default Oncoview;

customElements.define('onco-view', Oncoview);
