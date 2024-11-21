import {LitElement, html, css} from 'lit';

var leftEnd;
var rightEnd;
var myCharts = [];
var ctx = [];
var thresholds = [];
var ys = [];
// var hoverIndex=0;



/**
 * 
 * @param {*} label       name of time TimeSeries
 * @param {*} x           x axis values
 * @param {*} y           y axis values
 * @param {*} colors 
 * @param {*} thresholds  thresholds of y valueString
 * @param {*} hoverIndex  index of the element under the cursor
 * @returns               Chart.js configuration to be embedded in the data field of Chart.js object
 */
function basePlot2(label, x, y, colors, thresholds, hoverIndex){

  let up = (ctx, colors, thresholds) => {
    let i;
    for(i=1; i<thresholds.length; i++){
      if(ctx.p1.parsed.y < thresholds[i]){
        // console.log(i, "---y: ", ctx.p1.parsed.y, " --- : ", thresholds[i]);
        return colors[i];
      }
      
    }
    return colors[i];
    // ctx.p1.parsed.y > 5 ? value : "rgba(255, 173, 96,1)"
    
  };

  let down = (ctx, colors, thresholds) => {
    let i;
    for(i=0; i<thresholds.length-1; i++){
      if(ctx.p1.parsed.y < thresholds[i]){
        // console.log(i, "---y: ", ctx.p1.parsed.y, " --- : ", thresholds[i]);
        return colors[i];
      }
      
    }
    return colors[i];
    // ctx.p1.parsed.y > 5 ? value : "rgba(255, 173, 96,1)"
    
  };  


  // let getMaxVec = (n, val) =>{
  //   let i;
  //   let vec = [];
  //   for(i=0; i< n; i++){
  //     vec.push(val);
  //   }
  //   return vec
  // }
  
  // let barY = getMaxVec(y.length, max(y));
  let barY = new Array(y.length);
  barY.fill(Math.max(...y))
  console.log("barY: ", barY);
  let backColors = barY.map(x=>'rgba(255, 255, 255, 0)');
  let hoverColors = barY.map(x=>'rgba(0, 0, 0, 0.5)');
  backColors[hoverIndex] = 'rgba(0, 0, 255, 0.5)';

  console.log(backColors[hoverIndex]);

  let template = 
                  {
                      labels: x,
                      datasets: [
                                {
                                  type: 'bar',
                                  data: barY,
                                  backgroundColor: backColors,
                                  hoverBackgroundColor:hoverColors,
                                  barThickness: 10,
                                  spanGaps: true
                              },        
                              {
                                  type: 'line',
                                  label: label,
                                  data: y,
                                  fill:{
                                    value: 20000,
                                  },

                                  segment:{ 
                                              borderColor: "rgba(0, 0, 0, 0.5)",
                                              backgroundColor: ctx => up(ctx, colors, thresholds)
                                  },

                                  spanGaps: true

                              },
                              {
                                type: 'line',
                                label: '',
                                data: y,
                                fill:{
                                  value: 0,
                                },

                                segment:{
                                            borderColor: "rgba(0, 0, 0, 0.5)",
                                            backgroundColor: ctx => down(ctx, colors, thresholds)
                                },

                                spanGaps: true

                            },         
               
                              ]
                  };
  // console.log(template);
  return template;
}  

/** synchronize the zoom of the charts
 * 
 */
function updateChart() {
    myCharts.forEach(x=>{
        x.options.scales.x.min = leftEnd;
        x.options.scales.x.max = rightEnd;
        x.update('none');
        // console.log(x._metasets[0].label, ": ", x);
    });
}

/** plots time series
 * 
 */
class PlotElements extends LitElement {
  static properties={
    height      : {
                    state:true,
                  },
    _inputData : {
                    type: Object,
                    state: true,

                 },
    myName :    {
                    attribute: 'my-name', 
                },
    hoverIndex: {state:true},
    ctx: [],
    myCharts: [],
    // myChart: {}
  };

  constructor() {
    super();
    this.height= [100, 100, 200, 200, 100];
    this.hoverIndex=0;
  }



