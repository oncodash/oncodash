import {Container, Row} from 'react-bootstrap';
import CanvasJSReact from '../../lib/canvasjs.stock.react';
var CanvasJSStockChart = CanvasJSReact.CanvasJSStockChart;  

/////////////////////////////////////////

function leftPad(number, targetLength) {
    var output = number + '';
    while (output.length < targetLength) {
        output = ' ' + output;
    }
    return output;
}

function create_chart(dayzero, time_series, name){
    // console.log("dayzero: ", dayzero);
    // console.log("create_chart\ntime_series: ", time_series);
    let points = [];
    let points_below = [];
    let points_above = [];
    let derivative = [];
    let derivative_left  = [];
    const derivative_threshold = 50;
    // let isca125 = name === "ca125";
    let thresholds = time_series.thresholds;
    if(name === "ca125"){
        thresholds = [-10, 10000] //[-10, 8000];
        let diff_x;
        let diff_y;
        for(let i=1; i<time_series.sparse_x.length; i++){
            diff_y = time_series.sparse_y[i]-time_series.sparse_y[i-1];
            diff_x = Math.abs(time_series.sparse_x[i]-time_series.sparse_x[i-1]);
            derivative.push(diff_y/diff_x);
            // console.log("diff_y: ", diff_y);
            // console.log("diff_x: ", diff_x);
        }
        // console.log("derivative: ", derivative);
        // console.log("time_series: ", time_series);
    }
    if(name === "hb"){
        thresholds = [117, 155];
    }
    if(name === "leuk"){
        thresholds = [3.4, 8.2];
    }
    if(name === "neut"){
        thresholds = [1.5, 6.7];
    }
    if(name === "platelets"){
        thresholds = [150, 360];
    }
    // let min_x_value = Math.min(...time_series.x);
    // time_series.x = time_series.x.map(x=>x-min_x_value+1);
    let max_y = Math.max.apply(null, time_series.y)*1.2;
    for(let i=0; i<time_series.x.length; i++){
        let date = new Date(dayzero);
        // console.log("date: ", date)
        date.setDate(date.getDate() + time_series.x[i]);
        // console.log("date: ", date)
        // console.log("x: ", time_series.x[i])
        points.push({x: date, y: time_series.y[i]})
        //below
        if(name!=="ca125"){
            if(time_series.y[i]!==null){
                if(time_series.y[i]<thresholds[0]){
                    points_below.push({x: date, y: [0, time_series.y[i]], markerType: "circle",  markerSize: 10})  
                }else{  
                    points_below.push({x: date, y: [null, null]})
                }
                //above
                if(time_series.y[i]>thresholds[1]){
                    points_above.push({x: date, y: [time_series.y[i], max_y], markerType: "circle",  markerSize: 10})
                }else{
                    points_above.push({x: date, y: [null, null]});
                }
            }
        }
        
    }
    if(name==="ca125"){
        let k = -1;
        for(let i=0; i<time_series.x.length; i++){
            let date = new Date(dayzero);
            date.setDate(date.getDate() + time_series.x[i]);
            if(time_series.sparse_x.includes(time_series.x[i])){    
                k = k + 1; 
                if(k>0){
                    // console.log("included: ", time_series.x[i]);
                    // console.log("derivative[k-1]: ", derivative[k-1]);
                    let previous_day = new Date(dayzero);
                    previous_day.setDate(previous_day.getDate() + time_series.sparse_x[k-1]);
                    if(derivative[k-1]>derivative_threshold){
                        points_above.push({x: previous_day, y: [time_series.sparse_y[k-1], max_y]});
                        points_above.push({x: date, y: [time_series.y[i], max_y], 
                            // markerType: "circle",  markerSize: 10
                        });
                        points_below.push({x: date, y: [null, null]});
                    }else{
                        points_above.push({x: date, y: [null, null]})
                    }
                    if(derivative[k-1]<-derivative_threshold){
                        points_below.push({x: previous_day, y: [-100, time_series.sparse_y[k-1]]});
                        points_below.push({x: date, y: [-100, time_series.y[i]], 
                            // markerType: "circle",  markerSize: 10
                        });
                        points_above.push({x: date, y: [null, null]});
                    }else{
                        points_below.push({x: date, y: [null, null]})
                    }
                }else{
                    // points_above.push({x: date, y: [null, null]})
                    // points_below.push({x: date, y: [null, null]})
                }
            }else{
                // points_above.push({x: date, y: [null, null]})
                // points_below.push({x: date, y: [null, null]})
            }
        }
        // console.log("name: ", name);
        // console.log("points above: ", points_above);
        // console.log("points below: ", points_below);
    }


    let axisXtemplate = {
        gridThickness: 1,
        tickLength: 0,
        lineThickness: 1,
        labelFormatter: function(){
          return " ";
        }
    }; 
    let stripLinesTemplate = [
        {
            startValue:thresholds[0],
            endValue:thresholds[1],                
            color:"#d8d8d8",
            label : ""+thresholds[0]+" - "+thresholds[1],
            labelFontColor: "#a8a8a8",
            labelPlacement: "inside",
        }
    ];
    let stripLines = name!=="ca125" ? stripLinesTemplate : [];
    let axisX = name!=="platelets" ? axisXtemplate : {gridThickness: 1};
    let chart = {

        axisY:{
            title: name,
            margin:20,
            // titleFontWeight: "bold",
            titleFontSize: 14,
            // logarithmic: isca125,
            maximum: Math.max.apply(null, time_series.y)*1.1,
            minimum: Math.min.apply(null, time_series.y.filter(x=>x!==null))*0.9,
            labelFormatter: function ( e ) {
                return leftPad(e.value, 5);
            },
            // labelFormatter: function ( e ) {
            //     return "";
            // },
            stripLines:stripLines
        },
        axisX:axisX,
        data: [
                {
                    name: name,
                    type:"line",
                    connectNullData: true,
                    dataPoints: points,
                },
                {
                    type:"rangeArea",
                    // connectNullData: true,
                    dataPoints: points_below,
                },
                {
                    type:"rangeArea",
                    // connectNullData: true,
                    dataPoints: points_above,
                }
        ]
    };
    // console.log("points: ", points);
    // console.log("Chart: ", chart);
    return chart;
}

