/**
 * Structure of the genomic data from the server
 */
export interface GenomicData {
  genomic: {
    actionable_aberrations: [number, string]
    other_variants: [number, string]
  }
  actionable_aberrations: Record<string, GeneData>
  other_variants: Record<string, GeneData>
  order: Record<string, Array<string> >
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
  alt_type: string
  treatments: Record<string, string>
}

export type AlterationSampleData = AlterationSampleDataSNP | AlterationSampleDataCNV | AlterationSampleDataSV

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
  "HGVS.change": string

 /* FIXME ugly hack */
  is_of_type: 'AlterationSampleDataSNP'
}

export interface AlterationSampleDataCNV {
  sample: string
  nMajor: string
  nMinor: string

 /* FIXME ugly hack */
  is_of_type: 'AlterationSampleDataCNV'
  samples: string
  "AD.0": string
  "AD.1": string
  DP: string
  AF: string
  // nMajor: string
  // nMinor: string
  LOHstatus: string
  "expHomCI.cover": string
}

export interface AlterationSampleDataSV {
  is_of_type: 'AlterationSampleDataSV'
  sample: string
  undisruptedCopyNumber: string
  affectedCopyNumber: string

 /* FIXME ugly hack */
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
