import {Row, Col} from 'react-bootstrap';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';

function Footer(props) {

    return(
        <Navbar className="bg-secondary py-3 mt-5 fixed-bottom" expand="lg">
            <Container fluid>
                <Row className="w-100">
                    <Col className="col-2 d-flex justify-content-center align-items-start">
                        
                    </Col>
                    <Col className="col-7 d-flex justify-content-start align-items-start">

                    </Col>
                    <Col className="col-3 d-flex justify-content-center">
                            <div className="text-white m-1">
                                Designed by 
                                <a className="text-light m-1" href="https://www.deciderproject.eu/">
                                    DECIDER
                                </a>
                            </div>
                    </Col>
                </Row>
            </Container>
        </Navbar>
    );
}
export default Footer;
