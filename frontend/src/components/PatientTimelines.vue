<template>
  <div class="demo-label">
    Dates are not real for demonstration purpose
  </div>
  <CanvasJSStockChart
    :options="chartOptions()"
    :style="chartStyle"
    @stockchart-ref="chartRef" />
</template>

<script>
import { nextTick } from 'vue';
import { Patient } from '../models/Patient';

/**
 * IMPORTANT
 * This component must use the old Options API structure of Vue.js
 * since CanvaJS does not support the Composition API.
 */
export default {
  props: {
    patient: {
      type: [Patient, null],
      required: true
    }
  },
  data() {
    return {
      chartStyle: {
        height: "700px"
      },
      timelinesOrder: [
        'ca125',
        'neut',
        'hb',
        'leuk',
        'platelets'
      ],
      eventsOrder: [
        'clinical',
        'chemotherapy',
        'ctdna_sample',
        'fresh_sample',
        'fresh_sample_sequenced',
        'radiology',
        'tykslab_plasma'
      ],
      pointsColorDict: {
        "diagnosis": ["orange", "square"],
        "death": ["black", "square"],
        "last_date_of_primary_therapy": ["red", "triangle"],

        "ctdna": ["brown", "circle"],
        "fresh_sample": ["green", "circle"],
        "fresh_sample_sequenced": ["grey", "circle"],
        "radiology": ["red", "circle"],
        "tykslab_plasma": ["purple", "circle"],
        "None": ["black", "triangle"],

        "chemotherapy_dose": ["purple", "circle"],
        "carboplatin": ["grey", "circle"],
        "gemcitabine": ["purple", "circle"],
        "paclitaxel": ["green", "circle"],
        "doxorubicin": ["orange", "circle"],
        "docetaxel": ["red", "circle"],
        "pld": ["yellow", "circle"],
        "bevacizumbab": ["blue", "circle"],
        "topotecan": ["brown", "circle"],
        "pembrolizumbab": ["black", "circle"]
      }
    }
  },
  methods: {
    chartRef: async function (chartInstance) {
      // Needs to re-render the chart after first render due to some
      // weird display bug
      await nextTick()
      chartInstance.render()
    },

    chartOptions: function () {
      const dayzero = new Date("2000-01-01");
      const min = Math.min(this.patient.time_series["ca125"].x)
      const max = Math.max(this.patient.time_series["ca125"].x)

      let datemin = new Date(dayzero);
      datemin.setDate(dayzero.getDate() + min);

      let datemax = new Date(dayzero);
      datemax.setDate(dayzero.getDate() + max);

      const eventsPoints = this.eventsOrder
        .filter((d) => this.patient.event_series[d].date_relative.length !== 0)
        .map((d) => {
          return this.createEventsPoints(dayzero, this.patient.event_series[d], d, min, max);
        });

      const eventsTimeline = this.createEventsTimeline(eventsPoints);

      const timelines = this.timelinesOrder
        .filter((d) => this.patient.time_series[d].sparse_x.length !== 0)
        .map((d) => {
          return this.createTimeline(dayzero, this.patient.time_series[d], d);
        });

      return {
        charts: [
          ...eventsTimeline,
          ...timelines
        ],
        title: {
          text: "",
          fontSize: "14",
        },
        navigator: {
          data: timelines[0].data,
          height: 50,
        },
        rangeSelector: {
          buttonStyle: {
            labelFontSize: 18,
            labelFontStyle: "normal",
            spacing: 5,
            borderThickness: 1,
            borderRadius: 20,
          },
          inputFields: {
            startValue: new Date("1999-12-1"),
            style: {
              fontSize: 18,
              fontStyle: "normal",
            }
          }
        },
      }
    },

    leftPad: function (number, targetLength) {
      var output = number + '';
      while (output.length < targetLength) {
        output = ' ' + output;
      }
      return output;
    },

    createTimeline: function (dayzero, time_series, name) {
      let points = [];
      let points_below = [];
      let points_above = [];
      let derivative = [];
      const derivative_threshold = 50;
      let thresholds = time_series.thresholds;
      if (name === "ca125") {
        thresholds = [-10, 10000]
        let diff_x;
        let diff_y;
        for (let i = 1; i < time_series.sparse_x.length; i++) {
          diff_y = time_series.sparse_y[i] - time_series.sparse_y[i - 1];
          diff_x = Math.abs(time_series.sparse_x[i] - time_series.sparse_x[i - 1]);
          derivative.push(diff_y / diff_x);
        }
      }
      if (name === "hb") thresholds = [117, 155]
      if (name === "leuk") thresholds = [3.4, 8.2]
      if (name === "neut") thresholds = [1.5, 6.7]
      if (name === "platelets") thresholds = [150, 360]

      let max_y = Math.max.apply(null, time_series.y) * 1.2;
      for (let i = 0; i < time_series.x.length; i++) {
        let date = new Date(dayzero);
        date.setDate(date.getDate() + time_series.x[i]);
        points.push({ x: date, y: time_series.y[i] })
        if (name !== "ca125") {
          if (time_series.y[i] !== null) {
            if (time_series.y[i] < thresholds[0]) {
              points_below.push({ x: date, y: [0, time_series.y[i]], markerType: "circle", markerSize: 10 })
            } else {
              points_below.push({ x: date, y: [null, null] })
            }
            if (time_series.y[i] > thresholds[1]) {
              points_above.push({ x: date, y: [time_series.y[i], max_y], markerType: "circle", markerSize: 10 })
            } else {
              points_above.push({ x: date, y: [null, null] });
            }
          }
        }
      }

      if (name === "ca125") {
        let k = -1;
        for (let i = 0; i < time_series.x.length; i++) {
          let date = new Date(dayzero);
          date.setDate(date.getDate() + time_series.x[i]);
          if (time_series.sparse_x.includes(time_series.x[i])) {
            k = k + 1;

            if (k > 0) {
              let previous_day = new Date(dayzero);
              previous_day.setDate(previous_day.getDate() + time_series.sparse_x[k - 1]);

              if (derivative[k - 1] > derivative_threshold) {
                points_above.push({ x: previous_day, y: [time_series.sparse_y[k - 1], max_y] });
                points_above.push({
                  x: date, y: [time_series.y[i], max_y],
                });
                points_below.push({ x: date, y: [null, null] });
              } else {
                points_above.push({ x: date, y: [null, null] })
              }

              if (derivative[k - 1] < -derivative_threshold) {
                points_below.push({ x: previous_day, y: [-100, time_series.sparse_y[k - 1]] });
                points_below.push({
                  x: date, y: [-100, time_series.y[i]],
                });
                points_above.push({ x: date, y: [null, null] });
              } else {
                points_below.push({ x: date, y: [null, null] })
              }
            }
          }
        }
      }

      let axisXtemplate = {
        gridThickness: 1,
        tickLength: 0,
        lineThickness: 1,
        labelFormatter: function () {
          return " ";
        }
      };

      let stripLinesTemplate = [
        {
          startValue: thresholds[0],
          endValue: thresholds[1],
          color: "#d8d8d8",
          label: "" + thresholds[0] + " - " + thresholds[1],
          labelFontColor: "grey",
          labelPlacement: "outside",
          labelAlign: "far",
          showOnTop: false
        }
      ];

      let stripLines = name !== "ca125" ? stripLinesTemplate : [];
      let axisX = name !== "platelets" ? axisXtemplate : { gridThickness: 1 };

      let chart = {
        axisY: {
          title: name,
          margin: 20,
          titleFontSize: 14,
          maximum: Math.max.apply(null, time_series.y) * 1.1,
          minimum: Math.min.apply(null, time_series.y.filter(x => x !== null)) * 0.9,
          labelFormatter: (e) => {
            return this.leftPad(e.value, 10);
          },
          stripLines: stripLines
        },
        axisX: axisX,
        data: [
          {
            name: name,
            type: "line",
            connectNullData: true,
            dataPoints: points,
          },
          {
            type: "rangeArea",
            dataPoints: points_below,
          },
          {
            type: "rangeArea",
            dataPoints: points_above,
          }
        ]
      };

      return chart;
    },

    createEventsPoints: function (dayzero, event_series, name, min, max) {
      let points = [];
      let value = 1;

      if (name === "clinical") value = 1
      if (name === "chemotherapy") value = 2
      if (name === "ctdna") value = 3
      if (name === "fresh_sample") value = 4
      if (name === "fresh_sample_sequenced") value = 5
      if (name === "radiology") value = 6
      if (name === "tykslab_plasma") value = 7

      for (let i = 0; i < event_series.date_relative.length; i++) {
        let date = new Date(dayzero)
        date.setDate(date.getDate() + event_series.date_relative[i])

        if (event_series.name[i] === "None") continue

        points.push({
          x: date,
          y: value,
          name: event_series.name[i],
          markerColor: name !== "clinical" && name !== "chemotherapy"
            ? this.pointsColorDict[name][0]
            : this.pointsColorDict.hasOwnProperty(event_series.name[i])
              ? this.pointsColorDict[event_series.name[i]][0]
              : "blue",

          markerType: name !== "clinical" && name !== "chemotherapy"
            ? this.pointsColorDict[name][1]
            : this.pointsColorDict.hasOwnProperty(event_series.name[i])
              ? this.pointsColorDict[event_series.name[i]][1]
              : "triangle",
        })
      }

      const data_object = {
        name: name,
        type: "scatter",
        connectNullData: true,
        dataPoints: points,
        toolTipContent: "{name}",
      };

      return data_object
    },

    createEventsTimeline: function (data_points) {
      return [
        {
          data: data_points,
          axisY: {
            title: "Events timeline",
            interval: 1,
            margin: 20,
            includeZero: true,
            titleFontSize: 12,
            labelFormatter: (e) => {
              if (e.value === 1) return this.leftPad("clinical", 22)
              else if (e.value === 2) return this.leftPad("chemotherapy", 22)
              else if (e.value === 3) return this.leftPad("ctdna_sample", 22)
              else if (e.value === 4) return this.leftPad("fresh_sample", 22)
              else if (e.value === 5) return this.leftPad("fresh_sample_sequenced", 22)
              else if (e.value === 6) return this.leftPad("radiology", 22)
              else if (e.value === 7) return this.leftPad("tykslab_plasma", 22)
              else return this.leftPad("", 22)
            },
            viewportMinimum: 0,
            viewportMaximum: 7
          },
          axisX: {
            gridThickness: 1,
            tickLength: 0,
            lineThickness: 0,
            labelFormatter: function () {
              return " "
            }
          }
        }
      ]
    }
  }
}
</script>

<style>
.demo-label {
  text-align: end;
  color: orangered;
  padding: 8px;
}
</style>
