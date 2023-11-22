import {Row, Col} from 'react-bootstrap';
import Container from 'react-bootstrap/Container';
import OverviewGenomicCard from './OverviewGenomicCard'

function Genomic(props) {
    let counter = 0;
    const genomic = props.patient.genomic.genomic;
    // const genomic = {
    //     "putative_functionally_relevant_variant": [2, "PUTATIVE FUNCTIONALLY RELEVANT VARIANT"],
    //     "variants_of_uknown_functional_significance": [1, "VARIANTS OF UKNOWN FUNCTIONAL SIGNIFICANCE"],
    //     "putative_functionally_neutral_variants": [1, "PUTATIVE FUNCTIONALLY NEUTRAL VARIANTS"],
    //     "other_alterations": [1, "OTHER ALTERATIONS"],
    // };
    
    const genomic_all = props.patient.genomic
    const displayObjectsKeys = ["putative_functionally_relevant_variant","variants_of_uknown_functional_significance","putative_functionally_neutral_variants","other_alterations"];
    const nameDICT = {
        "putative_functionally_relevant_variant":"PUTATIVE FUNCTIONALLY RELEVANT VARIANT",
        "variants_of_uknown_functional_significance":"VARIANTS OF UKNOWN FUNCTIONAL SIGNIFICANCE",
        "putative_functionally_neutral_variants":"PUTATIVE FUNCTIONALLY NEUTRAL VARIANTS",
        "other_alterations":"OTHER ALTERATIONS",
    }
    // const putative_functionally_relevant_variant = {
    //     "BRCA": {
    //         "description": "Gene information... Lorem ipsum",
    //         "alterations": [
    //             {
    //                 "name": "stop gained p.Lys2008Ter exon 11/27",
    //                 "description": "Alteration information... Lorem ipsum",
    //                 "row": [
    //                     {
    //                     "samples_ids":1,
    //                     "samples_info":"Plasma sample",
    //                     "treatment_phase":"Primary",
    //                     "tumor_purity":"40%",
    //                     "mutation_affects":"DNA",
    //                     "reported_sensitivity":"Niraparib",
    //                 },
    //                 {
    //                     "samples_ids":2,
    //                     "samples_info":"Plasma sample",
    //                     "treatment_phase":"Follow-up",
    //                     "tumor_purity":"30%",
    //                     "mutation_affects":"RNA",
    //                     "reported_sensitivity":"Bevacizumab",
    //                 }                    
    //             ]
    //             },
    //             {
    //                 "name": "missense p.Cys2689Phe exon 18/27",
    //                 "description": "Alteration information... Lorem ipsum",
    //                 "row": [
    //                     {
    //                     "samples_ids":2,
    //                     "samples_info":"Plasma sample",
    //                     "treatment_phase":"Interval",
    //                     "tumor_purity":"60%",
    //                     "mutation_affects":"RNA",
    //                     "reported_sensitivity":"Olaparib",
    //                 }
    //             ]
    //             }
    //         ]
    //     },
    //     "AKT1": {
    //         "description": "Gene information... Lorem ipsum",
    //         "alterations": [
    //             {
    //                 "name": "stop gained p.Lys2008Ter exon 11/27",
    //                 "description": "Alteration information... Lorem ipsum",
    //             }
    //         ]
    //     }        
    // };

    const displayOrder = ["samples_ids", "samples_info", "treatment_phase", "tumor_purity", "mutation_affects", "reported_sensitivity"]
    const displayOrderNameMap = {
        "samples_ids":"SAMPLES IDS",
        "samples_info":"SAMPLES INFO",
        "treatment_phase":"TREATMENT PHASE",
        "tumor_purity":"TUMOR PURITY",
        "mutation_affects":"MUTATION AFFECTS",
        "reported_sensitivity":"REPORTED SENSITIVITY RESPONSE",
    }

    return(
        <Container className="py-4 px-5 bottomBorderRadius">
            <Row  className="row justify-content-between">
                {
                    Object.keys(genomic).map(k=>
                        <OverviewGenomicCard key={k} value={genomic[k][0]} name={genomic[k][1]}/>
                    )
                }
                
            </Row>

            {
                displayObjectsKeys.map(dob=>
                        <div key={counter++}>
                        <Row  className="row justify-content-between mt-5">
                            <div className="bg-success pl-5 ml-5 bg-opacity-25 fs-3">
                                <b>{nameDICT[dob]} - {genomic[dob][0]}</b>
                            </div>
                        </Row>                    
                        {Object.keys(genomic_all[dob]).map(k=>
                        <div key={counter++} className="my-4 px-5 mx-5 bg-opacity-25">
                            <div className="fs-3">
                                <b>{k}</b>
                            </div>
                            <div className="fs-5">
                                {genomic_all[dob][k]["description"]}
                            </div>
                            {
                                genomic_all[dob][k]["alterations"].map(a=>
                                    <div key={counter++}>
                                        <div key={a.name} className="my-3 fs-3 px-5 bg-opacity-10 bg-success">
                                            <b>Alteration - </b>{a.name}
                                        </div>  
                                        <div className="fs-5 px-5">
                                            {a["description"]}
                                        </div>
                                        {
                                            "row" in a ?
                                                <Row key={counter++} className="py-3 text-right">
                                                    <Row className="px-5 py-2">
                                                        {
                                                            displayOrder.map(d=>
                                                                <Col key={counter++} style={{"fontWeight":"bold"}} className="text-center" xs={2} sm={2} md={2} lg={2} xl={2} xxl={2}>
                                                                    {displayOrderNameMap[d]}
                                                                </Col>
                                                            )
                                                        }
                                                    </Row>                                         
                                                        { 
                                                            a.row.map(r=>
                                                                <Row key={counter++} className="px-5">  
                                                                    {
                                                                        displayOrder.map(d=>
                                                                            <Col key={counter++} className="text-center" xs={2} sm={2} md={2} lg={2} xl={2} xxl={2}>
                                                                                {d=="samples_ids"? r[d].replaceAll("_","-"): r[d].split(";").map(f => <div key={counter++}><div>{f}</div><div style={{"height":"10px", }}>&nbsp;</div></div>)}
                                                                            </Col>
                                                                        )
                                                                    }
                                                                </Row>
                                                            )
                                                        }
                                                    
                                                </Row>
                                                :
                                                ''
                                        } 
                                    </div>                               
                                )
                            }
                        
                        </div>
                    )}</div>
                )
            }
        </Container>
    );
}
export default Genomic;
