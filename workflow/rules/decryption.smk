# The decrypt_file rule is general enough that it could be applied to the index
# as well.  To ensure the index is processed by the decrypt_index rule we set
# this rule's priority higher than the more general one.
ruleorder: decrypt_index > decrypt_file


checkpoint decrypt_index:
    input:
        index = get_source_remote("index.tsv.c4gh")
    output:
        index = get_dest_remote("index.tsv")
    log:
        "logs/decrypt-index.log",
    params:
        recipient_key=config["recipient_key"]
    shell:
        # Because this rules outputs with get_dest_remote it needs to create
        # the parent directories of its output file
        """
        mkdir -p "$(dirname {output:q})" &&
        crypt4gh decrypt \
                --sk {params.recipient_key:q} \
                < {input:q} > {output:q} 2> {log}
        """

rule decrypt_file:
    input:
        encrypted = "encrypted/{filename}.c4gh"
    output:
        decrypted = get_dest_remote("{filename}")
    log:
        "logs/decrypt-{filename}.log",
    benchmark:
        "bench/decrypt-{filename}.bench"
    params:
        recipient_key = config["recipient_key"]
    resources:
        mem_mb = 1024,  # guessed and probably overestimated
    shell:
        # 1. Because this rules outputs with get_dest_remote it needs to create
        # the parent directories of its output file.
        """
        mkdir -p "$(dirname {output:q})" &&
        crypt4gh decrypt \
                --sk {params.recipient_key:q} \
                < {input.encrypted:q} > {output.decrypted:q} 2> {log:q}
        """
