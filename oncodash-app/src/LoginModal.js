import {Button, Modal, Alert, Form} from 'react-bootstrap';
import {useState} from 'react';

function MyLoginModal(props) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [validated, setValidated] = useState(false);
    const [errorEmail, setErrorEmail] = useState(undefined);
    const [errorPassword, setErrorPassword] = useState(undefined);
    const [loginErr, setLoginErr] = useState(undefined);
    

    const handleClose = (event) => {
        setEmail("");
        setPassword("");
        setValidated(false);
        setErrorEmail(undefined);
        setErrorPassword(undefined);
        setLoginErr(undefined);
        props.onHide();
    }
    
    const handleSubmit = (event) => {
        event.preventDefault();
        event.stopPropagation();
        if(email===""){
            setErrorEmail("Insert Email!!!");
            setLoginErr(false);
        }else{
            setErrorEmail(undefined);
        }
        if(password===""){
            setErrorPassword("Insert Password!!!");
            setLoginErr(false);
        }else{
            setErrorPassword(undefined);
        }
        if(email !== "" & password!== "")
        {
            setLoginErr(false);
            setValidated(true);
            props.loginCallback(email, password)
                .then(()=>handleClose())
                .catch((msg)=>{
                    setValidated(false);
                    setLoginErr(msg);
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
                            LOGIN
                        </Modal.Title>
                    </Modal.Header>
                        <Modal.Body>
                            <Form.Group controlId="exampleForm.ControlInput1">
                                <Form.Label>Email</Form.Label>
                                <Form.Control required type="email" value={email} onChange={(event)=>setEmail(event.target.value)} />
                                {errorEmail ? <Alert variant='danger'>{errorEmail}</Alert> : ''}
                            </Form.Group>
                            <Form.Group controlId="exampleForm.ControlInput2">
                                <Form.Label>Password</Form.Label>
                                <Form.Control required type="password" value={password} onChange={(event)=>setPassword(event.target.value)} />
                                {errorPassword ? <Alert variant='danger'>{errorPassword}</Alert> : ''}
                            </Form.Group>
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="primary" type="submit" >Submit</Button>
                            <Button variant="secondary" onClick={() => handleClose()}>Close</Button>
                        </Modal.Footer>
                        {loginErr ? <Alert variant='danger'>Incorrect username and/or password!!!</Alert> : ''}
                    </Form>
        </Modal>
    );
}
export default MyLoginModal;
