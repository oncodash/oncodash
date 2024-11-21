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
    barY.fill(Math.max(...y)*2)
    let barY_neg = new Array(y.length);
    barY_neg.fill(-10)
    // console.log("barY: ", barY);
    let backColors = barY.map(x=>'rgba(255, 255, 255, 0)');
    let hoverColors = barY.map(x=>'rgba(0, 0, 0, 0.5)');
    backColors[hoverIndex] = 'rgba(0, 0, 255, 0.5)';
  
    // console.log(backColors[hoverIndex]);
  
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
                              //   {
                              //     type: 'bar',
                              //     data: barY_neg,
                              //     backgroundColor: backColors,
                              //     hoverBackgroundColor:hoverColors,
                              //     barThickness: 10,
                              //     spanGaps: true
                              // },     
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

  const plot_utils = {basePlot2};
  export default plot_utils;  