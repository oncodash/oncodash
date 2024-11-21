import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import { useNavigate } from 'react-router-dom';

// import alive from './assets/alive.svg';
// import dead from './assets/not-alive.svg';

function TableView(props) {
    const navigate = useNavigate();
    const handleRowClick = (patient_id) => {
        navigate("/patientview", {state:{patient_id: patient_id}});
    }  

    return(
        <Container className="p-0">
                <Table className="tableView" striped bordered hover>
                    <thead>
                        <tr>
                        <th>ID</th>
                        <th>Age</th>
                        <th>Survival</th>
                        <th>Stage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {props.patients.map(p=>
                            // <Link to={"/patientview"} state={{patient_id:}}>
                                <tr key={p.patient_id} onClick={()=> handleRowClick(p.patient_id)} role="button">     
                                    <td>{p.patient_id}</td>
                                    <td>{p.age_at_diagnosis}</td>
                                    <td>{p.survival}</td>
                                    <td>{p.stage}</td>                            
                                </tr>
                            // </Link>    
                        )}
                    </tbody>
                </Table>
        </Container>
    );
}
export default TableView;
