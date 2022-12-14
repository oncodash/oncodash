// import logo from './logo.svg';
import './App.css';
import Row from 'react-bootstrap/Row';
import 'bootstrap/dist/css/bootstrap.min.css';
import MyNavBar from './MyNavBar.js';
// import {useState, useEffect} from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import MyMain from "./MyMain"
import Footer from "./Footer"
import { useEffect, useState } from 'react';
import API from "./API";
import PatientView from './PatientView';
import { useCookies } from 'react-cookie';


function App() {

  const [cookie, setcookie] = useCookies();
  const [logged, setLogged] = useState(false);
  const [token, setToken] = useState("");
  const [patients, setPatients] = useState([]);
  const [filter, setFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [waiting, setWaiting] = useState(true);

  const logoutCallback = async () => {
    await API.logOut(token);
    setLogged(false);
    setToken("");
    setPatients([]);
    setWaiting(true);
    setcookie('token', undefined);
    // clean up everything
  }

  const loginCallback = async (email, password) => {
    try {
      const res = await API.logIn(email, password)
      // alert(`Token, ${res.token}!`);  
      setLogged(true);
      setToken(res.token);
      setcookie('token', res.token);
      // setDirty(true);
      return false;
    } catch(err) {
      throw err;
    }
  }

  useEffect(()=>{
    if(cookie["token"]!==undefined && cookie["token"]!=="undefined"){
      setToken(cookie["token"]);
      setLogged(true);
    }
  },[cookie]
  );

  useEffect(()=>{
      const getPatients = async()=>{
        if(token!=="" && token!=="undefined"){
            try{
                // setToken(cookie["token"]);
                // setLogged(true);
                // console.log(cookie);
                setWaiting(true);
                const patients = await API.getPatients(token);
                setPatients([...patients]);
                setWaiting(false);
              //   getSelectedPatient(patients[0].id);
                return patients;
            }catch(err){
                throw err;
            }
        }
      };
          getPatients();
      }, [token]
  );

  const getFilteredPatients = () =>{
    let filteredPatients = [...patients];
    if(filter!=="")
      filteredPatients = filteredPatients.filter(p=>String(p.patient_id).includes(String(filter)) || String(p.stage).toLowerCase().includes(String(filter).toLowerCase()));
    if(statusFilter!=="")
      filteredPatients = filteredPatients.filter(p=>String(p.survival).toLowerCase()===String(statusFilter).toLowerCase()); 
    return filteredPatients;
  }


  return (
    <Router>
        <MyNavBar logged={logged} loginCallback={loginCallback} logoutCallback={logoutCallback}/>
        <Row className="vheight-100  m-0">
            <Routes>
                <Route path="/patientview"    element={<PatientView token={token}/>}    />
                {/* <Route path="/clinical"       element={<Clinical/>}       />
                <Route path="/explainer"      element={<Explainer/>}      /> */}
                <Route path="/"               element={<MyMain 
                                                          waiting={waiting} 
                                                          patients={getFilteredPatients()} 
                                                          setFilterCallback={setFilter} 
                                                          filter={filter}
                                                          statusFilter={statusFilter}
                                                          setStatusFilterCallback={setStatusFilter}
                                                      />}    
                />
            </Routes>
        </Row>
        <Footer/>
    </Router>
  );
}

export default App;
