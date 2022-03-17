import { LitElement, html, css, PropertyValues } from "lit";
import {
    customElement,
    property,
    queryAssignedElements,
} from "lit/decorators.js";

/** A mediator that binds a `patient_id` selector with viewer(s).
 *
 * This class can catch `patient_selected` events, and
 * expects managed widgets to have a `patient_id` attribute.
 */
@customElement("oncodash-patient-broker")
export class ODPatientBroker extends LitElement {
    /** Main managed attribute.
     *
     * This is not strictly speaking necessary for the sub-widgets management,
     * but this widget may itself be composed in another widget,
     * so we expose the main attribute here as well.
     */
    @property({ type: Number })
    patient_id: number = Number.NaN;

    /** Makes an accessor to the children in slots.
     *
     * Here for the "viewer" slot.
     */
    @queryAssignedElements({ slot: "viewer" })
    viewers!: Array<HTMLElement>;

    /** Render the widget. */
    override render() {
        return html`
            <div id="oncodash-patient-broker">
                <div
                    id="oncodash-patient-broker-selector"
                    @patient_selected=${this.onPatientSelected}
                >
                    <slot name="selector">No patient loaded…</slot>
                </div>
                <div id="oncodash-patient-broker-view">
                    <slot name="viewer"
                        >Click on a patient to display its card.</slot
                    >
                </div>
            </div>
        `;
    }

    /** Called when the `patient_selected` event is caught. */
    private onPatientSelected(e: CustomEvent) {
        this.patient_id = e.detail.id;
    }

    /** Called when the `patient_id` property is changed.
     *
     * Probably because `onPatientSelected` caught an event.
     * We then propagate the `patient_id` value down to the viewer widget.
     */
    override updated(changedProperties: PropertyValues<any>): void {
        super.updated(changedProperties);
        if (!Number.isNaN(this.patient_id)) {
            for (const child of this.viewers) {
                child.setAttribute("patient_id", `${this.patient_id}`);
            }
        }
    }

    static styles = css`
        #oncodash-patient-broker {
            display: flex;
            flex-direction: row;
            height: 90vh;
        }

        #oncodash-patient-broker-selector {
            width: 25%;
            height: 100%;
            overflow: auto;
            border: thin solid #ccc;
            background-color: #eee;
        }

        #oncodash-patient-broker-view {
            width: 75%;
            height: auto;
        }

        /* On screens that are less than 700px wide, make the sidebar into a topbar. */
        @media screen and (max-width: 900px) {
            #oncodash-patient-broker {
                display: block;
            }

            #oncodash-patient-broker-selector {
                width: 100%;
                height: 20em;
                overflow: auto;
                position: relative;
            }

            #oncodash-patient-broker-view {
                width: 100%;
                height: auto;
            }
        }
    `;
}

declare global {
    interface HTMLElementTagNameMap {
        "oncodash-patient-broker": ODPatientBroker;
    }
}
