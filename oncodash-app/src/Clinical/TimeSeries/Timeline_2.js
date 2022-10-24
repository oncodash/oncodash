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
    // let isca125 = name === "ca125";
    let thresholds = time_series.thresholds;
    if(name === "ca125"){
        thresholds = [-10, 80000];
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
    for(let i=0; i<time_series.x.length; i++){
        let date = new Date(dayzero);
        // console.log("date: ", date)
        date.setDate(date.getDate() + time_series.x[i]);
        // console.log("date: ", date)
        // console.log("x: ", time_series.x[i])
        points.push({x: date, y: time_series.y[i]})
        //below
        if(time_series.y[i]!==null){
            if(time_series.y[i]<thresholds[0]){
                points_below.push({x: date, y: [0, time_series.y[i]]})  
            }else{  
                points_below.push({x: date, y: [null, null]})
            }
            //above
            if(time_series.y[i]>thresholds[1]){
                points_above.push({x: date, y: [time_series.y[i], Math.max.apply(null, time_series.y)*1.2]})
            }else{
                points_above.push({x: date, y: [null, null]})
            }
        }
        
        
    }
    let chart = {

        axisY:{
            title: name,
            margin:50,
            // logarithmic: isca125,
            maximum: Math.max.apply(null, time_series.y)*1.1,
            minimum: Math.min.apply(null, time_series.y.filter(x=>x!==null))*0.9,
            labelFormatter: function ( e ) {
                return leftPad(e.value, 5);
            },
            // labelFormatter: function ( e ) {
            //     return "";
            // },
            stripLines:[
                {
                    startValue:thresholds[0],
                    endValue:thresholds[1],                
                    color:"#d8d8d8",
                    label : ""+thresholds[0]+" - "+thresholds[1],
                    labelFontColor: "#a8a8a8",
                    labelPlacement: "inside",
                }
            ]
        },
        data: [
                {
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
    return chart;
}



/////////////////////////////////////////


function Timeline2(props) {
    const displayOrder = ['ca125', 'neut', 'hb', 'leuk', 'platelets'];
    const dayzero = new Date("2000-01-01");
    const charts = displayOrder.filter((d)=>!props.time_series[d].y.every(e=>e===null)).map((d)=> {
        return create_chart(dayzero, props.time_series[d], d);
    });
    
    // console.log("charts: \n", charts);
    const options = {

        title: {
            text: "",
            fontSize: "14",
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
        charts: charts, 
        navigator: {
          slider: {
            minimum: new Date("2017-12-31"),
            maximum: new Date("2018-06-30")
          }
        }
      };
      const containerProps = {
        width: "100%",
        height: "800px",
        margin: "auto"
      };



    return(
          <Container fluid className="py-4 px-0">
                    <Row  className="d-inline-block w-100 py-2 px-0">
                        <div style={{width: '100%', padding: '0px'}}>   
                            <CanvasJSStockChart
                                options={options}
                                containerProps = {containerProps}
                                // onRef={ref => this.stockChart = ref}
                            />
                        </div>
                    </Row>
          </Container>
      );
  }
  export default Timeline2;