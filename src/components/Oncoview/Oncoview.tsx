import React, { useEffect, RefObject } from 'react'
import './Oncoview.css';
import * as d3 from 'd3';

// Types
interface Link {
    from : string,
    to : string,
    certainty : number, // certainty in ] 0,1]
    strength  : number  // strenght  in [-1,1]
    
};

interface OncoData {
    samples : string[],
    lines: string[],
    alterations : string[],
    cancers : string[],
    drugs: string[],
    effects: string[],
    
    samples_lines : Link[],
    lines_alterations: Link[],
    alterations_cancers : Link[]
    cancers_drugs: Link[],
    drugs_effects : Link[]
};

// Data
var data : OncoData = {
    // Labels
    samples:     ['Ascites','Peritoneum','Tuba 1','Mesenterium 1'],
    lines:       ['KMM-1','293A','A549'],
    alterations: ['FANCA del', 'CDKN1B del'],
    cancers:     ['High-grade','Low-grade'],
    drugs:       ['PARP', 'CDK2/4','CDK4/6'],
    effects:     ['Platelet drop', 'Blood drop', 'Vomiting', 'Stomach', 'Nausea', 'Fatigue'],

    // Links
    samples_lines: [
        {from: 'Ascites',       to: 'KMM-1',  certainty: 0.5, strength: 0.5},
        {from: 'Peritoneum',    to: '293A',   certainty: 0.8, strength: 0.2},
        {from: 'Tuba 1',        to: 'KMM-1',  certainty: 0.1, strength: 0.1},
        {from: 'Mesenterium 1', to: '293A',   certainty: 0.9, strength: 0.1},
        {from: 'Ascites',       to: 'A549',   certainty: 0.5, strength: 0.5},
        {from: 'Tuba 1',        to: 'A549',   certainty: 0.5, strength: 0.5},
        {from: 'Mesenterium 1', to: 'KMM-1',  certainty: 0.1, strength: 0.9}
    ],
    lines_alterations: [
        {from: 'KMM-1', to: 'FANCA del',  certainty: 0.8, strength: 0.1},
        {from: 'KMM-1', to: 'CDKN1B del', certainty: 0.4, strength: 0.3},
        {from: '293A',  to: 'CDKN1B del', certainty: 0.8, strength: 1.0},
        {from: 'A549',  to: 'FANCA del',  certainty: 0.2, strength: 0.9},
    ],
    alterations_cancers: [
        {from: 'FANCA del',  to: 'High-grade', certainty: 1.0, strength: 0.9},
        {from: 'FANCA del',  to: 'Low-grade',  certainty: 0.1, strength: 0.5},
        {from: 'CDKN1B del', to: 'High-grade', certainty: 0.3, strength: 0.3}
    ],
    cancers_drugs: [
        {from: 'High-grade', to: 'PARP',   certainty: 0.8, strength: 0.2},
        {from: 'Low-grade',  to: 'PARP',   certainty: 0.8, strength: 0.2},
        {from: 'High-grade', to: 'CDK2/4', certainty: 0.2, strength: 0.1},
        {from: 'Low-grade',  to: 'CDK2/4', certainty: 0.4, strength: 0.8},
        {from: 'High-grade', to: 'CDK4/6', certainty: 0.8, strength: 0.2},
        {from: 'Low-grade',  to: 'CDK4/6', certainty: 0.9, strength: 0.6},
    ],
    drugs_effects: [
        {from: 'PARP',   to: 'Platelet drop', certainty: 0.2, strength: 0.3},
        {from: 'CDK2/4', to: 'Platelet drop', certainty: 0.1, strength: 0.9},
        {from: 'CDK4/6', to: 'Platelet drop', certainty: 0.8, strength: 0.2},
        {from: 'PARP',   to: 'Blood drop',    certainty: 0.2, strength: 0.4},
        {from: 'CDK2/4', to: 'Blood drop',    certainty: 0.1, strength: 0.1},
        {from: 'CDK4/6', to: 'Blood drop',    certainty: 0.8, strength: 0.3},
        {from: 'PARP',   to: 'Vomiting',      certainty: 0.4, strength: 0.7},
        {from: 'CDK2/4', to: 'Vomiting',      certainty: 0.5, strength: 0.6},
        {from: 'CDK4/6', to: 'Vomiting',      certainty: 0.1, strength: 0.8},
        {from: 'PARP',   to: 'Stomach',       certainty: 0.7, strength: 0.2},
        {from: 'CDK2/4', to: 'Stomach',       certainty: 0.4, strength: 0.1},
        {from: 'CDK4/6', to: 'Stomach',       certainty: 0.3, strength: 0.05},
        {from: 'PARP',   to: 'Nausea',        certainty: 0.9, strength: 0.95},
        {from: 'CDK2/4', to: 'Nausea',        certainty: 0.1, strength: 0.8},
        {from: 'CDK4/6', to: 'Nausea',        certainty: 0.2, strength: 0.2},
        {from: 'PARP',   to: 'Fatigue',       certainty: 0.1, strength: 0.45},
        {from: 'CDK2/4', to: 'Fatigue',       certainty: 0.9, strength: 0.2},
        {from: 'CDK4/6', to: 'Fatigue',       certainty: 0.9, strength: 0.1},    ]

};

interface Coords {
    x : number,
    y : number
};

interface BoxBound {
    left : Coords,
    right : Coords
};

interface BoxBounds {
    // Maps labels to box bounds
    [index: string] : BoxBound;
};


