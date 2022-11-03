import {Row, Col} from 'react-bootstrap';
import Container from 'react-bootstrap/Container';

function Extra(props) {

    return(
        <Container className="py-4">
            <Row>
                <Col className="d-flex align-items-center justify-content-center">
                    Extra
                </Col>
            </Row>
        </Container>
    );
}
export default Extra;
