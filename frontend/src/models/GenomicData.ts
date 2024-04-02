/**
 * Structure of the genomic data from the server
 */
export interface GenomicData {
  genomic: {
    putative_functionally_relevant_variant: [number, string]
    variants_of_unknown_functional_significance: [number, string]
    putative_functionally_neutral_variants: [number, string]
    other_alterations: [number, string]
  }
  putative_functionally_relevant_variant: Record<string, GeneData>
  variants_of_unknown_functional_significance: Record<string, GeneData>
  putative_functionally_neutral_variants: Record<string, GeneData>
  other_alterations: Record<string, GeneData>
}

export interface GeneData {
  description: string
  alterations: Array<AlterationData>
}

export interface AlterationData {
  name: string,
  description: string
  row: Array<AlterationSampleData>
}

export interface AlterationSampleData {
  samples_ids: string
  samples_info: string
  treatment_phase: string
  tumor_purity: string
  mutation_affects: string
  reported_sensitivity: string
}
