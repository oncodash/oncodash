import * as d3 from "d3";
import { LitElement, css } from "lit";
import {customElement, property} from 'lit/decorators.js';

@customElement("oncodash-clinical-card")
class ClinicalCard extends LitElement {

    @property()
    private patient: any;

    constructor() {
        super();
    }

    static styles = css`
        img {
            height:1.2em;
        }
    
        #patient-card {
            margin:2em;
            padding:1em;
            border: thin solid grey;
            box-shadow: 3px 3px 8px grey;

        }
        #patient-main {
            display: flex;
            font-size:large;
            font-weight:bold;
        }
        
        .patient-main-item {
            background-color:grey;
            padding:3px 1.25rem;
            position:relative;
            margin-right:-14px;
            clip-path: polygon(0% 0%, calc(100% - 14px) 0%, 100% 50%, calc(100% - 14px) 100%, 100% 100%, 0% 100%, 14px 50%);
        }

        #patient-name {
            background-color:#AACCFF;
        }
        
        #patient-age {
            background-color:#80B3FF;
        }
        
        #patient-cud_histology {
            background-color:#0066FF;
            color:white;
        }

        #patient-cud_stage {
            background-color:#0055D4;
            color:white;
        }

        #patient-survival {
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
        }

        #patient-info {
            font-size:large;
            margin:0.5em 0.5em 0.5em 1em;
        }

        #patient-primary {
            font-size:medium;
            border: thin solid grey;
            padding:1em;
            margin:1em;
        }

        #patient-primary-grid {
            display: grid;
            grid:repeat(4,2em) / auto-flow 25ex;
        }

        .patient-primary-item {
            margin:0.5em;
        }
        
        .patient-primary-item img {
            vertical-align:text-top;
        }

        .patient-primary-item span {
            margin-left:0.2em;
            vertical-align:text-top;
        }

        #patient-secondary {
            font-size:small;
            border: thin solid grey;
            padding:1em;
            margin:1em;
        }
        #patient-secondary-grid {
            display: grid;
            grid:repeat(3,2em) / auto-flow 30ex;
        }

        .patient-secondary-item {
            text-align:right;
        }

        .patient-secondary-item img {
            margin-left:0.5ex;
            vertical-align:text-top;
        }

        .true {
            font-weight:bold;
            color:black;
        }
        .false {
            font-weight:normal;
            color:grey;
        }
    `;

    connectedCallback(): void {
        super.connectedCallback();
        this.fetchClinicalData(3); // TODO: idx arg as user input
    }

    private fetchClinicalData(id: number) {
        const apiUrl = `http://127.0.0.1:8888/api/clinical-overview/data/${id}/`;
        return fetch(apiUrl)
            .then((response) => response.json() as Promise<any>)
            .then((jsonData) => {
                this.patient = jsonData;
                console.log("Clinical data: ", this.patient);
                this.requestUpdate();
            });
    }

    private insert_icon_text(where:any, name:string, text:string) {
        const e = where.append("span")
            .attr("id",`patient-${name}`)
            .attr("class","patient-primary-item");
        if( text ) {
            e.append("img")
                .attr("id",`icon-${name}`)
                .attr("src",`assets/${name}.svg`)
                .attr("title",name);
            e.append("span").text(text);
            
        } else {
            e.append("img")
                .attr("id",`icon-${name}`)
                .attr("src",`assets/${name}_NONE.svg`)
                .attr("title",name).attr("alt",`${name}: `);
        }
    }

    private insert_bool_icon(where:any, name:string, value:boolean) {

        const re = /has_/;
        const txt = name.replace(re, "");

        const e = where.append("span")
            .attr("id",`patient-${name}`)
            .attr("class",`${value} patient-secondary-item`)
            .text(txt);

        const img = e.append("img")
            .attr("id",`icon-${name}`);

        if( value ) {
            img.attr("title",`${txt}: YES`).attr("alt",`: YES`);
            img.attr("src",`assets/${name}.svg`);
        } else {
            img.attr("title",`${txt}: NO`).attr("alt",`: NO`);
            img.attr("src",`assets/${name}_NONE.svg`);
        }
    }

