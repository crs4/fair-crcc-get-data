# Snakemake workflow: FAIR CRCC - get data

[![Snakemake](https://img.shields.io/badge/snakemake-≥6.3.0-brightgreen.svg)](https://snakemake.github.io)
[![GitHub actions status](https://github.com/crs4/fair-crcc-get-data/workflows/Tests/badge.svg?branch=main)](https://github.com/crs4/fair-crcc-get-data/actions?query=branch%3Amain+workflow%3ATests)

A Snakemake workflow for downloading and decrypting Crypt4GH-encrypted sensitive
data from the [CRC
Cohort](https://www.bbmri-eric.eu/scientific-collaboration/colorectal-cancer-cohort/)
[access request](https://www.bbmri-eric.eu/services/access-policies/).

## What's the CRC Cohort?

The CRC Cohort is a collection of clinical data and digital high-resolution
digital pathology images pertaining to tumor cases.  The collection has been
assembled from a number of participating biobanks and other partners through the
[ADOPT BBMRI-ERIC](https://www.bbmri-eric.eu/scientific-collaboration/adopt-bbmri-eric/)
project.

Researchers interested in using the data for science can file an application for
access.  If approved, the part of the dataset required for the planned and
approved work can be copied to the requester's selected secure storage location
(using this workflow).

## Usage

The workflow needs **three main inputs**, which are all provided via the
**configuration file**:

1. The source of the data;
2. The destination for the data;
3. The recipient's private encryption key, which will be used to decrypt the
   data as it's downloaded.

Optionally, you can specify filters to only fetch part of the dataset.

For source and destination, all the storage types supported by Snakemake can be
used -- from locally mounted storage to remote S3, FTP, etc.

### Configuration file

An example configuration is available under [config/example_config.yml](config/example_config.yml),
while the full, documented schema is available in the file <workflow/schemas/config.schema.yml>.

### Filters

A list of filter rules can be specified to download only parts of the full
collection. The filters follow a logic similar to rsync (for those who are
familiar with that tool).

* Filter rules specify an `action` (*include* or *exclude*) and a **glob
  expression** `pattern` for matching files.
* The pattern is applied to the *original file names* (the ones with which the
  files would be saved in the destination storage). This is the name you'll find
  the in the index.tsv file without the .c4gh extension.
* The filter patterns are tried in the order they are specified:
  * the first one that matches is applied;
  * if no filters match a file name, the file is included.

#### Examples

Download everything except "test-file_2.txt":

```yaml
  filters:
  - action: exclude
    pattern: "test-file_2.txt"
```

Only download files matching the specific pattern `sample_123*.tiff`

```yaml
  filters:
  - action: include
    pattern: "sample_123*.tiff"
  - action: exclude
    pattern: "*"
```

### The index file

In addition to the data files, the workflow will generate a file called
`index.tsv`. This is an index to the dataset at the source location.

Format: tab-separated fields.  The fields are:

1. file name at the source (this name is a random UUID);
2. original encrypted file name;
3. checksum of the encrypted file.

The checksum is used to validated the integrity of the downloaded file.

Note that depending on the filters you apply, some or all of the files in the
index may not be fetched.

**Remember:** the filter patterns are applied to the index file names with the
`.c4gh` extension removed.

## Authors

If you use this workflow in a paper, don't forget to give credits to the authors
by citing the URL of this (original) repository and its DOI (TBD).

* Luca Pireddu <luca.pireddu@crs4.it>
