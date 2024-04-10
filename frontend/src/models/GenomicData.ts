/**
 * Structure of the genomic data from the server
 */
export interface GenomicData {
  genomic: {
    actionable_aberrations: [number, string]
    putative_functionally_relevant_variants: [number, string]
    other_variants: [number, string]
  }
  actionable_aberrations: Record<string, GeneData>
  putative_functionally_relevant_variants: Record<string, GeneData>
  other_variants: Record<string, GeneData>
  samples_info: {
    name: string
    row: Array<SampleInfo>
  }
}

export interface SampleInfo {
  sample: string
  purity: string
  ploidy: string
  tumor_site: string
  sample_time: string
  sample_type: string
}

export interface GeneData {
  description: string
  alterations: Array<AlterationData>
}

export interface AlterationData {
  name: string,
  description: string
  reported_sensitivity: string
  row: Array<AlterationSampleData>
}

export type AlterationSampleData = AlterationSampleDataSNP | AlterationSampleDataCNV

export interface AlterationSampleDataSNP {
  samples: string
  "AD.0": string
  "AD.1": string
  DP: string
  AF: string
  nMajor: string
  nMinor: string
  LOHstatus: string
  "expHomCI.cover": string
}

export interface AlterationSampleDataCNV {
  sample: string
  nMajor: string
  nMinor: string
}
