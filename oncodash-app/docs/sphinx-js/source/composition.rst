.. widgets_composition:

####################################
Widget Composition Model in Oncodash
####################################

******************
General Principles
******************

Oncodash use the `Lit library <https://lit.dev>`_ to implement its web components.
Lit encapsulate most of the complexity of creating new widgets
and allows to assemble self-contained widgets from smaller units.
Lit can be programmed with Typescript, which brings decorator and types,
for a better programming ergonomics.

Lit comes as a layer on top of web components, and abstract its templates inside
the :class:`litElement` class, from which all widgets should inherit.

:numref:`Figure {number}<Lit_Compo>` shows widgets composition and data flows.

.. _Lit_Compo:

.. figure:: _static/lit_composition.svg
    :class: diagram

    The application is built as a composition of Lit widgets.
    Any widget can make independent calls to the backend, through the API.
    Composed widgets can update the data held by sub-widgets,
    and should raise events every time they are updated
    (by new data from the backend or after an interaction with the user).


***********************
Composition in Oncodash
***********************

The preferred composition architecture in Oncodash is to use composition of classes,
using Lit's *reactive controllers* instead of *mixins*, unless necessary [#LIT]_.

For Oncodash, a user interface element is a *widget*.
Any widget may have a graphical representation in the form of HTML nodes.
Any widget may also fetch data from any entry point, be it from Oncodash's backend or a public API.

Widgets may also be composed with other widgets.
That is, a graphical element in a given widget may be itself a widget, and not just a pure vanilla HTML element.
The way those widgets communicate forms the core of the Oncodash widget architecture.

Widgets being assembled from other widgets, they form a tree.
Each widget thus have one parent widget, and may have several child widgets that composes it.
Widgets communicate only up or down the composition tree, with two different mechanisms:

* either it raises an event to its parent widget (*events up*),
* either it sets attributes of its child widgets (*properties down*).

Widgets cannot exchange data across the composition tree.
To synchronize information across several widgets, we use the Mediator design pattern.
In this pattern, a parent widget which would receive an updated information from one child widget
is responsible to update all its corresponding child widgets.


*******************
Composition Example
*******************

As an example, the following section will demonstrate the simplest articulation of three widgets:

* A Selector, on which a user can decide what item to display among a list.
* A Viewer, which actually displays a complete data item.
* A Mediator, which binds them.

The communication process follows this chain of events:

1. The user selects an item in the Selector widget,
2. the Selector put the selected ``item_id`` in an event and dispatch it up to the Mediator,
3. the Mediator updates its ``item_id`` property with the data in the event,
4. which trigger an update of the Mediator,
5. which then set the corresponding ``item_id`` attribute of its Viewer,
6. the Viewer spots that its ``item_id`` attribute is updated,
7. it fetches the corresponding data in its ``item`` state,
8. which triggers a rendering of the Viewer widget.

.. figure:: _static/mediator.svg
    :class: diagram

    Summary of the process by which a change in one managed widget (here the Selector)
    leads to an update in another managed widget (here the Viewer)
    by passing through a Mediator widget.

The following sections show the code for this example,
read the comments for explanations.


Selector Widget
===============

.. code-block:: typescript

    import {LitElement, html} from 'lit';
    import {customElement, property} from 'lit/decorators.js';

    // The Selector widget is responsible for getting an information from the user.
    // Then it will dispatch the selected info up to the Mediator,
    // that may ask over widget to do something with that new information.
    @customElement('my-selector')
    export class Selector extends LitElement {

        // The ID of the item that the user is selecting.
        // As a Lit "property", so it will trigger
        // an update sequence every time it is changed.
        @property({type: Number})
        item_id = Number.NaN;

        // The full list of selectable items.
        // In this demo, it is hard coded.
        // However, we will see in the Viewer class
        // to see how to fetch this kind of data.
        private items: Array<any> = [];

        // This function is called when the widget
        // is loaded for the first time.
        // In this demo we use it to create the
        // hard-coded data structure.
        override connectedCallback(): void {
            console.log("[Selector] Callback");
            super.connectedCallback();
            this.items = [
                {"name":"item 1","id":1},
                {"name":"item 2","id":2},
                {"name":"item 3","id":3}
            ];
            this.item_id = this.items[0].id;
        }

        // This is called when the widget is rendered.
        override render() {
            console.log("[Selector] Rendering");
            // Every time the user selects something in this HTML component,
            // it will call this.onSelection.
            // Note that each item displayed here has a *label* (here, item.name)
            // and a *value* (here item.id).
            return html`<h2>Selector:</h2>
                <select @change=${this.onSelection}>
                    ${this.items.map((item) => html`
                        <option
                            value=${item.id}
                            test=${this.item_id}
                            ${(this.item_id === item.id) ? "selected" : ""}
                        >${item.name}</option>
                    `)}
                </select>`;
            // FIXME the "selected" attribute does not appear.
        }

        // This is called every time the user selects something.
        private onSelection(e : Event) {
            // Extract the value hidden within the HTML component.
            const id: number = Number((e.target as HTMLInputElement).value);
            if(!Number.isNaN(id)) { // If the value makes sense.
                this.item_id = id;
                console.log("[Selector] User selected item: ",this.item_id);
                // We raise an event up to the Mediaton widget.
                const options = {
                    detail: {id},
                    // This option will let the event raise up in
                    // the widget composition chain, up to the Mediator.
                    bubbles: true,
                    composed: true
                };
                // We use a specific `selected` event that the Mediator knows.
                this.dispatchEvent(new CustomEvent('selected',options));
                
            } else { // Error management.
                console.log("[Selector] User selected item, but item_id is",this.item_id);
            }
        }
    }

    declare global {
      interface HTMLElementTagNameMap {
        'my-selector': Selector;
      }
    }


