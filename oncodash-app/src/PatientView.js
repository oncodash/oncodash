import { Row, Container, Col    } from 'react-bootstrap';
import Clinical from './Clinical/Clinical';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import {useLocation, Navigate} from 'react-router-dom';
import API from "./API.js";
import { useEffect, useState } from 'react';
// import alive from './assets/alive.svg';
// import dead from './assets/not-alive.svg';
import ExplAIner from './Explainer/Explainer';
import Genomic from './Genomic/Genomic';
import Extra from './Extra/Extra';
import { ArrowClockwise } from 'react-bootstrap-icons';
import PatientSummary from './PatientSummary';

function PatientView(props) {
    // const displayOrder = ["id", "age", "cud_survival", "cud_histology", "cud_stage"];
    // const displayOrder = ["id", "age", "cud_survival", "cud_histology", "cud_stage"];
    // const displayOrder = ["id", "age", "cud_survival", "cud_histology", "cud_stage"];

    const location = useLocation();
    const { state } = location;

    const [selectedPatient, setSelectedPatient] = useState({});
    const [waitingSelected, setWaitingSelected] = useState(true);
    // const [selectedTab, setSelectedTab] = useState("clinical");

    const getSelectedPatient = async(token, patient_id)=>{
        try{
            setWaitingSelected(true);
            let patient = await API.getSelectedPatient(token, patient_id);
            const genomic = await API.getGenomic(token, patient_id);
            patient.genomic = genomic;
            setSelectedPatient(patient);
            setWaitingSelected(false);
        }catch(err){
            throw err;
        }
    };

    useEffect(()=>{
        const getPatients = async()=>{
            if(props.token!=="" && props.token!==undefined && props.token!=="undefined"){
                try{
                    getSelectedPatient(props.token, state.patient_id);
                }catch(err){
                    throw err;
                }
            }
        };
            getPatients();
        }, [props.token, state.patient_id]   
    );

    return(
            state === null ? <Navigate to="/" relative={-1}/> : state.patient_id === undefined || props.token==="" ? <Navigate to="/" relative={-1}/> :
            <div className="below-nav w-100 px-5 mx-0 my-5">
                
                <Container style={{marginTop:"100px"}}>
                    {/* <Row>
                        <Col className="mb-5 py-2 fs-2 text-center bg-secondary bg-opacity-25 border-bottom">
                            Patient View
                        </Col>
                    </Row> */}
                    {waitingSelected === true ? 
                        <Row>
                            <Col className="mt-5 d-flex justify-content-center">
                                <ArrowClockwise size={50}/>
                            </Col>
                        </Row>
                    :
                    <>
                        <Row className="patientHeader mt-3">
                            <Col>
                                PATIENT {selectedPatient.patient_id}
                            </Col>
                        </Row>
                        <PatientSummary patient={selectedPatient}/>
                        <Row className='fs-5'>
                            <Tabs   
                                className="border-secondary px-0"
                                defaultActiveKey="clinical"
                                id="databrowser"
                                transition={false}
                                fill
                            >
                                <Tab eventKey="clinical" title="CLINICAL DATA">
                                    <Row className="bg-white bottomBorderRadius">
                                        {state !== undefined? <Clinical patient={selectedPatient}></Clinical>: "" }
                                    </Row>
                                </Tab>
                                <Tab eventKey="genomic" title="GENOMIC DATA">
                                    <Row className="bg-white bottomBorderRadius">
                                        {state !== undefined? <Genomic patient={selectedPatient}></Genomic>: "" }
                                    </Row>
                                </Tab>
                                <Tab eventKey="explainer" title="EXPLAINER">
                                    <Row className="bg-white bottomBorderRadius">
                                        {state !== undefined? <ExplAIner patient={selectedPatient}></ExplAIner>: "" }
                                    </Row>
                                </Tab>      
                                <Tab eventKey="extra" title="OTHER">
                                    <Row className="bg-white bottomBorderRadius">
                                        {state !== undefined? <Extra patient={selectedPatient}></Extra>: "" }
                                    </Row>
                                </Tab>                                   
                            </Tabs>
                        </Row>

                    </>
                }
                </Container>
            </div>
        

      );
  }
  export default PatientView;