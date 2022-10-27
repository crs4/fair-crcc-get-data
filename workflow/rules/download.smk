
rule fetch_file:
    """
    Fetch file from the source.
    The file must be referenced by the dataset index.
    The file will be renamed from its mangled name to its normal name.

    We don't run this rule in a container (unlike the rest of the workflow)
    so that we can create hard links on the local FS, if the destination is 'local'.
    """
    input:
        lambda w: get_source_remote(get_mangled_file_name(w.filename))
    output:
        temp("encrypted/{filename,.+\.c4gh}")
    log:
        "logs/fetch-{filename}.log"
    benchmark:
        "bench/fetch-{filename}.bench"
    resources:
        mem_mb = 128
    container: None
    shell:
        # This job is just a target for the data download jobs, so it
        # doesn't really do anything with the files. To create a real
        # output that can be the source for the next job down the DAG
        # we create a symlink to the temporary download file created by
        # snakemake.
        """
        /bin/cp --link {input:q} {output:q}
        """


rule validate_file:
    input:
        index = rules.decrypt_index.output.index,
        data_file = "encrypted/{filename}"
    output:
        touch("encrypted/{filename,.+\.c4gh}.validated")
    log:
        "logs/validate-{filename}.log"
    benchmark:
        "bench/validate-{filename}.bench"
    resources:
        mem_mb = 1024  # guessed and probably overestimated
    shell:
        # This gets a big intricate implemented as a single shell expression... Consider implementing a helper script.
        # The code gets the relevant line from the index and selects the checksum
        # field (field 3, extracted with `cut`). The `paste` command is then used
        # to form a line with the filename and checksum, as accepted by `sha256sum --check`.
        # This last command performs the validation.
        # set -o pipefail is required to catch errors in the pipeline.
        """
        (grep {wildcards.filename:q} {input.index:q} | \
         cut -d '\t' -f 3 | \
         paste - <(echo encrypted/{wildcards.filename:q}) | sha256sum --check) && \
        touch "encrypted/{wildcards.filename:q}.validated"
        """
