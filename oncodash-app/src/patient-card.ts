import * as d3 from "d3";
import { LitElement, css /*, html*/ } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("oncodash-patient-card")
class ODPatientCard extends LitElement {
    @property({ type: Number })
    patient_id = Number.NaN;

    @state()
    private patient: any;

    // private async getPatient(): Promise<any> {
    private getPatient(): any {
        // return this.fetchClinicalData(this.patient_id);
        this.fetchClinicalData(this.patient_id);
        return this.patient;
        // this.patient = this.fetchClinicalData(this.patient_id);
        // return this.patient;
        // const patient:any = await this.fetchClinicalData(this.patient_id);
        // .then(data => {
        //     console.log("Promised data?",data);
        //     return data;
        // })
        // .catch(error => console.warn(error));
        // const patient = this.fetchClinicalData(this.patient_id);
        // return patient;
    }

    private async fetchClinicalData(id: number): Promise<any> {
        const apiUrl = `http://127.0.0.1:8888/api/clinical-overview/data/${id}/`;
        // const response = await fetch(apiUrl);
        // return response.json();
        return await fetch(apiUrl)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(response.statusText);
                } else {
                    return response.json() as Promise<any>;
                }
            })
            .then((jsonData) => {
                this.patient = jsonData;
                // console.log("Fetched patient data for patient_id ",id, this.patient);
                console.log("Fetched patient data for patient_id ", id);
                // return jsonData;
            })
            .catch((error) => console.warn(error));
    }

    override render() {
        // render = (): HTMLElement => { // FIXME does not fix the false undefined patient error
        console.log("Render card for patient_id ", this.patient_id);

        const div = document.createElement("div");

        if (Number.isNaN(this.patient_id)) {
            console.log("Cannot render, no patient_id");
            return div;
        }

        // console.log("getPatient:",this.getPatient());
        const patient = this.getPatient();
        // let getpatient = async() => {return await this.fetchClinicalData(this.patient_id)};
        // const patient = getpatient();
        // const patient = this.fetchClinicalData(this.patient_id)
        //     .then(data => {
        //         console.log("Promised data?",data);
        //         return data;
        //     })
        //     .catch(error => {
        //         console.warn(error);
        //     });

        if (patient === undefined) {
            console.log("No patient data");
            return div;
        }
        console.log("Render patient data: ", patient);

        const card = d3
            .select(div)
            .attr("id", "clinicalwidget")
            .append("div")
            .attr("id", "patient-card");

        /***** Header *****/
        const header = card.append("div").attr("id", "patient-header");

        const main = header.append("div").attr("id", "patient-main");
        const survival = main.append("span").attr("id", "patient-survival");
        const img = survival
            .append("img")
            .attr("alt", patient.cud_survival)
            .attr("title", patient.cud_survival);
        if (patient.cud_survival == "ALIVE") {
            img.attr("class", "patient-alive").attr("src", "assets/alive.svg");
        } else {
            img.attr("class", "patient-not-alive").attr(
                "src",
                "assets/not-alive.svg"
            );
            survival.text(`(${patient.cud_date_of_death})`);
        }

        main.append("span")
            .attr("class", "patient-main-item")
            .attr("id", "patient-name")
            .text(patient.patient);
        main.append("span")
            .attr("class", "patient-main-item")
            .attr("id", "patient-age")
            .text(`${patient.age}y`);
        main.append("span")
            .attr("class", "patient-main-item")
            .attr("id", "patient-cud_histology")
            .text(patient.cud_histology);
        main.append("span")
            .attr("class", "patient-main-item")
            .attr("id", "patient-cud_stage")
            .text(patient.cud_stage);

        header
            .append("div")
            .attr("id", "patient-info")
            .text(patient.extra_patient_info);

        /***** Primary section *****/
        const primary = card.append("div").attr("id", "patient-primary");
        const primgrid = primary
            .append("div")
            .attr("id", "patient-primary-grid");
        this.insert_icon_text(
            primgrid,
            "cud_treatment_strategy",
            patient.cud_treatment_strategy
        );
        this.insert_icon_text(
            primgrid,
            "cud_current_treatment_phase",
            patient.cud_current_treatment_phase
        );
        this.insert_icon_text(
            primgrid,
            "cud_primary_therapy_outcome",
            patient.cud_primary_therapy_outcome
        );
        this.insert_icon_text(
            primgrid,
            "maintenance_therapy",
            patient.maintenance_therapy
        );
        this.insert_icon_text(
            primgrid,
            "other_diagnosis",
            patient.other_diagnosis
        );
        this.insert_icon_text(
            primgrid,
            "cancer_in_family",
            patient.cancer_in_family
        );
        this.insert_icon_text(
            primgrid,
            "chronic_illness",
            patient.chronic_illness
        );
        this.insert_icon_text(
            primgrid,
            "other_medication",
            patient.other_medication
        );
        const bmi: number = Math.round(
            patient.weight / (patient.height / 100) ** 2
        );
        this.insert_icon_text(primgrid, "bmi", `${bmi} kg/m̉²`);

        const stage: string = patient.cud_stage_info;
        const progm: string = patient.progression_detection_method;
        if (stage || progm) {
            primary
                .append("div")
                .attr("id", "patient-cud_stage_info")
                .text(`${stage} (${progm}).`);
        }

        /***** Secondary section *****/
        const secondary = card.append("div").attr("id", "patient-secondary");
        const secgrid = secondary
            .append("div")
            .attr("id", "patient-secondary-grid");
        this.insert_bool_icon(
            secgrid,
            "has_response_ct",
            patient.has_response_ct
        );
        this.insert_bool_icon(secgrid, "has_ctdna", patient.has_ctdna);
        this.insert_bool_icon(secgrid, "has_petct", patient.has_petct);
        this.insert_bool_icon(secgrid, "has_wgs", patient.has_wgs);
        this.insert_bool_icon(
            secgrid,
            "has_singlecell",
            patient.has_singlecell
        );
        this.insert_bool_icon(
            secgrid,
            "has_germline_control",
            patient.has_germline_control
        );
        this.insert_bool_icon(
            secgrid,
            "has_paired_freshsample",
            patient.has_paired_freshsample
        );
        this.insert_bool_icon(
            secgrid,
            "has_brca_mutation",
            patient.has_brca_mutation
        );
        this.insert_bool_icon(secgrid, "has_hrd", patient.has_hrd);

        /***** Footer *****/
        // const footer = card.append("div").attr("id","patient-footer");

        return div;
    }

    private insert_icon_text(where: any, name: string, text: string): void {
        const e = where
            .append("span")
            .attr("id", `patient-${name}`)
            .attr("class", "patient-primary-item");
        if (text) {
            e.append("img")
                .attr("id", `icon-${name}`)
                .attr("src", `assets/${name}.svg`)
                .attr("title", name);
            e.append("span").text(text);
        } else {
            e.append("img")
                .attr("id", `icon-${name}`)
                .attr("src", `assets/${name}_NONE.svg`)
                .attr("title", name)
                .attr("alt", `${name}: `);
        }
    }

    private insert_bool_icon(where: any, name: string, value: boolean): void {
        const re = /has_/;
        const txt = name.replace(re, "");

        const e = where
            .append("span")
            .attr("id", `patient-${name}`)
            .attr("class", `${value} patient-secondary-item`)
            .text(txt);

        const img = e.append("img").attr("id", `icon-${name}`);

        if (value) {
            img.attr("title", `${txt}: YES`).attr("alt", `: YES`);
            img.attr("src", `assets/${name}.svg`);
        } else {
            img.attr("title", `${txt}: NO`).attr("alt", `: NO`);
            img.attr("src", `assets/${name}_NONE.svg`);
        }
    }

    static styles = css`
        img {
            height: 1.2em;
        }

        #patient-card {
            margin: 2em;
            padding: 1em;
            border: thin solid grey;
            box-shadow: 3px 3px 8px grey;
        }
        #patient-main {
            display: flex;
            font-size: large;
            font-weight: bold;
        }

        .patient-main-item {
            background-color: grey;
            padding: 3px 1.25rem;
            position: relative;
            margin-right: -14px;
            clip-path: polygon(
                0% 0%,
                calc(100% - 14px) 0%,
                100% 50%,
                calc(100% - 14px) 100%,
                100% 100%,
                0% 100%,
                14px 50%
            );
        }

        #patient-name {
            background-color: #aaccff;
        }

        #patient-age {
            background-color: #80b3ff;
        }

        #patient-cud_histology {
            background-color: #0066ff;
            color: white;
        }

        #patient-cud_stage {
            background-color: #0055d4;
            color: white;
        }

        #patient-survival {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        #patient-info {
            font-size: large;
            margin: 0.5em 0.5em 0.5em 1em;
        }

        #patient-primary {
            font-size: medium;
            border: thin solid grey;
            padding: 1em;
            margin: 1em;
        }

        #patient-primary-grid {
            display: grid;
            grid: repeat(4, 2em) / auto-flow 25ex;
        }

        .patient-primary-item {
            margin: 0.5em;
        }

        .patient-primary-item img {
            vertical-align: text-top;
        }

        .patient-primary-item span {
            margin-left: 0.2em;
            vertical-align: text-top;
        }

        #patient-secondary {
            font-size: small;
            border: thin solid grey;
            padding: 1em;
            margin: 1em;
        }
        #patient-secondary-grid {
            display: grid;
            grid: repeat(3, 2em) / auto-flow 30ex;
        }

        .patient-secondary-item {
            text-align: right;
        }

        .patient-secondary-item img {
            margin-left: 0.5ex;
            vertical-align: text-top;
        }

        .true {
            font-weight: bold;
            color: black;
        }
        .false {
            font-weight: normal;
            color: grey;
        }
    `;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-patient-card": ODPatientCard;
    }
}