    render():HTMLElement  {
    // render = (): HTMLElement => { // FIXME does not fix the false undefined this.patient error
        const div = document.createElement("div");
        const card = d3.select(div)
            .attr("id", "clinicalwidget")
            .append("div")
                .attr("id", "patient-card");

        /***** Header *****/
        const header = card.append("div").attr("id","patient-header");
        
        const main = header.append("div").attr("id","patient-main");
        const survival = main.append("span")
            .attr("id","patient-survival");
        const img = survival.append("img")
            .attr("alt",this.patient.cud_survival)
            .attr("title",this.patient.cud_survival);
        if( this.patient.cud_survival == "ALIVE" ) {
            img.attr("class","patient-alive").attr("src","assets/alive.svg");
        } else {
            img.attr("class","patient-not-alive").attr("src","assets/not-alive.svg")
            survival.text(`(${this.patient.cud_date_of_death})`);
        }

        main.append("span").attr("class","patient-main-item").attr("id","patient-name").text(this.patient.patient);
        main.append("span").attr("class","patient-main-item").attr("id","patient-age").text(`${this.patient.age}y`);
        main.append("span").attr("class","patient-main-item").attr("id","patient-cud_histology").text(this.patient.cud_histology);
        main.append("span").attr("class","patient-main-item").attr("id","patient-cud_stage").text(this.patient.cud_stage);
        
        header.append("div").attr("id","patient-info").text(this.patient.extra_patient_info);

        /***** Primary section *****/
        const primary = card.append("div").attr("id","patient-primary");
        const primgrid = primary.append("div").attr("id","patient-primary-grid");
        this.insert_icon_text(primgrid, "cud_treatment_strategy", this.patient.cud_treatment_strategy);
        this.insert_icon_text(primgrid, "cud_current_treatment_phase", this.patient.cud_current_treatment_phase);
        this.insert_icon_text(primgrid, "cud_primary_therapy_outcome", this.patient.cud_primary_therapy_outcome);
        this.insert_icon_text(primgrid, "maintenance_therapy", this.patient.maintenance_therapy);
        this.insert_icon_text(primgrid, "other_diagnosis", this.patient.other_diagnosis);
        this.insert_icon_text(primgrid, "cancer_in_family", this.patient.cancer_in_family);
        this.insert_icon_text(primgrid, "chronic_illness", this.patient.chronic_illness);
        this.insert_icon_text(primgrid, "other_medication", this.patient.other_medication);
        const bmi:number = Math.round(this.patient.weight/(this.patient.height/100)**2);
        this.insert_icon_text(primgrid, "bmi", `${bmi} kg/m̉²`);

        const stage:string = this.patient.cud_stage_info;
        const progm:string = this.patient.progression_detection_method;
        if(stage || progm) {
            primary.append("div")
                .attr("id","patient-cud_stage_info")
                .text(`${stage} (${progm}).`);
        }

        /***** Secondary section *****/
        const secondary = card.append("div").attr("id","patient-secondary");
        const secgrid = secondary.append("div").attr("id","patient-secondary-grid");
        this.insert_bool_icon(secgrid, "has_response_ct", this.patient.has_response_ct);
        this.insert_bool_icon(secgrid, "has_ctdna", this.patient.has_ctdna);
        this.insert_bool_icon(secgrid, "has_petct", this.patient.has_petct);
        this.insert_bool_icon(secgrid, "has_wgs", this.patient.has_wgs);
        this.insert_bool_icon(secgrid, "has_singlecell", this.patient.has_singlecell);
        this.insert_bool_icon(secgrid, "has_germline_control", this.patient.has_germline_control);
        this.insert_bool_icon(secgrid, "has_paired_freshsample", this.patient.has_paired_freshsample);
        this.insert_bool_icon(secgrid, "has_brca_mutation", this.patient.has_brca_mutation);
        this.insert_bool_icon(secgrid, "has_hrd", this.patient.has_hrd);
        
        /***** Footer *****/
        // const footer = card.append("div").attr("id","patient-footer");

        return div;
    }
}

export default ClinicalCard;
customElements.define("oncodash-clinical-card", ClinicalCard);
