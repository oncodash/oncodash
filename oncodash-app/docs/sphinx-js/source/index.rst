.. 
    oncodash-app documentation master file, created by
    sphinx-quickstart on Tue Jan 11 16:38:31 2022.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.
..
    Python's recommended sections marks:
        # with overline, for parts
        * with overline, for chapters
        =, for sections
        -, for subsections
        ^, for subsubsections
        ", for paragraphs

###############################
Oncodash frontend documentation
###############################

************
Architecture
************

Open Web Components
===================

Oncodash makes a heavy use of reusable custom elements for its Graphical User Interface (GUI).
Those "widgets" are implemented following an open standard,
to allow for an easier composition of widgets within "views",
and better integration with third parties.

Web components [#WC]_ uses three main concepts:

Custom elements
    Javascript APIs allowing to define our own widgets.

Shadow DOM
    Javascript APIs for inserting a part of the Document Ojbect Model (DOM)
    that is rendered separately from the main document,
    allowing to keep the implementation details hidden from the main templates.

HTML templates
    A separate HTML DOM tree that is displayed at runtime, on demand.

Using this approach, one can design interactive graphical widgets
that can be inserted in any view by just using a named HTML tag,
allowing to share them across various frontends.


Lit Component
=============

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

The preferred composition architecture in Oncodash is to use composition of classes,
using Lit's *reactive controllers* instead of *mixins*, unless necessary.
See `Lit's documentation <https://lit.dev/docs/composition/component-composition/>`_ for more details.


************
Main modules
************

..
    FIXME: for some reason, shpinx-js does not allow for passing :maxdepth: or :caption:.

.. toctree::

    explainer


.. rubric:: Notes and References

.. [#WC] For more details, see the `Web Components <https://developer.mozilla.org/en-US/docs/Web/Web_Components>`_ page on the MDN.


..
    FIXME there is no recursive autosummary in sphinx-js?

    ******************
    Complete Reference
    ******************

    .. autofunction:: sayIt


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
