Explainer
=========

Causal Network Visualization
----------------------------

The fundamental questions raised in a tumour board are:

1. what kind of treatment may improve the patient's health, and
2. what kind of treatment the patient can tolerate.

To help oncologists to explore the data involved with these questions,
we designed a diagram that reads from left to right, showing at least:

1. the existing samples,
2. the detected alterations, 
3. the actionable drugs,
4. the foreseen side-effects.

This diagram takes the form of a network, where the nodes are the object of interest,
and the directed edges figures the evidences that links one object to another.
Those evidences are drawn as arrows, which displays both the *strength* of the evidence
and its *uncertainty*.
To that end, we use a visual grammar [#Bae]_ which have been proven to maximize
the efficiency of interpretation for visual representation of causes and effects:

- causal relationships are figured by arrows linking state nodes,
- the "strength" of the relationship is figured by the width of the arrow,
- the "certainty" of the relationship is fugured by the opacity and the fuzziness of the drawing (the more uncertain, the more transparent and blurred).

Additionaly, the graph is shaped to be read from the left to the right,
with nodes grouped on columns evenly spread, so as to ease the reading.

To read more about the underlying concept of Bayesian networks, see the `backend's documentation of the Explainer widget </backend/explainer.html>`_.


Widget architecture
-------------------

The widget :class:`Oncoview` is a :class:`LitElement`_ which fetch its data from the "explainer/networks" API entrypoint.
The expected data is a JSON graph encoding a directed graph, as a list of nodes and a list of links.
Each link holds a "strength" and a "certainty" data field.
See the backend's documentation for the detail of the graph data structure.

The visualization is dnawn using a Scalable Vector Graphic (SVG) object right within the page.
The :func:`drawGraph` is called when the widget is rendered and is in charge of adding
the SVG objects figuring node labels and link arrows.
Nodes and links are grouped within SVG groups.
All SVG objects have CSS class, "link" for arrows, and "label-box" for nodes.

Nodes are drown by the :func:`drawColumn` function,
which proceed column by column, evenly spreading the labels on each vertical axis.

Arrows are drawn by the :func:`drawLinks` function, as a rotated paths.
Their colors is adjusted to the strength of the link through opacity and
their certainty through the SVG blur filter.

.. 
    FIXME sphinx does not find the sources
    Reference
    ---------

    .. autoclass:: ExplainerView
        :members:

    .. autofunction:: drawGraph

    .. autofunction:: drawLinks

    .. autofunction:: drawColumn


.. rubric:: Notes and References

.. [#Bae] Bae, J., Ventocilla, E., Riveiro, M., Helldin, T., & Falkman, G., `Evaluating Multi-Attributes on Cause and Effect Relationship Visualization <https://doi.org/10.5220/0006102300640074>`_. Proceedings of the 12th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications (VISIGRAPP 2017), Volumne 3: IVAPP, 64–74, 2017.


