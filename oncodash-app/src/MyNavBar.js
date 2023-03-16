import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import { Row, Col} from 'react-bootstrap';
import logo from './assets/oncodash-logo.svg';
import {Link} from 'react-router-dom';
import { useState } from 'react';
import LoginModal from './LoginModal';

function MyNavBar(props) {
    const [modalShow, setModalShow] = useState(false);

    return(
            
            <Navbar className="bg-secondary py-3 fixed-top" expand="lg">
                <Container fluid>
                    <Row className="w-100">
                        <Col className="col-2 d-flex justify-content-center align-items-start">
                            <img style={{height: '60px'}} src={logo} alt="logo"/>
                        </Col>
                        <Col className="col-9 d-flex justify-content-start align-items-center">
                            <Link className='' to="/">
                                <Button className="bg-transparent text-light border-0 fw-bold fs-4">
                                    Patients List
                                </Button>
                            </Link>
                        </Col>
                        <Col className="col-1 d-flex justify-content-center align-items-center">
                            {props.logged ?  <Button variant="dark" onClick={()=>props.logoutCallback()} >Logout</Button>  :  <Button variant="primary" onClick={() => setModalShow(true)} type="button">LOGIN</Button> }
                        </Col>
                    </Row>
                </Container>
                <LoginModal
                    show={modalShow}
                    onHide={() => setModalShow(false)}
                    loginCallback={props.loginCallback}
                />
            </Navbar>

      );
  }
  export default MyNavBar;