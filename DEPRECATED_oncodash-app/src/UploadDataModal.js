import {Button, Modal, Alert, Form, FormControl} from 'react-bootstrap';
import {useState, useEffect} from 'react';
// import bsCustomFileInput from "bs-custom-file-input";

function UploadDataModal(props) {
    const [separator, setSeparator] = useState("");
    const [errorSeparator, setErrorSeparator] = useState(undefined);
    const [type, setType] = useState("");
    const [errorType, setErrorType] = useState(undefined);
    const [isUploaded, setIsUploaded] = useState(false);
    const [file, setFile] = useState();
    const [errorFile, setErrorFile] = useState(undefined);
    const [validated, setValidated] = useState(false);
    const [uploadError, setUploadError] = useState(undefined);

    // useEffect(() => {
    //     bsCustomFileInput.init();
    //   }, []);
    
    const handleClose = (event) => {
        setSeparator(undefined);
        setFile(undefined);
        setIsUploaded(false);
        props.onHide();
    }
    
    const handleSubmit = (event) => {
        event.preventDefault();
        event.stopPropagation();
        if(separator===""){
            setErrorSeparator("Select a separator!!!");
        }else{
            setErrorSeparator(undefined);
        }
        if(type===""){
            setErrorType("Select a type!!!");
        }else{
            setErrorType(undefined);
        }        
        if(file===undefined){
            setErrorFile("Upload file!!!");
        }else{
            setErrorFile(undefined);
        }
        if(separator !== "" & type!== "" & file !== undefined)
        {
            setUploadError(false);
            setValidated(true);
            props.uploadDataCallback(separator, type, file)
                .then(()=>handleClose())
                .catch((msg)=>{
                    setValidated(false);
                    setUploadError(true);
                });
        }

    }

    return(
        <Modal 
            show={props.show}
            onHide={()=>handleClose()}
            size="lg"
            aria-labelledby="contained-modal-title-vcenter"
            centered>
                    <Form noValidate validated={validated} onSubmit={handleSubmit}>
                    <Modal.Header closeButton>
                        <Modal.Title id="contained-modal-title-vcenter">
                            Upload Data
                        </Modal.Title>
                    </Modal.Header>
                        <Modal.Body>
                            <Form.Group controlId="exampleForm.ControlInput1">
                            <Form.Label>Separator</Form.Label>
                            <Form.Select aria-label="Default select example" value={separator} onChange={(event)=>setSeparator(event.target.value)}>      
                                <option value="">None</option>                          
                                <option value=",">,</option>
                                <option value=";">;</option>
                                <option value="&">&</option>
                                <option value=":">:</option>
                            </Form.Select>
                                {/* <Form.Control required value={separator} onChange={(event)=>setSeparator(event.target.value)} /> */}
                                {errorSeparator ? <Alert variant='danger'>{errorSeparator}</Alert> : ''}
                            </Form.Group>
                            <Form.Group controlId="exampleForm.ControlInput2">
                                <Form.Label>Type</Form.Label>
                                <Form.Select aria-label="Default select example" value={type} onChange={(event)=>setType(event.target.value)}>      
                                    <option value="">None</option>                          
                                    <option value="clinical">clinical</option>
                                    <option value="timeline">timeline</option>
                                </Form.Select>
                                {errorType ? <Alert variant='danger'>{errorType}</Alert> : ''}
                            </Form.Group>
                            <Form.Group controlId="exampleForm.ControlInput3">
                                <Form.Label>File</Form.Label>
                                <Form.Control type="file" onChange={(e) => {
                                                                                            console.log(e.target.files[0]); 
                                                                                            setFile(e.target.files[0]);
                                                                                            setIsUploaded(true);
                                                                                                    }
                                                                                            }/>
                                {errorFile ? <Alert variant='danger'>{errorFile}</Alert> : ''}
                            </Form.Group>
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="primary" type="submit" >Submit</Button>
                            <Button variant="secondary" onClick={() => handleClose()}>Close</Button>
                        </Modal.Footer>
                        {uploadError ? <Alert variant='danger'>Check your Separator/Type/File!!!</Alert> : ''}
                    </Form>
        </Modal>
    );
}
export default UploadDataModal;
