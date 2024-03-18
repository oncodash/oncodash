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

The underlying data structure is thus a kind of Bayesian Network, able to manage uncertainties.
To this end, the Explainer makes use of *Credal Network*, which models uncertainties as intervals.

To read more about the visualization of this network, see the `frontend's documentation of the Explainer widget </frontend/explainer.html>`_.


Credal Networks
---------------

Credal networks [#Cozman]_ are graph-based statistical models, sharing many properties with Bayesian networks
but allowing more flexibility by dealing with imprecision and uncertainty.
Instead of probability mass functions as parameters,
credal networks parameters take values in closed convex sets (also called credal sets).
In practical terms, while in a Bayesian network every variable is associated to a probability or
a conditional probability, in a credal network variables may also be associated to probabilistic inequalities.

One of the challenges we may have to deal with is the sparsity of the data that prevents us from
learning the complete conditional probability tables (CPT [#CPT]_).
To tackle it, it is possible to use Noisy-OR gates [#Antonucci]_ given an existing network structure.
They are usually used to describe the interactions between different causes of a common effect,
where each cause is assumed to be sufficient to cause the effect and
where the ability to cause the effect is assumed independent of the presence of the other causes.

An extension of the Noisy-OR takes into account the situation where the causes of the effect are not all known,
which results in the effect occurring even if all the considered causes are false.
It’s the leaky Noisy-OR.

The use of credal networks seems well adapted to our situation in order to
integrate different data in the same graph, while leaving a certain range of uncertainty.
However, the construction of such a network requires a lot of data in order
to describe all the cases in the CPT and is very computationally expensive.
The use of Noisy-OR can reduce these difficulties but is based on the assumption that the causes are additive.

Reasoning features of the Explainer are based on the `pyAgrum <https://pyagrum.readthedocs.io>`_
Python library, which is dedicated to Bayesian networks and other graphical models.


Main Datastructure
------------------

TODO



Explainer's *Views*
-------------------

The main entry point to Explainer is the :mod:`network <explainer.urls>` URL.
It serves the :class:`NetworkViewSet <explainer.views.NetworkViewSet>` functor:

TODO

.. autosummary

.. explainer.views.NetworkViewSet

See the full module documentation: :mod:`explainer`.


.. rubric:: Notes and References

.. [#Cozman] Fabio G. Cozman, Credal networks. Artificial Intelligence, 120(2):199–233, 2000.
.. [#CPT] A **complete** *Conditional Probability Table* holds the probabilities that the considered node of the network is true, for all the cartesian products of its input edges.
.. [#Antonucci] Alessandro Antonucci, The imprecise noisy-or gate. Fusion 2011 — 14th International Conference on Information Fusion, 01/2011.
