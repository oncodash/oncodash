/**
 * Structure of the genomic data from the server
 */
export interface GenomicData {
  genomic: {
    actionable_relevant_targets: [number, string]
    putative_functionally_relevant_variants: [number, string]
    other_variants: [number, string]
  }
  actionable_relevant_targets: Record<string, GeneData>
  putative_functionally_relevant_variants: Record<string, GeneData>
  other_variants: Record<string, GeneData>
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
