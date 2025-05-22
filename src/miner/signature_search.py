import pyhmmer
import json

alphabet = pyhmmer.easel.Alphabet.amino()

pipeline = pyhmmer.plan7.Pipeline(alphabet)


def get_family_specifics(enzyme_family):
    """Load positions and signatures for a specific enzyme family

    Args:
        enzyme_family (str):
            vanadium-dependent, flavin-dependent,
            sam-dependent (S-Adenosyl-L-Methionine-dependent),
            non-heme-fe (Non-heme iron alphaketoglutarate-dependent),
            dimetal-carboxylate
    """
    with open("metadata.json") as enzyme_info:
        family_info = json.load(enzyme_info)
        return family_info[f"{enzyme_family}"]

def align_to_phmm(hmm_path, seq_path):
    """Align sequences against a pHMM and save the hits

    Args:
        hmm_path (str): path to the pHMM file
        seq_path (str): path to the fasta file with protein sequences
    """
    with pyhmmer.plan7.HMMFile(hmm) as hmm_file:
        hmm = hmm_file.read()

        with pyhmmer.easel.SequenceFile(seq_path, digital=True, alphabet=alphabet) as seq_file:
            sequences = seq_file.read_block()
            pipeline = pipeline.plan7.Pipeline(hmm.alphabet)
            hits = pipeline.search_hmm(hmm, seq_file)
            hits[0].domains[0].alignment.hmm_sequence
    return hits

def iter_target_match(alignment):
    position = alignment.hmm_from
    for hmm_letter, amino_acid in zip(alignment.hmm_sequence, alignment.target_sequence):
        if hmm_letter != ".":
            yield position, amino_acid
            position += 1

def get_catalytic_residues(hits, catalytic_positions):
    for hit in hits:
        for domain in hit.domains:
            ali = domain.alignment
            aligned = dict(iter_target_match(ali))

            try:
                signature = [aligned[x] for x in catalytic_positions]
            except KeyError:
                print("Domain is likely too short")
            return signature

def compare_target_to_known(hmm_path, seq_path, family, specifics: None|str):
    """Find the residues in functionally important positions in your target enzymes.
    You can use this function without the specifics, in that case, you are only searching
    the pHMMs.

    Args:
        hmm_path (str):
        seq_path (str):
        enzyme_family (str):
            vanadium-dependent, flavin-dependent,
            sam-dependent (S-Adenosyl-L-Methionine-dependent),
            nhfe (Non-heme iron alphaketoglutarate-dependent),
            dimetal-carboxylate

        specifics (str): subgroup you would like to target,
                         flavin-dependet (canonical: trp, phenolic, pyrrole; uncanonical)
                         vanadium-dependent (chloroperoxidase: selective, non-selective; bromoperoxidase; iodoperoxidase)
                         sam-dependent (chlorinase, fluorinase)
                         nhfe   (variant A: nucleotide, amino acid, indole_alkaloid; variant B)
                         dimetal-carboxylate (putative_catalytic_residues)
    """
    hits = align_to_phmm(hmm_path, seq_path)
    family_residues = get_family_specifics(family)
    if specifics:
        signature = get_catalytic_residues(hits, family_residues[specifics])
        return hits, signature

    return hits