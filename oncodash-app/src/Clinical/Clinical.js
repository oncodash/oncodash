import {Container, Row, Col} from 'react-bootstrap';
import Timeline2 from './TimeSeries/Timeline_2';
import alive from '../assets/alive.svg';
import dead from '../assets/not-alive.svg';

function Clinical(props) {
    const displayOrder1 = ["id", "age", "survival", "histology", "stage", "bmi"];
    const displayOrder2 = ["cancer_in_family", "BRCA"];
    const displayOrder3 = ["strategy", "primary_outcome", "current_phase", "maintenance"];
  
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
        
            <div className="below-nav w-100 pb-5 mx-0">
                <Container className="p-0">
                                            {/* overview generale paziente */}
                        <Row className="my-5">
                            <Col>
                                <div className="text-center fw-bold">General Info</div>
                                <div className="bg-opacity-25  px-4 py-2  rounded mx-0">     
                                    {/* <Row>
                                        <Col className="d-flex justify-content-center">
                                            {props.patient.survival==="ALIVE"?<img src={alive} alt="alive"/>:<img src={dead} alt="dead"/>}  
                                        </Col>
                                    </Row> */}
                                    
                                    {
                                        displayOrder1.map(d=>
                                                <Row key={d} className="text-center text-primary font-weight-bold">
                                                    <Col className="text-end text-dark">{d.replace('', '')}:</Col> 
                                                    <Col className="text-start">{props.patient[d]} {d==="bmi"? "[kg/m^2]":""}</Col>
                                                </Row>  
                                            )
                                    }
                                </div> 
                            </Col>
                            <Col className="border-end border-start">
                                <div className="text-center fw-bold">Background</div>
                                <div className="bg-opacity-25  px-4 py-2  rounded mx-0">    
                                    
                                    {displayOrder2.map(d=>
                                                        <Row key={d} className="text-center text-primary font-weight-bold">
                                                            <Col className="text-end text-dark">{d.replace('', '')}: </Col> 
                                                            <Col className="text-start">{props.patient[d]}{props.patient[d]===true?"True": ""}{props.patient[d]===false?"False": ""}{props.patient[d]===NaN?"NaN": ""}</Col> 
                                                        </Row>)}    
                                </div> 
                            </Col>
                            <Col>
                                <div className="text-center fw-bold">Treatments</div>
                                <div className="bg-opacity-25  px-4 py-2  rounded mx-0">   
                                    
                                    {displayOrder3.map(d=>  
                                                            <Row key={d} className="text-center text-primary font-weight-bold">
                                                                <Col className="text-end text-dark">{d}:</Col> 
                                                                <Col className="text-start">{props.patient[d]}</Col> 
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