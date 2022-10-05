import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import { Row, Col} from 'react-bootstrap';
import { Calendar, Tag, Table, Sliders2Vertical, Microsoft} from 'react-bootstrap-icons';

function Navigator(props) {
    return(
            <>
            <Navbar  expand="lg">
                <Container>
                    <Row className="w-100">
                        <Col className="p-4 col-8 d-flex align-items-center">
                            <Form className="w-100">
                                <Form.Control
                                    type="search"
                                    placeholder="Search by project id, member, etc"
                                    className="p-2 border border-secondary rounded"
                                    aria-label="Search"
                                />
                                {/* <Button variant="outline-success">Search</Button> */}
                            </Form>
                        </Col>
                        <Col className="col-4 d-flex justify-content-center align-items-center">
                            <Navbar.Collapse id="navbarScroll">
                                <Nav navbarScroll className="d-flex justify-content-end w-100" >
                                    <NavDropdown id="daterange" className="mx-1 border border-secondary rounded" title={<div style={{float: 'left'}}><div className="d-flex align-items-center float"><Calendar className="mr-1 fa-lg"/><div className="px-1  fs-6">Date range</div></div></div>}>
                                        <NavDropdown.Item href="#action3">Action</NavDropdown.Item>
                                        <NavDropdown.Item href="#action4">Action</NavDropdown.Item>
                                        <NavDropdown.Divider />
                                        <NavDropdown.Item href="#action5">
                                            Something else here
                                        </NavDropdown.Item>
                                    </NavDropdown>
                                    <NavDropdown id="status" className="mx-1 border border-secondary rounded" title={<div style={{float: 'left'}}><div className="d-flex align-items-center float"><Tag className="mr-1 fa-lg"/><div className="px-1  fs-6">Status</div></div></div>}>
                                        <NavDropdown.Item href="#action3">Action</NavDropdown.Item>
                                        <NavDropdown.Item href="#action4">Action</NavDropdown.Item>
                                        <NavDropdown.Divider />
                                        <NavDropdown.Item href="#action5">
                                            Something else here
                                        </NavDropdown.Item>
                                    </NavDropdown>
                                    <NavDropdown id="morefilters" className="mx-1 border border-secondary rounded" title={<div style={{float: 'left'}}><div className="d-flex align-items-center float"><Sliders2Vertical className="mr-1 fa-lg"/><div className="px-1  fs-6">More filters</div></div></div>}>
                                        <NavDropdown.Item href="#action3">Action</NavDropdown.Item>
                                        <NavDropdown.Item href="#action4">Action</NavDropdown.Item>
                                        <NavDropdown.Divider />
                                        <NavDropdown.Item href="#action5">
                                            Something else here
                                        </NavDropdown.Item>
                                    </NavDropdown>
                                </Nav>
                            </Navbar.Collapse>
                        </Col> 
                 
                    </Row>

                </Container>
            </Navbar>
            <Navbar  expand="lg">
                <Container>
                    <Row className="w-100">
                        <Col className="col-4 d-flex align-items-center p-4">
                            Selected {(props.page-1)*props.patientsPerPage+1}-{Math.min(((props.page)*props.patientsPerPage), Math.ceil(props.patients.length))} of {props.patients.length} patients
                        </Col>
                        <Col className="col-6 d-flex align-items-center justify-content-end">
                            <div className='p-2'>Patients per page: </div>
                            <NavDropdown    id="view" 
                                            className="mx-1 border border-secondary rounded px-2" 
                                            title={
                                                <div style={{float: 'left'}}>
                                                    <div className="d-flex align-items-center float">
                                                        <div className="px-1  fs-6">
                                                            {props.patientsPerPage}
                                                        </div>
                                                    </div>
                                                </div>}
                            >
                                        <NavDropdown.Item  onClick={()=>props.setPatientsPerPage_callback(8)}>8</NavDropdown.Item>
                                        <NavDropdown.Item  onClick={()=>props.setPatientsPerPage_callback(16)}>16</NavDropdown.Item>
                                        <NavDropdown.Item  onClick={()=>props.setPatientsPerPage_callback(32)}>32</NavDropdown.Item>
                            </NavDropdown>
                        </Col>
                        <Col className="col-2 d-flex align-items-center justify-content-end">
                            <div className='p-2'>View: </div>

                            <Button className={props.viewMode === "TABLE"? 
                                                    "mx-1 p-2 d-flex align-items-center float rounded-circle "
                                                    :
                                                    "mx-1 p-2 d-flex align-items-center float rounded-circle bg-secondary border-secondary"
                                            } onClick={()=>props.setViewMode_callback("TABLE")}>
                                <Table/>
                            </Button>
                            <Button className={props.viewMode === "GRID"? 
                                                    "mx-1 p-2 d-flex align-items-center float rounded-circle"
                                                    :
                                                    "mx-1 p-2 d-flex align-items-center float rounded-circle bg-secondary border-secondary"
                                            } onClick={()=>props.setViewMode_callback("GRID")}>
                                <Microsoft/>
                            </Button>
                        </Col>
                    </Row>
                </Container>
            </Navbar>
            
            </>
            

      );
  }
  export default Navigator;