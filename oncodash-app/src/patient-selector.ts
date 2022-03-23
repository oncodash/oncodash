import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("oncodash-patient-selector")
export class ODPatientSelector extends LitElement {
    @property({ type: Number })
    patient_id = Number.NaN;

    @state()
    private patients: Array<any> = [];

    override connectedCallback(): void {
        super.connectedCallback();
        this.fetchPatients();
    }

    private fetchPatients() {
        const apiUrl = `http://127.0.0.1:8888/api/clinical-overview/data/`;
        return fetch(apiUrl)
            .then((response) => response.json() as Promise<any>)
            .then((jsonData) => {
                this.patients = jsonData;
                console.log(this.patients.length, "patients");
                // this.patient_id = this.patients[0].id;
                // this.requestUpdate();
            });
    }

    override render() {
        return html`
            <div id="patients-query">
                <select @change=${this.onChange}>
                    ${this.patients.map(
                        (item) => html`
                            <option
                                value="${item.id}"
                                ${this.patient_id == item.id ? "selected" : ""}
                            >
                                ${item.patient}
                            </option>
                        `
                    )}
                </select>
            </div>
        `;
    }

    private onChange(e: Event) {
        const id = Number((e.target as HTMLInputElement).value);
        if (!Number.isNaN(id)) {
            this.patient_id = id;
            console.log("User selected patient: ", this.patient_id);
            const options = {
                detail: { id },
                bubbles: true,
                composed: true,
            };
            this.dispatchEvent(new CustomEvent("patient_selected", options));
        }
    }

    static styles = css``;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-patient-selector": ODPatientSelector;
    }
}
