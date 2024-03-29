import {Container, Row, Col} from 'react-bootstrap';
import Timeline2 from './TimeSeries/Timeline_2';
// import alive from '../assets/alive.svg';
// import dead from '../assets/not-alive.svg';
import StaticToggle from './StaticToggle';

function Clinical(props) {
    const displayOrder1 = ["cohort_code", "age_at_diagnosis", "bmi_at_diagnosis","previous_cancer"]; // date of diagnosis is missing
    const displayOrder2 = ["treatment_strategy", "primary_therapy_outcome", "residual_tumor_pds", "residual_tumor_ids", "maintenance_therapy", "drug_trial_name", "progression"]; 
    const displayOrder3 = ["hrd_myriad_status", "brca_mutation_status", "germline_pathogenic_variant"]; //genetic alteration with druggable target is misssing

    const dictionary = {
                        "age_at_diagnosis":"Age at diagnosis",
                        "bmi_at_diagnosis": "BMI", 
                        "previous_cancer": "Previous cancer",
                        "treatment_strategy":"Strategy",
                        "primary_therapy_outcome":"Primary outcome",
                        "progression":"Progression",
                        "hrd_myriad_status":"HRD status",
                        "brca_mutation_status":"BRCA mutation",
                        "maintenance_therapy": "Maintenance after 1st line",
                        "drug_trial_name": "Participation in drug trial",
                        "germline_pathogenic_variant": "Germ line pathogenic variants",
                        "residual_tumor_ids" : "IDS",
                        "residual_tumor_pds" : "PDS",
                        "cohort_code":"Cohort Code"
                    }
  
    // const location = useLocation();

    // const [patients, setPatients] = useState([]);
    // const [selectedPatient, setSelectedPatient] = useState({});
    // const [waitingSelected, setWaitingSelected] = useState(true);

    // const getSelectedPatient = async(patient_id)=>{
    //     try{
    //         setWaitingSelected(true);
    //         const patient = await API.getSelectedPatient(patient_id);
    //         setSelectedPatient(patient);
    //         setWaitingSelected(false);
    //     }catch(err){
    //         throw err;
    //     }
    // };

    // useEffect(()=>{
    //     const getPatients = async()=>{
    //         try{
    //             getSelectedPatient(props.patient_id);
    //         }catch(err){
    //             throw err;
    //         }
    //     };
    //         getPatients();
    //     }, []
    // );

    return(
        
            <div className="below-nav w-100 pb-5 mx-0 px-0">
                <Container className="p-0">
                                            {/* overview generale paziente */}
                        <Row className="my-5 mx-0">
                            <Col>
                                <div className="text-center fw-bold">Baseline</div>
                                
                                <div className="bg-opacity-25  px-4 py-2  rounded mx-0">     
                                    {/* <Row>
                                        <Col className="d-flex justify-content-center">
                                            {props.patient.survival==="ALIVE"?<img src={alive} alt="alive"/>:<img src={dead} alt="dead"/>}  
                                        </Col>
                                    </Row> */}
                                    
                                    {
                                        displayOrder1.map(d=>
                                                <Row key={d} className="text-center text-primary font-weight-bold">
                                                    <Col className="text-end text-dark">{dictionary[d]}:</Col> 
                                                    <Col className="text-start d-flex align-items-end">{d==="bmi_at_diagnosis"?    Math.round(props.patient[d]):  
                                                                                                            d==="previous_cancer" ? 
                                                                                                                props.patient[d]===true?<StaticToggle answer={"Yes"} label={"Yes"}/> :
                                                                                                                props.patient[d]===false?<StaticToggle answer={"No"} label={"No"}/> :
                                                                                                                                        <StaticToggle answer={"NA"} label={"NA"}/> 
                                                                                                            :props.patient[d]} 
                                                                                {d==="bmi_at_diagnosis"? "[kg/m^2]":""}</Col>
                                                </Row>  
                                            )
                                    }
                                </div> 
                            </Col>
                            <Col className="border-end border-start">
                                <div className="text-center fw-bold">Treatment</div>
                                <div className="bg-opacity-25  px-4 py-2  rounded mx-0">    
                                    
                                    {displayOrder2.map(d=>
                                                        <Row key={d} className="text-center text-primary font-weight-bold">
                                                            <Col className="text-end text-dark">{dictionary[d]}: </Col> 
                                                            <Col className="text-start d-flex align-items-end">{props.patient[d]}
                                                                                        {props.patient[d]===true?<StaticToggle answer={"Yes"} label={"Yes"}/>: ""}
                                                                                        {props.patient[d]===false?<StaticToggle answer={"No"} label={"No"}/>: ""}
                                                                                        {props.patient[d]===NaN && d!=="primary_therapy_outcome"?<StaticToggle answer={"NA"} label={"NA"}/>: ""}
                                                                                        {props.patient[d]===null && d!=="primary_therapy_outcome"?<StaticToggle answer={"NA"} label={"NA"}/>: ""}</Col> 
                                                        </Row>)}    
                                </div> 
                            </Col>
                            <Col>
                                <div className="text-center fw-bold">Basic genetics</div>
                                <div className="bg-opacity-25  px-4 py-2  rounded mx-0">   
                                    
                                    {displayOrder3.map(d=>  
                                                            <Row key={d} className="text-center text-primary font-weight-bold">
                                                                <Col className="text-end text-dark">{dictionary[d]}:</Col> 
                                                                <Col className="text-start d-flex align-items-end text-break">{d==="brca_mutation_status" || d==="germline_pathogenic_variant"? 
                                                                                                    props.patient[d] !=="No BRCA mut" && props.patient[d] !==null  && props.patient[d] !==NaN && props.patient[d] !==""? 
                                                                                                                                        <StaticToggle answer={"Yes"} label={props.patient[d].slice(0,14)}/>
                                                                                                                                        : props.patient[d] === "No BRCA mut" ?  <StaticToggle answer={"No"} label={props.patient[d]}/>
                                                                                                                                        : <StaticToggle answer={"NA"} label={props.patient[d]}/>
                                                                                            :props.patient[d]}

                                                                </Col> 
                                                            </Row>)}
                                </div> 
                            </Col>
                        </Row>
                         {/* overview generale paziente */}
                    <Row className="col-12 text-center m-0">
                        <Col className="text-center p-0">
                            {/* {waitingSelected===true ? "loading..." :  */}
                                <>
                                    {/* <PatientCard patient={props.patient} /> */}
                                    {/* <Button className="pe-auto mb-1">{selectedPatient.toString()}</Button>*/}
                                    <Timeline2 time_series={props.patient.time_series} event_series={props.patient.event_series}/> 
                                </>
                            {/* } */}
                        </Col>
                    </Row>
                </Container>
            </div>
    );


}

export default Clinical;