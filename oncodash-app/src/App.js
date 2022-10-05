// import logo from './logo.svg';
import './App.css';
import Row from 'react-bootstrap/Row';
import 'bootstrap/dist/css/bootstrap.min.css';
import MyNavBar from './MyNavBar.js';
import Clinical from './Clinical/Clinical.js';
import Explainer from './Explainer/Explainer.js';
// import {useState, useEffect} from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import MyMain from "./MyMain"
import Footer from "./Footer"
import { useEffect, useState } from 'react';
import API from "./API";
import PatientView from './PatientView';


function App() {

  const [patients, setPatients] = useState([]);
//   const [selectedPatient, setSelectedPatient] = useState({});
  const [waiting, setWaiting] = useState(true);
//   const [waitingSelected, setWaitingSelected] = useState(true);

//   const getSelectedPatient = async(patient_id)=>{
//       try{
//           setWaitingSelected(true);
//           const patient = await API.getSelectedPatient(patient_id);
//           setSelectedPatient(patient);
//           setWaitingSelected(false);
//       }catch(err){
//           throw err;
//       }
//   };

  useEffect(()=>{
      const getPatients = async()=>{
          try{
              setWaiting(true);
              const patients = await API.getPatients();
              setPatients([...patients]);
              setWaiting(false);
            //   getSelectedPatient(patients[0].id);
              return patients;
          }catch(err){
              throw err;
          }
      };
          getPatients();
      }, []
  );


  return (
    <Router>
        <MyNavBar/>
        <Row className="vheight-100  m-0">
            <Routes>
                <Route path="/patientview"   element={<PatientView/>}   />
                <Route path="/clinical"   element={<Clinical/>}   />
                <Route path="/explainer"  element={<Explainer/>}  />
                <Route path="/"           element={<MyMain waiting={waiting} patients={patients}/>}    />
            </Routes>
        </Row>
        <Footer/>
    </Router>
  );
}

export default App;
