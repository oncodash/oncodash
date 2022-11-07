import {Row, Col} from 'react-bootstrap';
import Container from 'react-bootstrap/Container';
import {Link} from 'react-router-dom';

import alive from './assets/alive.svg';
import dead from './assets/not-alive.svg';

function GridView(props) {


    return(
        <Container>
            <Row>
                {props.patients.map(p=>
                    <Col key={p.patient_id} xs={12} sm={12} md={6} lg={4} xl={3} xxl={3}>
                        <Link to={"/patientview"} state={{patient_id:p.patient_id}}>
                            <div className={p.survival === "alive" ? 
                                    "bg-success bg-opacity-25 border border-secondary py-5 px-2 m-3  rounded"
                                    :
                                    "bg-danger bg-opacity-25 border border-secondary py-5 px-2 m-3  rounded"}
                                role="button">
                                {p.survival==="alive"?<img src={alive} alt="alive"/>:<img src={dead} alt="dead"/>}
                                <div>ID: {p.patient_id}</div>
                                <div>Age: {p.age_at_diagnosis}</div>
                                <div>Survial: {p.survival}</div>
                                <div>Stage: {p.stage}</div>
                            </div>
                        </Link>    
                    </Col>
                )}

            </Row>
        </Container>
    );
}
export default GridView;
