// import { Chart, TimeSeriesScale } from 'chart.js';
import {LitElement, html, css} from 'lit';


/** Given a time series object it creates a child node (plot-elements) which plots the data
 * 
 */
class PlotManager extends LitElement {


  static properties={
    time_series : {
                  attribute: 'time-series',
                  converter: (value, type) => {
                    return JSON.parse(value);
                  },

  
                },                
    myName : {attribute: 'my-name'}
  };

  constructor() {
    super();
      this.time_series = {'nothing':{'x':[0], 'y':[0]}};                    
  }

// /**
//    * 
//    * @param {*} label name of time TimeSeries
//    * @param {*} x     x axis values
//    * @param {*} y     y axis values
//    * @returns         Chart.js configuration to be embedded in the data field of Chart.js object
//    */
//   basePlot(label, x, y){



//       let template = `
//         {
//             "labels": ${JSON.stringify(x)},
//             "datasets": [{
//                         "label": ${JSON.stringify(label)},
//                         "data": ${JSON.stringify(y)},
//                         "fill":false,
//                         "backgroundColor": [
//                             "rgba(255, 99, 132, 0.2)"

//                         ],
//                         "borderColor": [
//                             "rgba(0,100,100,1)"
//                         ],
//                         "borderWidth": 1
//                     }]
//         }`;
//       return template;
//   }

// /**
//    * 
//    * @param {*} label name of time TimeSeries
//    * @param {*} x     x axis values
//    * @param {*} y     y axis values
//    * @returns         Chart.js configuration to be embedded in the data field of Chart.js object
//    */
//   basePlot2(label, x, y){
//     const down = (ctx, value) => ctx.p1.parsed.y > 5 ? value : "rgba(0,255,0,1)";
//     let template = 
//                     {
//                         labels: x,
//                         datasets: [{
//                                     label: label,
//                                     data: y,
//                                     fill:false,
//                                     // interaction: {
//                                     //   intersect: false
//                                     // },
//                                     // radius: 0,
//                                     // backgroundColor: [
//                                     //     "rgba(100, 0, 0, 0.8)"
//                                     // ],
//                                     borderColor: [
//                                       "rgba(100, 0, 0, 0.8)"
//                                   ],
//                                     // borderWidth: 1,
//                                     segment:{
//                                                 borderColor: ctx => down(ctx, "rgba(255,0,0,1)")
//                                     },

//                                     spanGaps: true

//                                 }]
//                     };
//     // console.log(template);
//     return template;
// }  

  render() {
    if(this.time_series != undefined)
    {
      return html`
        <div style="width:100%; background-color:lightblue">

          <plot-elements  ._inputData=${this.time_series}></plot-elements>                                                             
        </div>
        `;
    }
    else return html``;
  }
}

customElements.define('plot-manager', PlotManager);
  