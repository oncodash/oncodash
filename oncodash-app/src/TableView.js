import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import { useNavigate } from 'react-router-dom';

// import alive from './assets/alive.svg';
// import dead from './assets/not-alive.svg';

function TableView(props) {
    const navigate = useNavigate();
    const handleRowClick = (id) => {
        navigate("/patientview", {state:{patient_id: id}});
    }  

    return(
        <Container>
                <Table striped bordered hover>
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
                                <tr key={p.id} onClick={()=> handleRowClick(p.id)} role="button">     
                                    <td>{p.id}</td>
                                    <td>{p.age}</td>
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
