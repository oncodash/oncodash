import {LitElement, html, css} from 'lit';

var leftEnd;
var rightEnd;

function updateChart() {
    Chart.helpers.each(Chart.instances, function (instance) {
        instance.options.scales.xAxes[0].time.min = leftEnd;
        instance.options.scales.xAxes[0].time.max = rightEnd;              
        instance.update();
    });
}

class PlotElement extends LitElement {
  static properties={
    _inputData : {
                    type: Object,
                    state: true
                 },
    myName :    {
                    attribute: 'my-name', 
                },
    ctx: {},
    // myChart: {}
  };

  constructor() {
    super();
    // console.log("constructor: "+this.myName);
  }

//   updated(changedProperties){
//     super.updated(changedProperties);
//     this.updateCanvas();
//     console.log("updated");
// }




  updateCanvas(ctx){
    if(this.myChart!==undefined){
      this.myChart.destroy();
    }
    this.myChart = new Chart(ctx, {
        type: 'line',
        data: this.data,
        options: {
            // responsive: false,
            // scales: {
            //     yAxes: [{
            //         ticks: {
            //             beginAtZero:true
            //         }
            //     }]
            // },
            plugins:{
              zoom:{
                pan:{
                    mode:'x',
                    wheel:{
                      modifierKey: 'alt',
                      enabled: true,
                    }
                },
                zoom: {
                  wheel: {
                    enabled: true,
                    // modifierKey: 'shift',
                  },
                  mode: 'x',
                }
              }
            },
            interaction: {
              intersect: false,
              axis: 'x',
            },
            events:['mousemove', 'click'],
          //   plugins: {
          //     zoom: {
          //         pan: {
          //             mode: 'x',
          //             onPan: function () {
          //                 console.log("PAN");                          
          //                 leftEnd = this.myChart.getDatasetMeta(0).dataset._scale.chart.scales['x-axis-0']._table[0].time;
          //                 rightEnd = this.myChart.getDatasetMeta(0).dataset._scale.chart.scales['x-axis-0']._table[1].time;

          //                 updateChart();
          //             }
          //         },
          //         zoom: {
          //             wheel:{
          //               enabled: true,
          //             },
          //             mode: 'x',
          //             onZoom: function () {
          //                 console.log("zoom: ", this.myChart);
          //                 console.log(this.myChart);
          //                 leftEnd = this.myChart.getDatasetMeta(0).dataset._scale.chart.scales['x-axis-0']._table[0].time;
          //                 rightEnd = this.myChart.getDatasetMeta(0).dataset._scale.chart.scales['x-axis-0']._table[1].time;

          //                 updateChart();
          //             }
          //         }
          //     }
          // },

        },

    });
  }

  updated() {
    // console.log("firstUpdated: "+this.myName);
    if(this.ctx !== undefined)
    {
        this.ctx.clearRect(0,0,800,200);
    }

    if(this._inputData != null)
    {
      // this.data=JSON.parse(this._inputData);
      this.data=this._inputData;
      // console.log(this.data);
    }
    else{
      this.data = {
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
          };
          // console.log(this.data);
      }
    this.ctx = this.renderRoot.querySelector( '#myChart2' ).getContext('2d');
    this.updateCanvas(this.ctx);
  }

  render() {
    // console.log("render: "+this.myName);
    // console.log("\n\n");
    return html`
        <div style="width:100%; background-color:white">
          <!-- <div style="margin:auto; width:800px; text-align:left">Inside Render: ${this.myName}</div> -->
          <canvas style="margin:auto" id="myChart2" width="800" height="200"></canvas>
        </div>
      `;
  }
}

customElements.define('plot-elem', PlotElement);

export{PlotElement};