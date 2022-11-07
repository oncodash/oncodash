import { Row, Container, Col    } from 'react-bootstrap';
import Clinical from './Clinical/Clinical';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import {useLocation, Navigate} from 'react-router-dom';
import API from "./API.js";
import { useEffect, useState } from 'react';
import alive from './assets/alive.svg';
import dead from './assets/not-alive.svg';
import ExplAIner from './Explainer/Explainer';
import Genomic from './Genomic/Genomic';
import Extra from './Extra/Extra';
import { ArrowClockwise } from 'react-bootstrap-icons';

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
            const patient = await API.getSelectedPatient(token, patient_id);
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
        }, []   
    );

    return(
            state === null ? <Navigate to="/" relative={-1}/> : state.patient_id === undefined || props.token==="" ? <Navigate to="/" relative={-1}/> :
            <div className="below-nav w-100 px-5 mx-0 my-5">
                
                <Container>
                    {/* <Row>
                        <Col className="mb-5 py-2 fs-2 text-center bg-secondary bg-opacity-25 border-bottom">
                            Patient View
                        </Col>
                    </Row> */}
                    {waitingSelected === true ? 
                        <Row>
                            <Col className="d-flex justify-content-center">
                                <ArrowClockwise size={50}/>
                            </Col>
                        </Row>
                    :
                    <>

                        <Row className='fs-5'>
                            <Tabs   
                                className="border-bottom border-secondary"
                                defaultActiveKey="clinical"
                                id="databrowser"
                                transition={false}
                                fill
                            >
                                <Tab eventKey="clinical" title="Clinical data">
                                    <Row className="px-2">
                                        {state !== undefined? <Clinical patient={selectedPatient}></Clinical>: "" }
                                    </Row>
                                </Tab>
                                <Tab eventKey="genomic" title="Genomic data">
                                    <Row className="px-2">
                                        {state !== undefined? <Genomic patient={selectedPatient}></Genomic>: "" }
                                    </Row>
                                </Tab>
                                <Tab eventKey="explainer" title="ExplAIner">
                                    <Row className="px-2">
                                        {state !== undefined? <ExplAIner patient={selectedPatient}></ExplAIner>: "" }
                                    </Row>
                                </Tab>      
                                <Tab eventKey="extra" title="Extra">
                                    <Row className="px-2">
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