import {Row, Col} from 'react-bootstrap';
import { PersonCheck, PersonX } from 'react-bootstrap-icons';
import StaticToggle from './Clinical/StaticToggle';

function PatientSummary(props) {
    const displayOrder1 = ["patient_id", "cohort_code", "age_at_diagnosis", "stage"];
    const displayOrder2 = ["survival", "current_treatment_phase", "progression"]; 
    const displayOrder3 = ["paired_fresh_samples_available", "platinum_free_interval", "days_to_death", "followup_time"]; 
    const dictionary = {
        "patient_id":"Patient ID",
        "cohort_code":"Cohort Code",
        "age_at_diagnosis":"Age",
        "stage":"Stage",
        "survival":"Status",
        "progression":"Progression",
        "paired_fresh_samples_available":"PFS",
        "platinum_free_interval":"PFI",
        "days_to_death":"OS",
        "current_treatment_phase": "current phase",
        "followup_time" : "F-UP"
    };
    const survcolor = props.patient["survival"] === "alive" ? "green":"red"

    return(
        <Row style={{fontWeight:"bold",boxShadow:"5px 5px 20px rgba(0, 0, 0, 0.2)"}} className='bg-white my-5 py-3'>    
            <Col className='d-flex justify-content-center align-items-center'>
                <div  style={{   "padding": "10px",
                                "borderStyle": "solid",
                                "borderRadius": "50%",
                                "borderColor": survcolor,
                                "color": survcolor,
                            }}>
                    {props.patient["survival"] === "alive" ?<PersonCheck size={60} />:<PersonX size={60} />}
                </div>
            </Col>

            <Col>
                    <div className="bg-opacity-25  px-4 py-2  rounded mx-0">    
                        {
                            displayOrder1.map(d=>
                                    <Row key={d} className="text-center text-primary font-weight-bold">
                                        <Col className="text-end text-dark">{dictionary[d]}:</Col> 
                                        <Col className="text-start">{props.patient[d]}</Col>
                                    </Row>  
                                )
                        }
                    </div> 
            </Col>

            <Col>
            <div className="bg-opacity-25  px-4 py-2  rounded mx-0">    
                        {displayOrder2.map(d=>
                                <Row key={d} className="text-center text-primary font-weight-bold">
                                    <Col className="text-end text-dark">{dictionary[d]}: </Col> 
                                    <Col className="text-start d-flex align-items-center">{props.patient[d]}
                                                                {props.patient[d]===true?<StaticToggle answer={"Yes"} label={"Yes"}/>: ""}
                                                                {props.patient[d]===false?<StaticToggle answer={"No"} label={"No"}/>: ""}
                                                                {props.patient[d]===NaN && d==="progression"?<StaticToggle answer={"NA"} label={"NA"}/>: ""}
                                                                {props.patient[d]===null && d==="progression"?<StaticToggle answer={"NA"} label={"NA"}/>: ""}</Col> 
                                </Row>)}    
                        </div>           
            </Col>

            <Col>
                     <div className="bg-opacity-25  px-4 py-2  rounded mx-0">    
                        {
                            displayOrder3.map(d=>
                                    <Row key={d} className="text-center text-primary font-weight-bold">
                                        <Col className="text-end text-dark">{dictionary[d]}:</Col> 
                                        <Col className="text-start">{props.patient[d]===null?'NA':props.patient[d]}</Col>
                                    </Row>  
                                )
                        }
                    </div> 
            </Col>
        </Row>
    );


} 

export default PatientSummary;