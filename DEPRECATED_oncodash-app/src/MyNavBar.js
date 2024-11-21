import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import { Row, Col} from 'react-bootstrap';
import logo from './assets/logos/OncodashLogo_White.png';
import { useState } from 'react';
import LoginModal from './LoginModal';
import { Link, useLocation } from 'react-router-dom';

function MyNavBar(props) {
    const location = useLocation();
    const [modalShow, setModalShow] = useState(false);

    return(
            
            <Navbar style={{fontFamily:'Livvic'}} className="py-3 fixed-top navBack" expand="lg">
                <Container fluid>
                        <Col  className="col-3 d-flex justify-content-center align-items-start">
                            <img style={{height: '60px', borderRight:'1px solid grey', paddingRight:'10px'}} src={logo} alt="logo"/>
                        </Col>
                        <Col className="col-6 d-flex justify-content-start align-items-center">
                            <Link className='navLink px-3' to="/" >
                                <Button className={"bg-transparent text-light fw-bold fs-4 ".concat(location.pathname === '/home' ? 'navActive' : 'navDisactive')}>
                                    Homepage
                                </Button>
                            </Link>
                            <Link className='navLink px-3' to="/" >
                                <Button className={"bg-transparent text-light fw-bold fs-4 ".concat(location.pathname === '/' ? 'navActive' : 'navDisactive')}>
                                    Patients List
                                </Button>
                            </Link>
                            <Link className='navLink px-3' to="/" >
                                <Button className={"bg-transparent text-light fw-bold fs-4 ".concat(location.pathname === '/contact' ? 'navActive' : 'navDisactive')}>
                                    Contact
                                </Button>
                            </Link>
                            <Link className='navLink px-3' to="/" >
                                <Button className={"bg-transparent text-light fw-bold fs-4 ".concat(location.pathname === '/about' ? 'navActive' : 'navDisactive')}>
                                    About
                                </Button>
                            </Link>
                        </Col>
                        <Col className="col-2 d-flex justify-content-center align-items-center">
                            {props.logged ?  <Button style={{color:'white', borderRadius:'30px', border:'3px solid white', backgroundColor:'transparent', fontFamily:'Open-Sans'}} onClick={()=>props.logoutCallback()} >LOGOUT</Button>  :  <Button style={{color:'white', borderRadius:'30px', border:'3px solid white', backgroundColor:'transparent', fontFamily:'Open-Sans'}} onClick={() => setModalShow(true)} type="button">LOGIN</Button> }
                        </Col>
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