function create_chart2_points(dayzero, event_series, name, min, max){
    let points = [];
    let value=1;
    let z = 10;
    if(name === "ctdna"){
        value = 1;
    }
    if(name === "fresh_sample"){
        value = 2;
    }
    if(name === "fresh_sample_sequenced"){
        value = 3;
    }
    if(name === "radiology"){
        value = 4;
    }
    if(name === "tykslab_plasma"){
        value = 5;
    }

    for(let i=0; i<event_series.date_relative.length; i++){
        let date = new Date(dayzero);
        date.setDate(date.getDate() + event_series.date_relative[i]);
        // if(points[points.length-1]!==undefined){
        //     // console.log(points[points.length-1], date, points[points.length-1].y, points[points.length-1].x===date);
        //     // if(points[points.length-1].x.getTime()===date.getTime()){
        //     //     value = value + 1;
        //     // }else{
        //     //     value = 1;
        //     // }
        // }
        points.push({
                    x: date, 
                    y: value, 
                    // z:z, 
                    name:event_series.name[i],
                    // label: name   
        });
    }

    const data_object =   {
        name: name,
        type:"scatter",
        connectNullData: true,
        dataPoints: points,
        toolTipContent: "{name}",
        // indexLabel: "{name}"
    };

    return data_object;
}

function create_chart2(data_points, name="event_timeline"){
    let chart = {

        axisY:{
            title: name,
            interval: 1,
            margin:20,
            // titleFontWeight: "bold",
            includeZero: true,
            titleFontSize: 12,
            // maximum: Math.max.apply(null, time_series.y)*1.1,
            // minimum: Math.min.apply(null, time_series.y.filter(x=>x!==null))*0.9,
            labelFormatter: function ( e ) {
                // console.log("e: ", e);
                if(e.value===1)
                    return leftPad("ctdna_sample", 10);
                else if(e.value===2)
                    return leftPad("fresh_sample", 10);
                else if(e.value===3)
                    return leftPad("fresh_sample_sequenced", 10);
                else if(e.value===4)
                    return leftPad("radiology", 10);  
                else if(e.value===5)
                    return leftPad("tykslab_plasma", 10);                     
                else 
                    return leftPad("", 10);
                
            },
        },
        axisX:{
            gridThickness: 1,
            tickLength: 0,
            lineThickness: 0,
            labelFormatter: function(){
            return " ";
            }
        },
        data: data_points
    };
    // console.log("points: ", points);
    return [chart];
}

/////////////////////////////////////////


function Timeline2(props) {
    let options;
    let containerProps;
    if(props.time_series!==null){
        const displayOrder = ['ca125', 'neut', 'hb', 'leuk', 'platelets'];
        const displayOrder2 = [    
                                    'ctdna_sample',   'fresh_sample', 'fresh_sample_sequenced', 
                                    'radiology', 
                                    'tykslab_plasma'
                                ];
        // console.log(props.event_series);
        const dayzero = new Date("2000-01-01");
        const min = Math.min(props.time_series["ca125"].x)
        const max = Math.max(props.time_series["ca125"].x)
        
        let datemin = new Date(dayzero);
        datemin.setDate(dayzero.getDate() + min);
        let datemax = new Date(dayzero);
        datemax.setDate(dayzero.getDate() + max);
        const charts2_points = displayOrder2.filter((d)=>props.event_series[d].date_relative.length!==0).map((d)=> {
            return create_chart2_points(dayzero, props.event_series[d], d, min, max);
        });
        const charts2 = create_chart2(charts2_points);
        const charts = displayOrder.filter((d)=>!props.time_series[d].y.every(e=>e===null)).map((d)=> {
            return create_chart(dayzero, props.time_series[d], d); 
        });
        const concat = charts2.concat(charts);

        
        // console.log("charts: \n", charts);
        options = {

            title: {
                text: "",
                fontSize: "14",
            },
            navigator:{
                // slider:{
                //     minimum: datemin,
                //     maximum: datemax,
            
                // },
                data: charts[0].data
            },
            rangeSelector:{
                buttonStyle: {
                    labelFontSize: 18,
                    labelFontStyle: "normal",
                    spacing: 5, 
                    // borderColor: "#81C5D7",
                    borderThickness: 1,
                    borderRadius: 20,

                },
                inputFields: {
                    style: {
                    fontSize: 18,
                    fontStyle: "normal",
                    }
                }
            },
            charts: concat, 
        };
        containerProps = {
            width: "100%",
            height: "800px",
            margin: "auto"
        };
    }



    return(
          <Container fluid className="py-4 px-0">
                    <Row  className="d-inline-block w-100 py-2 px-0">
                        <div style={{width: '100%', padding: '0px'}}>   
                            {props.time_series===null?<div>No TimeSeries data available for this patient</div>:
                            <CanvasJSStockChart
                                options={options}
                                containerProps = {containerProps}
                                // onRef={ref => this.stockChart = ref}
                            />}
                        </div>
                    </Row>
          </Container>
      );
  }
  export default Timeline2;