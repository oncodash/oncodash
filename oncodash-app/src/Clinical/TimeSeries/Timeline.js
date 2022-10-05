import {Container, Row} from 'react-bootstrap';
// import {basePlot2} from './plot_utils.js';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import zoomPlugin from "chartjs-plugin-zoom";

/////////////////////////////////////////

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    zoomPlugin,
  );


/////////////////////////////////////////
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    pan:{
        mode:'x',
        enabled: true,
    },
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
          sensitivity: 0.1,
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
  };

  const createData = (x, y, name)=>{
    // console.log("name ", name);
    // console.log("x ", x);
    // console.log("y ", y);
    return {
                labels: x, //x,
                datasets: [
                    {
                        label: name,
                        data: y, //y,
                        borderColor: 'rgb(0, 0, 0)',
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        spanGaps: true,
                    } 
                ]
            }
  };  


// import {useState} from 'react';

function Timeline(props) {

    return(
          <Container fluid>
                {
                    Object.entries(props.time_series).map(([k, v])=> 
                    <Row key={k} className="d-inline-block w-100 py-2">
                        <div style={{width: '100%', height: '150px'}}>   
                            <Line type="line" className="my-0 mx-auto w-100" options={options} data={createData(v.x, v.y, k)}/>
                        </div>
                    </Row>)
                }
          </Container>
      );
  }
  export default Timeline;