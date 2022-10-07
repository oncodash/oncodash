
import Navigator from './Navigator';
import GridView from './GridView';
import TableView from './TableView';
import {useState } from 'react';
import Pagination from 'react-bootstrap/Pagination';
import {Container, Row, Col} from 'react-bootstrap';

function MyMain(props) {

    const [viewMode, setViewMode] = useState("GRID");
    const [patientsPerPage, setPatientsPerPage] = useState(8);
    const [page, setPage] = useState(1);

    function setPatientsPerPageWrapper(value){
        setPage(1);
        setPatientsPerPage(value);
    }

    function increasePage(page, n_pat, patientsPerPage){
        if(page<Math.ceil(n_pat/patientsPerPage)){
            setPage((page)=>(page+1))
        }
    }
    function decreasePage(page, n_pat, patientsPerPage){
        if(page>1){
            setPage((page)=>(page-1))
        }
    }
    function firstPage(){
        setPage(1);
    }
    function lastPage(n_pat, patientsPerPage){
        setPage(Math.ceil(n_pat/patientsPerPage))
    }

    function viewPatients(){
        let n_pat = props.patients.length;
        // let pages = Math.ceil(n_pat/patientsPerPage);
        let start_index = (page-1)*patientsPerPage;
        let end_index = start_index + patientsPerPage;
        if(end_index>=n_pat){
            end_index = n_pat ;
        }
        return props.patients.slice(start_index, end_index);
    }

    return(
        props.waiting? "" :
        <main className="w-100 p-0 my-5 ">

            <Navigator 
                patients={props.patients} 
                viewMode={viewMode} 
                setViewMode_callback={setViewMode}
                patientsPerPage={patientsPerPage}
                setPatientsPerPage_callback={setPatientsPerPageWrapper}
                page={page}
                setFilterCallback={props.setFilterCallback} 
                filter={props.filter}
                statusFilter={props.statusFilter}
                setStatusFilterCallback={props.setStatusFilterCallback}
            ></Navigator>
            {viewMode === "GRID"? 
                <GridView patients={viewPatients()}></GridView>
                :
                <TableView patients={viewPatients()}></TableView>
            }
            <Container>
                <Row>
                    <Col>
                        <Pagination className="mx-3 d-flex justify-content-end align-items-center">
                            <Pagination.First onClick={()=>firstPage()}/>
                            <Pagination.Prev  onClick={()=>decreasePage(page, props.patients.length, patientsPerPage)}/>
                            <div className="px-2">
                                Page {page} of {Math.ceil(props.patients.length/patientsPerPage)}
                            </div>   
                            <Pagination.Next onClick={()=>increasePage(page, props.patients.length, patientsPerPage)}/>
                            <Pagination.Last onClick={()=>lastPage(props.patients.length, patientsPerPage)}/>
                        </Pagination>
                    </Col>
                </Row>  
            </Container>
        </main>
    );
}
export default MyMain;
