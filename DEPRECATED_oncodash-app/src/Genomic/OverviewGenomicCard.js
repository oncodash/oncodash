import {Row, Col} from 'react-bootstrap';
import Container from 'react-bootstrap/Container';

function OverviewGenomicCard(props) {

    return(
        <Col style={{'width':'22%', 'border':'5px solid #159FC1', 'borderRadius':'25px'}} className="bg-opacity-25 py-1 px-3 m-3 ">
            <div style={{fontSize:'3em'}} className="text-center"><b>{props.value}</b></div>
            <div className="text-center fs-6">{props.name}</div>
        </Col>
    );
}
export default OverviewGenomicCard;
