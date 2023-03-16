import {Container, Row} from 'react-bootstrap';
import Timeline2 from './TimeSeries/Timeline_2';
// import API from "../API.js";
// import { useEffect, useState } from 'react';

function PatientCard(props) {
    const displayOrder = ["patient_id", "age_at_diagnosis", "survival", "histology", "stage"];

    return(
        <Row className='mb-2'>    
            <Container fluid>
                <div>       
                    {displayOrder.map(d=><Row key={d} className="text-center text-primary font-weight-bold">{d}: {props.patient[d]}</Row>)}
                </div>  
            </Container>
            <Timeline2 time_series={props.patient.time_series}/>
        </Row>
    );


} 

export default PatientCard;