Mediator Widget
===============

.. code-block:: typescript
    import {LitElement, html, PropertyValues} from 'lit';
    import {customElement, property, queryAssignedElements} from 'lit/decorators.js';

    // The Mediator widget receives any new information from the Selector.
    // It is then responsible to dispatch it to the widgets that
    // it holds in its slots.
    @customElement('my-mediator')
    export class Mediator extends LitElement {

        // The ID of the item that someone has selected.
        // May trigger an update sequence if changed.
        @property({type: Number})
        item_id: number = Number.NaN;

        // We define two slots, in which one can plug widgets.
        // One is for a widgets that can select an `item_id`,
        // while the other is for a widget that displays any
        // data associated with thi `item_id`.
        override render() {
            console.log("[Mediator] rendering");
            // When the Mediator receives our `selected` event,
            // this will call the `onSelected` function.
            return html`<h2>Mediator:</h2>
                  <div @selected=${this.onSelected}>
                      <slot name="selector" />
                  </div>
                  <div>
                      <slot name="viewer" />
                  </div>`;
        }

        // Called when our `selected` event bubbles up
        // from the Selector widget.
        private onSelected(e : CustomEvent) {
            console.log("[Mediator] Received selected from selector: ",e.detail.id);
            // The event embbeds the selected `item_id`.
            // We update the property, which will automagically
            // trigger an update sequence.
            this.item_id = e.detail.id;
        }

        // This is a handle on the widget that's in the Viewer slot.
        // It return an array, and the child widget is in the first element.
        @queryAssignedElements({slot:"viewer"})
        viewer!: Array<HTMLElement>;

        // The corresponding getter.
        getViewer(): HTMLElement {
            return this.viewer[0];
        }

        // Every time the Mediator is updated
        //   (whether it's because `this.item_id` was changed directly,
        //   or because it received an event from a child —selector— widget),
        // we propagate the `item_id` down to the widget in the Viewer slot.
        override updated(changedProperties:PropertyValues<any>): void {
            // Propagate the update to the Lit super class.
            super.updated(changedProperties);

            if(!Number.isNaN(this.item_id)) { // Sanity check.
                // Handle of the widget itself.
                let child = this.getViewer();
                console.log("[Mediator] Set child viewer widget's selection to: ", this.item_id);
                // Change the item_id attribute of the Viewer widget.
                child.setAttribute("item_id", `${this.item_id}`);
            }
        }
    }

    declare global {
      interface HTMLElementTagNameMap {
        'my-mediator': Mediator;
      }
    }


Viewer Widget
=============

.. code-block:: typescript
    import {LitElement, html} from 'lit';
    import {customElement, property, state} from 'lit/decorators.js';

    // The Viewer widget is responsible for displaying any information
    // that comes down from the Mediator.
    @customElement('my-viewer')
    export class Viewer extends LitElement {

        // We overload the setter for the `item_id` attribute
        // because we want to trigger an update of the corresponding data.
        // Hence, every time the Mediator widget does change this attribute,
        // we will fetch new data.
        @property({type: Number})
        set item_id(item_id: number) {
            console.log("[Viewer] Set item_id to", item_id);
            // The "true" attribute is private and prefixed by convention.
            this._item_id = item_id;
            this.fetchItem(item_id);
            this.requestUpdate("item_id", item_id);
        }
        // The "true" attribute.
        private _item_id: number = Number.NaN;
        // The corresponding getter.
        get item_id() { return this._item_id; }

        // The function called when the `item_id` is changed.
        // It download the corresponding data that this widget is displaying.
        private async fetchItem(id: number): Promise<any> {
            const apiUrl = `http://localhost:8000/dev/data.json`;
            var response: any;
            try {
                // Wait for the asynchronous `fetch` function to terminate.
                // Either it ends on a result or raise an exeption.
                response = await fetch(apiUrl);
            } catch (error) {
                console.warn("[Viewer]", error);
            }
            if (!response.ok) {
                throw new Error(response.statusText);
            } else {
                console.log("[Viewer] Fetched item for item_id ", id);
                // Convert the payload to JSON.
                const items = await response.json();
                // Get the first item.id of the list of items.
                const item = items.find((item: any) => item.id === (id || 1));
                // Set the fetched data as the new ones
                // to display in the Viewer widget.
                this.item = item;
            }
        }

        // This attribute holds the data that this widget is actually displaying.
        // As a `state`, every time it is changed, it will automatically
        // trigger an update sequence.
        @state()
        item: any = {};

        // This Lit function is called in the update sequence.
        // From there, we should have some data to display in `this.item`.
        override render() {
            console.log("[Viewer] rendering", this.item_id);
            if (Number.isNaN(this.item_id)) {
                console.log("[Viewer] nothing selected");
                return html`Nothing selected`;
            }
            // Extract some data field.
            const name = this.item["name"];
            // Display it.
            const content = html`<h2>Viewer:</h2>
                <p>Selected item:
                    ${name}
                </p>`;
            console.log("[Viewer] rendered:", name);
            return content;
        }
    }

    declare global {
      interface HTMLElementTagNameMap {
        'my-viewer': Viewer;
      }
    }



.. rubric:: Notes and References

.. [#LIT] See `Lit's documentation <https://lit.dev/docs/composition/component-composition/>`_ for more details.