function draw_column(
        labels : string[],
        id : string,
        svg : any,
        column_x : number,
        label_box_width : number,
        label_box_height : number,
        svg_width : number,
        svg_height : number
) : BoxBounds {
    
    let bounds : BoxBounds = {};

    // Column header
    svg.append('text')
        .attr('class', 'column_label')
        .attr('x', column_x + label_box_width/2)
        .attr('y', 20)
        .text(id);

    svg.append('line')
        .attr('class','column_line')
        .attr('x1',column_x + label_box_width/2)
        .attr('x2',column_x + label_box_width/2)
        .attr('y1',20)
        .attr('y2',svg_height);

    
    // for(let i in labels) { // FIXME how come this doesn't work?
    for(let i : number = 0; i < labels.length; i++) {

        var s = svg.append('g')
            .attr('id', id+'_'+i);

        let span : number = (svg_height/labels.length)/2;
        let box_y : number = 20 + span + svg_height / labels.length * i;
        bounds[labels[i]] = {
                left : {x: column_x,                 y: box_y + label_box_height/2},
                right: {x: column_x+label_box_width, y: box_y + label_box_height/2}
            };

        s.append('rect')
            .attr('class','label_box')
            .attr('width',label_box_width)
            .attr('height',label_box_height)
            .attr('x', column_x)
            .attr('y', box_y)
            .text(''); // FIXME only way to close the tag?

        s.append('text')
            .attr('class','label_text')
            .attr('x', column_x + label_box_width/2)
            .attr('y', span + label_box_height + svg_height/labels.length*i + 15)
            .text(labels[i])
            ;
    }

    return bounds;

}

function draw_links(
    links : Link[],
    bounds_left : BoxBounds,
    bounds_right : BoxBounds,
    svg : any,
    label_box_height : number

) {
        for(let link of links) {
            let x1 : number = bounds_left[link.from].right.x;
            let y1 : number = bounds_left[link.from].right.y;
            let x2 : number = bounds_right[link.to  ].left.x;
            let y2 : number = bounds_right[link.to  ].left.y;

            let l : number = Math.sqrt(Math.pow(x2-x1,2)+Math.pow(y2-y1,2));
            let h : number = label_box_height * link.strength;
            let c : number = link.certainty;
            let shape : string = `M 0 0 v ${h} h ${l-h/2} l ${h/2} ${-1*h/2} l ${-1*h/2} ${-1*h/2} h ${-1*(l-h/2)}`;

            // let place : any = d3.transform() // FIXME Attempted import error: 'transform' is not exported from 'd3' (imported as 'd3').
            //     .translate([10,10])
            //     .rotate(30);

            let arrow : any = svg.append("path")
                .attr('class', 'arrow')
                .attr('d',shape)
                // .attr('transform', place)
                .attr('transform', `translate(${x1} ${y1-h/2}) rotate(${Math.asin((y2-y1)/l) * 180/Math.PI} 0 ${h/2})`)
                .attr('opacity', 0.2 + c * 0.8)
                .attr('filter',`url(#blur_${Math.round((1-c)*10)/10})`)
                ;
        }
}

const Oncoview = () => {
    const ref: RefObject<HTMLDivElement> = React.createRef();

    useEffect(() => {
        draw()
    })

    const draw = () => {

        // General parameters
        let svg_width : number = 1024;
        let svg_height : number = 480;
        let column_width : number = svg_width / 5.5;
        let label_box_width : number = column_width/2;
        let label_box_height : number = 20;
        let blur_max : number = 3;

        // Canvas
        d3.select(ref.current).append('p').text('Oncoview');
        let svg = d3.select('svg')
            .attr('width', svg_width)
            .attr('height',svg_height);
        svg.append('rect')
            .attr('class','oncoview_canvas')
            .attr('width','100%')
            .attr('height','100%');

        // Filters
        var defs = svg.append("defs");

        for(let b : number = 0; b <= 1; b+=0.1) {
            let blur : number = Math.round(b*10)/10;
            defs.append("filter")
                .attr("id", `blur_${blur}`)
                .append("feGaussianBlur")
                .attr("stdDeviation", blur_max * blur);
        }

        // Draw links under items
        let links = svg.append('g').attr('id','links');
        let items = svg.append('g').attr('id','items');
            
        // Draw labels
        let samples     : BoxBounds = draw_column( data.samples,     'Sample',      items, 0*column_width, label_box_width, label_box_height, svg_width, svg_height );
        let lines       : BoxBounds = draw_column( data.lines,       'Line',        items, 1*column_width, label_box_width, label_box_height, svg_width, svg_height );
        let alterations : BoxBounds = draw_column( data.alterations, 'Alteration',  items, 2*column_width, label_box_width, label_box_height, svg_width, svg_height );
        let cancers     : BoxBounds = draw_column( data.cancers,     'Cancer',      items, 3*column_width, label_box_width, label_box_height, svg_width, svg_height );
        let drugs       : BoxBounds = draw_column( data.drugs,       'Drug',        items, 4*column_width, label_box_width, label_box_height, svg_width, svg_height );
        let effects     : BoxBounds = draw_column( data.effects,     'Effect',      items, 5*column_width, label_box_width, label_box_height, svg_width, svg_height );
        draw_links( data.samples_lines      , samples    , lines      , links, label_box_height );
        draw_links( data.lines_alterations  , lines      , alterations, links, label_box_height );
        draw_links( data.alterations_cancers, alterations, cancers    , links, label_box_height );
        draw_links( data.cancers_drugs      , cancers    , drugs      , links, label_box_height );
        draw_links( data.drugs_effects      , drugs      , effects    , links, label_box_height );

   }

    return (
        <div className="Oncoview" ref={ref}>
            <svg>
            </svg>
        </div>
    )
};

export default Oncoview;
