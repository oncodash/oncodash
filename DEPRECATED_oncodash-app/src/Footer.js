import {Row, Col} from 'react-bootstrap';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import logo from './assets/logos/normal-reproduction-high-resolution.jpg';
import { Twitter,Linkedin } from 'react-bootstrap-icons';

function Footer(props) {

    return(
        // <Navbar className="bg-white py-3 mt-5 fixed-bottom" expand="lg">
            <Container fluid className="fixed-bottom bg-white py-5">
                <Container >
                <Row className="w-100">
                    <Col className="col-2 d-flex justify-content-center align-items-start">
                        <img style={{height: '60px'}} src={logo} alt="logo"/>
                    </Col>
                    <Col className="col-5 d-flex justify-content-center align-items-start">
                        © Decider Project 2021
                    </Col>
                    <Col className="col-3  justify-content-center align-items-start">
                        <div>Folow us on:</div>
                        <div>
                            <a className="px-1" href="https://twitter.com/deciderproject">
                                <Twitter size={30}/>
                            </a>
                            <a className="px-1" href="https://www.linkedin.com/company/decider-project/">
                            <Linkedin size={30}/>
                            </a>
                        </div>
                    </Col>
                    <Col className="col-2  justify-content-left">
                        <div>
                            <a href="https://www.deciderproject.eu/accessibility-leaflet/">Accessibility leaflet</a>
                        </div>
                        <div>
                            <a href="https://www.deciderproject.eu/privacy-policy/">Privacy Policy</a>
                        </div>
                    </Col>
                </Row>
                </Container>
            </Container>
        // </Navbar>
    );
}
export default Footer;
