import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

/** A widget that lets the user select a patient and send the correpsponding ID up.
 *
 * Should be put in the slot of a Patient Broker.
 */
@customElement("oncodash-patient-selector")
export class ODPatientSelector extends LitElement {
    /** Main managed attribute.
     *
     * This is not strictly speaking necessary for the sub-widgets management,
     * but this widget may co-exist in a PatientBroker with another Selector,
     * so we expose the property to synchronize them.
     */
    @property({ type: Number })
    patient_id = Number.NaN;

    /** The actual list of patients.
     *
     * This is a state because any update of the data should trigger a render.
     */
    @state()
    private patients: Array<any> = [];

    /** First data import when loaded. */
    override connectedCallback(): void {
        super.connectedCallback();
        this.fetchPatients(); // FIXME
        if (this.patients.length > 0) {
            this.onSelectedPatient(this.patients[0].patient);
        } else {
            console.error("[ODPatientSelector] no patient");
        }
    }

    /** Download the data for all the patients. */
    private async fetchPatients(): Promise<any> {
        const apiUrl = `http://localhost:8888/api/clinical/data/`;
        let response: any;
        try {
            // Wait for the asynchronous `fetch` function to terminate.
            // Either it ends on a result or raise an exeption.
            response = await fetch(apiUrl);
        } catch (error) {
            console.warn("[ODPatientSelector]", error);
        }
        if (!response.ok) {
            throw new Error(response.statusText);
        } else {
            // Convert the payload to JSON.
            const items = await response.json();
            this.patients = items;
            if (this.patients.length == 0) {
                console.error("[ODPatientSelector] no patient fetched");
            }
        }
    }

    /** Render the widget. */
    override render() {
        return html`
            <h2 class="widget-title">Available Patients</h2>
            <div id="patients-query">
                <select @change=${this.onChange} tabindex="0">
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
        // FIXME the "selected" attribute does not appear.
    }

    /** Called when the user selects something. */
    private onChange(e: Event) {
        const id = Number((e.target as HTMLInputElement).value);
        this.onSelectedPatient(id);
    }

    /** This dispatch a `patient_selected` event up to the mediator. */
    private onSelectedPatient(id: number) {
        if (!Number.isNaN(id)) {
            this.patient_id = id;
            const options = {
                detail: { id },
                bubbles: true, // can bubble up through the DOM
                composed: true, // can bubble across the boundary between the shadow DOM and the regular DOM
            };
            this.dispatchEvent(new CustomEvent("patient_selected", options));
        } else {
            // Error management.
            console.error(
                "[ODPatientSelector] User selected patient, but patient_id is",
                this.patient_id
            );
        }
    }

    static styles = css`
        .widget-title {
            display: none;
        }
    `;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-patient-selector": ODPatientSelector;
    }
}
