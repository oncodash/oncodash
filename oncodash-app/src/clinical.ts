import * as d3 from "d3";
import { LitElement, css } from "lit";

class ClinicalView extends LitElement {

    constructor() {
        super();
    }

    static styles = css``;

    connectedCallback(): void {
        super.connectedCallback();
    }

    render(): HTMLElement {
        const div = document.createElement("div");
        const container = d3.select(div)
            .attr("id","clinicalwidget")
            .append("p").text("Clinical view");
        return div;
    }
}

export default ClinicalView;
customElements.define("clinical-view", ClinicalView);

