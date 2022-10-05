import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import { Row, Col} from 'react-bootstrap';
import logo from './assets/oncodash-logo.svg';
import {Link} from 'react-router-dom';

function MyNavBar(props) {
    return(
            
            <Navbar className="bg-secondary py-3 bg-opacity-25" expand="lg">
                <Container fluid>
                    <Row className="w-100">
                        <Col className="col-2 d-flex justify-content-center align-items-start">
                            <img style={{height: '60px'}} src={logo} alt="logo"/>
                        </Col>
                        <Col className="col-9 d-flex justify-content-start align-items-center">
                            <Link className='' to="/">
                                <Button className="bg-transparent text-secondary border-0 fw-bold fs-4">
                                    Patients List
                                </Button>
                            </Link>
                        </Col>
                        <Col className="col-1 d-flex justify-content-center align-items-center">
                            <Button className="bg-secondary bg-opacity-75 border-secondary text-light border rounded py-2 px-4 fs-6">
                                Login
                            </Button>
                        </Col>
                    </Row>
                </Container>
            </Navbar>

      );
  }
  export default MyNavBar;