  /** draw on every canvas the time series plot
   * 
   * @param {*} ctx vectos of canvas contexts
   */
  updateCanvas(ctx){

    if(myCharts!==undefined)
      if(myCharts.length!==0)
        myCharts.forEach((x, i) => {
              if(x!==undefined){
                x.destroy();
              }
            }
          );
    myCharts = ctx.map((ctx_i, i)=>{
      return new Chart(ctx_i, {
        data: this.data[i],
        options: {
          onClick: (e, elements) =>{
            this.hoverIndex = elements[1].index
          },

            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            scales:{
              y:{
                min: Math.min(...ys[i]) - 5,
                max: Math.max(...ys[i]) + 5,
                ticks:{
                  callback: function(value){
                    let valueString = value.toString()
                    let len = valueString.length;
                    let buffer = [];
                    let i;
                    for(i=0; i<5-len;i++)
                      buffer.push('_');
                    for(i=0; i<len; i++){
                      buffer.push(valueString[i]);
                    }
                    buffer = buffer.join("");
                    return buffer;
                  }
                }
              },
              x:{
                min: leftEnd,
                max: rightEnd
              }
            },

            interaction: {
              intersect: false,
              axis: 'x',

            },
            plugins: {
              tooltip:{
                  enabled: false,
              },
              legend:{
                display: false,
              },
              filler:{
                  propagate: true,
              },
              zoom: {
                  limits:{
                    x:{
                      minRange: 30,
                    }
                  },
                  pan: {
                      enabled: false,
                      mode: 'x',
                      onPan: function () {                         
                          leftEnd   = myCharts[i]._metasets[1]._scaleRanges['xmin'];
                          rightEnd  = myCharts[i]._metasets[1]._scaleRanges['xmax'];
                          updateChart();
                      },
                  },
                  zoom: {
                      wheel:{
                        enabled: true,
                      },
                      mode: 'x',
                      onZoom: function () { 
                          leftEnd   = myCharts[i]._metasets[1]._scaleRanges['xmin'];
                          rightEnd  = myCharts[i]._metasets[1]._scaleRanges['xmax'];
                          updateChart();
                      },

                  }
              },
              

            
          },
          }})});
  }


  updated() {
    if(this._inputData != null)
    {
      this.data=Object.entries(this._inputData).map(([k, v])=> basePlot2(k, v.x, v.y, v.colors, v.thresholds, this.hoverIndex));
      thresholds=Object.entries(this._inputData).map(([k, v])=> v.thresholds);
      ys=Object.entries(this._inputData).map(([k, v])=> v.y);
    }
    else{
      this.data = [{
        labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
        datasets: [{
                    label: '# of Votes',
                    data: [12, 19, 3, 5, 2, 3],
                    fill:true,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
          }];
      }
    
    if(this._inputData !== undefined)
    {
      let i = 0;
      ctx = Object.entries(this._inputData).map(([k, v])=> 
                    {
                      let id = i;
                      i = i + 1;
                      return this.renderRoot.querySelector( `#chart${id}` ).getContext('2d');
                      
                    });
    }
    
    this.updateCanvas(ctx);
  }
  
  /** return the html code with the canvas of the time series plot
   * 
   * @returns 
   */
  render() {
        let i = 0;

        if(this._inputData!==undefined){
          return html`
                      ${Object.entries(this._inputData).map(([k, v])=> {
                          let name = `chart${i}`;
                          let divID = `div${i}`;
                          i = i+1;
                          return html`
                              <div id=${divID} style="width:100%; background-color:white; overflow:auto; height:${this.height[i-1]}px">
                                  <div style="margin:auto; width:20%; float:left; display:table; height:100%">
                                      <div style="display:table-cell; vertical-align:middle; text-align:center">
                                          <div> ${k} </div>
                                          <div> ${v.y[this.hoverIndex]} </div>
                                      </div>
                                  </div>
                                  <div style="margin:auto; width:70%; float:left; height:100%">
                                    <canvas style="margin:auto; height:100%; width:100%" id=${name} width="800" height="${this.height[i-1]}"></canvas>
                                  </div>
                                  <div style="margin:auto; width:10%; float:left; display:table; height:100%">
                                      <div style="display:table-cell; vertical-align:middle; text-align:center">
                                          <div style="width:100%">
                                            <button >↑</button>
                                          </div>
                                          <div style="width:100%">
                                            <button >X</button>
                                          </div>
                                          <div style="width:100%">
                                            <button >↓</button>
                                          </div>  
                                      </div>
                                  </div>
                              </div>
                          `;
                      })}               
          `;
        }else{
          return html ``;
        }
  }
}

customElements.define('plot-elements', PlotElements);

export{PlotElements};