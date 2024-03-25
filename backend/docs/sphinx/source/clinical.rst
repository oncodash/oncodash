
Clinical
========

Clinical data sources
---------------------

The clinical data is sourced from an outside clinical database. The data is divided into two datasets:

1. Clinical export: this file consists of patient-level state data without any time series or history, such as age at diagnosis, disease histology, treatment strategy and variables like overall survival and progression-free survival. Some variables may change over time, mostly from undefined to defind. Only the current state of the variables in this file is of importance, not their history.

2. Time series data set: this data set contains information such as laboratory test results, chemotherapy information, sampling timepoints and operations. Timeline plots can be constructed from this data to visualise the whole treatment and disease progression from initial diagnosis.

In the current DECIDER setting, the source system does not allow for automatic retrieval of data via API connection. The data is provided in two separate CSV files.