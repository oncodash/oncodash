import {Check, Question, X} from 'react-bootstrap-icons';
// import API from "../API.js";
// import { useEffect, useState } from 'react';

function StaticToggle(props) {
    // console.log(props.answer, props.label);
    const displayOrder = ["patient_id", "cohort_code", "age_at_diagnosis", "survival", "histology", "stage"];

    function handleAnswer(answer, label){
        if(answer==="Yes"){
            return <div className='staticToggle' style={{"backgroundColor":"#90EE90"}}>
                        <div style={{"color":"white", "backgroundColor":"green", "borderRadius":"20px"}}><Check size={16}/></div>
                        <div style={{padding:"0px 0px 0px 4px"}}>{label}</div>
                    </div>;
        }
        else if(answer==="No"){
            return <div className='staticToggle' style={{"backgroundColor":"#FFCCCB"}}>
                        <div style={{"color":"white", "backgroundColor":"red", "borderRadius":"20px"}}><b><X size={16}/></b></div>
                        <div style={{padding:"0px 0px 0px 4px"}}>{label}</div>
                    </div>;
        }
        else{
            return <div className='staticToggle' style={{"backgroundColor":"#d6d6d6"}}>
                        <div style={{"color":"white", "backgroundColor":"grey", "borderRadius":"20px"}}><Question size={16}/></div>
                        <div style={{padding:"0px 0px 0px 4px"}}>{label===NaN||label===null||label===undefined?"NA":label}</div>
                    </div>;
        }
    }

    return(
        props.label!==undefined?handleAnswer(props.answer, props.label):""
    );


}

export default StaticToggle; 