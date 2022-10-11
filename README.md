# Snakemake workflow: FAIR CRCC - get data

[![Snakemake](https://img.shields.io/badge/snakemake-≥6.3.0-brightgreen.svg)](https://snakemake.github.io)
[![GitHub actions status](https://github.com/crs4/fair-crcc-get-data/workflows/Tests/badge.svg?branch=main)](https://github.com/crs4/fair-crcc-get-data/actions?query=branch%3Amain+workflow%3ATests)


A Snakemake workflow for downloading and decrypting Crypt4GH-encrypted sensitive data from
the [CRC
Cohort](https://www.bbmri-eric.eu/scientific-collaboration/colorectal-cancer-cohort/)
[access request](https://www.bbmri-eric.eu/services/access-policies/).

## What's the CRC Cohort?

The CRC Cohort is a collection of clinical data and digital high-resolution
digital pathology images pertaining to tumor cases.  The collection has been
assembled from a number of participating biobanks and other partners through the
[ADOPT BBMRI-ERIC](https://www.bbmri-eric.eu/scientific-collaboration/adopt-bbmri-eric/) project.

Researchers interested in using the data for science can file an application for
access.  If approved, the part of the dataset required for the planned and
approved work can be copied to the requester's selected secure storage location
(using this workflow).

## Usage

The usage of this workflow is described in the [Snakemake Workflow Catalog](https://snakemake.github.io/snakemake-workflow-catalog/?usage=crs4%2Ffair-crcc-get-data).

If you use this workflow in a paper, don't forget to give credits to the authors
by citing the URL of this (original) repository and its DOI (see above).

# TODO

* The workflow will occur in the snakemake-workflow-catalog once it has been
  made public. Then the link under "Usage" will point to the usage instructions
  if `<owner>` and `<repo>` were correctly set.
