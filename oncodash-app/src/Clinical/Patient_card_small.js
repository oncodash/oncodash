import {Button, Row} from 'react-bootstrap';
// import API from "../API.js";
// import { useEffect, useState } from 'react';

function PatientCardSmall(props) {
    const displayOrder = ["id", "age", "cud_survival", "cud_histology", "cud_stage"];

    return(
        <Row className='mb-2'>
            <Button className="p-4" onClick={()=>props.getSelectedPatientCallback(props.patient.id)}>
                {displayOrder.map(d=><Row key={d} className="text-center  font-weight-bold">{d}: {props.patient[d]}</Row>)}
            </Button>
        </Row>
    );


}

export default PatientCardSmall; 