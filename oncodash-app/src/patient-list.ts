import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { styleMap } from "lit/directives/style-map.js";

import { ODPatientCard } from "./patient-card";

/** A widget that lets the user select a patient and send the correpsponding ID up.
 *
 * Should be put in the slot of a Patient Broker.
 */
@customElement("oncodash-patient-list")
export class ODPatientList extends LitElement {
    /** Main managed attribute.
     *
     * This is not strictly speaking necessary for the sub-widgets management,
     * but this widget may co-exist in a PatientBroker with another Selector,
     * so we expose the property to synchronize them.
     */
    @property({ type: Number })
    patient_id = Number.NaN;

    @property({ type: Boolean })
    hideHeader = false;

    @property({ type: Boolean })
    hideMain = false;

    @property({ type: Boolean })
    hidePrimary = false;

    @property({ type: Boolean })
    hideSecondary = false;

    @property({ type: Boolean })
    hideFooter = false;

    @property({ type: Boolean })
    eventOnClick = true;

    @property({ type: styleMap })
    cardStyles = {};

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
        const apiUrl = `http://localhost:8888/api/clinical-overview/data/`;
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
            <div id="patient-query">
                <ul id="patient-list">
                    ${this.patients.map(
                        (item) => html`
                            <li>
                                <div class="patient-card">
                                    ${new ODPatientCard(
                                        item.id,
                                        { cursor: "pointer" },
                                        this.hideHeader,
                                        this.hideMain,
                                        this.hidePrimary,
                                        this.hideSecondary,
                                        this.hideFooter,
                                        this.eventOnClick
                                    )}
                                </div>
                            </li>
                        `
                    )}
                </ul>
            </div>
        `;
        // FIXME use anchor links?.
    }

    /** Called when the user selects something. */
    private onClick(e: Event) {
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
            display: var(--oncodash-patient-list-title-display, block);
        }

        #patient-list {
            list-style: none;
            padding: 0.5em;
        }

        #patient-list li {
            vertical-align: top;
            display: var(--oncodash-patient-list-li-display, block);
            width: var(--oncodash-patient-list-li-width, 100%);
        }
    `;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-patient-list": ODPatientList;
    }
}
