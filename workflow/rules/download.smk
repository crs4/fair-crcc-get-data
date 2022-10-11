
rule fetch_file:
    input:
        get_source_remote("{filename}"),
    output:
        temp("encrypted/{filename}")
    log:
        "logs/fetch-{filename}.log"
    benchmark:
        "bench/fetch-{filename}.bench"
    resources:
        mem_mb = 1024  # guessed and probably overestimated
    shell:
        """
        cp --link {input:q} {output:q}
        """


rule validate_file:
    input:
        index = rules.decrypt_index.output.index
    output:
        touch("encrypted/{filename}.validated")
    log:
        "logs/validate-{filename}.log"
    benchmark:
        "bench/validate-{filename}.bench"
    resources:
        mem_mb = 1024  # guessed and probably overestimated
    shell:
        """
        (grep $(basename {filename} | cut -d '\t' -f 3 | paste - <(echo {filename}) | sha256sum --check)
        && touch "encrypted/{filename}.validated"
        """

rule place_file:
    input:
        "decrypted/{filename}"
    output:
        get_dest_remote("{filename}")
    log:
        "logs/place-{filename}.log"
    benchmark:
        "bench/place-{filename}.bench"
    resources:
        mem_mb = 1024  # guessed and probably overestimated
    shell:
        """
        cp --link {input:q} {output:q}
        """
