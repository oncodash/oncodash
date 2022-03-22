import * as d3 from "d3";
import { LitElement } from "lit";


function showData(): HTMLElement {

    // shadow-DOM container
    const div = document.createElement("div");
    const container = d3.select(div).attr("id", "clinwidget");

    return div
}


class ClinicalView extends LitElement {
    constructor(private clinData?: any) {
        super();
    }

    connectedCallback(): void {
        super.connectedCallback();
        this.fetchClinicalData(3); // TODO: idx arg as user input
    }

    render(): HTMLElement {
        return showData();
    }

    private fetchClinicalData(id: number) {
        const apiUrl = `http://127.0.0.1:8888/api/clinical-overview/data/${id}/`;
        return fetch(apiUrl)
            .then((response) => response.json() as Promise<any>)
            .then((jsonData) => {
                this.clinData = jsonData;
                console.log(jsonData);
                this.requestUpdate();
            });
    }
}

export default ClinicalView;
customElements.define("clinical-view", ClinicalView);

