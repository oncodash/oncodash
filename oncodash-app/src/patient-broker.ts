import { LitElement, html, css, PropertyValues } from "lit";
import {
    customElement,
    property,
    queryAssignedElements,
} from "lit/decorators.js";

@customElement("oncodash-patient-broker")
export class ODPatientBroker extends LitElement {
    @property({ type: Number })
    patient_id: number = Number.NaN;

    // Makes an accessor to the children in slots.
    // Here for the "viewer" slot.
    @queryAssignedElements({ slot: "viewer" })
    viewers!: Array<HTMLElement>;

    getViewer(): HTMLElement {
        return this.viewers[0];
    }

    override render() {
        console.log("[ODPatientBroker] render");
        return html`
            <div id="oncodash-patient-broker">
                <div
                    id="oncodash-patient-broker-selector"
                    @patient_selected=${this.patientSelected}
                >
                    <slot name="selector" />
                </div>
                <div id="oncodash-patient-broker-view">
                    <slot name="viewer" @slotchange=${this.onSlotChange} />
                </div>
            </div>
        `;
    }

    private patientSelected(e: CustomEvent) {
        console.log("Received selected patient from query: ", e.detail.id);
        this.patient_id = e.detail.id;
        // this.requestUpdate();
    }

    private onSlotChange() {
        this.requestUpdate();
    }

    override updated(changedProperties: PropertyValues<any>): void {
        super.updated(changedProperties);
        if (!Number.isNaN(this.patient_id)) {
            const child = this.getViewer();
            child.setAttribute("patient_id", `${this.patient_id}`);
            console.log(
                "Set child widget's selected patient to: ",
                this.patient_id
            );
        }
    }

    static styles = css`
        #oncodash-patient-broker-selector {
            width: 20ex;
            height: 100%;
            overflow: auto;
        }

        #oncodash-patient-broker-view {
            margin-left: 20ex; // Should match #*-selector's width
        }

        /* On screens that are less than 700px wide, make the sidebar into a topbar. */
        @media screen and (max-width: 700px) {
            #query {
                width: 100%;
                height: auto;
                position: relative;
            }

            #oncodash-patient-broker-view {
                margin-left: 0;
            }
        }
    `;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-patient-broker": ODPatientBroker;
    }
}
