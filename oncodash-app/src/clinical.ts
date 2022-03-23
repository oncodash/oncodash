import * as d3 from "d3";
import { LitElement, css } from "lit";

class ClinicalView extends LitElement {
    constructor(private clinData?: any) {
        super();
    }

    static styles = css``;

    connectedCallback(): void {
        super.connectedCallback();
        this.fetchClinicalData(3); // TODO: idx arg as user input
    }

    private fetchClinicalData(id: number) {
        const apiUrl = `http://127.0.0.1:8888/api/clinical-overview/data/${id}/`;
        return fetch(apiUrl)
            .then((response) => response.json() as Promise<any>)
            .then((jsonData) => {
                this.clinData = jsonData;
                console.log("Clinical data: ", jsonData);
                this.requestUpdate();
            });
    }

    render(): HTMLElement {
        const div = document.createElement("div");
        d3.select(div)
            .attr("id", "clinicalwidget")
            .append("p")
            .text("Clinical view");
        return div;
    }
}

export default ClinicalView;
customElements.define("clinical-view", ClinicalView);
