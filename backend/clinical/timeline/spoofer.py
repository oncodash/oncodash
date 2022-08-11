import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import math, sys
from matplotlib.figure import Figure

verbose = True
filter_lab = True

# Burden decrease per outcome, imaginary
relative_burden = {
	'CR': [0, 30],
	'PR': [30, 50],
	'PD': [50, 110]
}

color_scheme = {
	'orange': '#e88700',
	'dark_orange': '#e35300',
	'light_green': '#50bf86',
	'violet': '#500091',
	'green': '#30a64c',
	'dark_red': '#a32e00',
}

configDicts = {

	'full': {
		'ca125': {
			'lab': True,
			'plot': True,
			'name': 'CA12-5',
			'color': color_scheme['orange'],
			'y_scale': 'linear',
			'y_lim': [0, 500],
			'hard_cap': False,
			'normal_level': [35], 
		},
		'platelets': {
			'lab': True,
			'plot': False,
			'name': 'Platelets',
			'color': color_scheme['green'],
			'normal_level': [150, 360]
		},
		'leuk': {
			'lab': True,
			'plot': False,
			'name': 'Leukocytes',
			'color': color_scheme['dark_red'],
			'normal_level': [3.4,8.2]
		},	
		'hb': {
			'lab': True,
			'plot': False,
			'name': 'Haemoglobin',
			'color': color_scheme['dark_red'],
			'normal_level': [117,155],
		},
		'chemotherapy': {
			'plot': True,
			'color': color_scheme['light_green'],
			'explode_chemos': True,
			'simplify_names': True,
		},
		'track_events': {
			'plot': True,
			'y_offset': 0,
			'legend': {
				'mode': None,
				'loc': 'upper left',
				'framealpha': 1.0,
			},
			'tracks': {
				'clinical': {
					'plot': True,				
					'name': 'Clinical',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'diagnosis': {
							'plot': True,
							'marker': 's',
							'color': color_scheme['orange'],
							'label': 'Diagnosis',
						},
						'oper1': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'oper2ids': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'last_date_of_primary_therapy': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['light_green'],
							'label': 'End of primary therapy',
						},					
						'primary_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'2nd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'3rd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'4th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},	
						'5th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},
						'death': {
							'plot': True,
							'marker': 'D',
							'color': '#000',
							'label': 'Death',
						},
						'operation': {
							'plot': True,
							'marker': 'v',
							'color': '#666',
							'label': 'Other operation'
						},
					},
				},
				'radiology': {
					'plot': True,
					'name': 'Radiology',
					'color': '#aaa',
					'padding_top': 1,
					'label_column': 'name',
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},				
					'events': {
						'radiology': {
							'omit_legend': True,
							'plot': True,
							'marker': 'o',
							'color': color_scheme['green'],
							'label': 'Radiology',
						}
					}
				},
				'plasma': {
					'plot': True,
					'name': 'Tykslab plasma',
					'color': '#aaa',
					'padding_top': 2.2,
					'label_column': 'aux_id',
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},
					'events': {
						'tykslab_plasma': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Plasma',
						},
						'ctdna_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#d92518',
							'label': 'ctDNA'
						},
					},				
				},
				'fresh_sample': {
					'plot': False,
					'name': 'Fresh tissue',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'fresh_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},
						'fresh_sample_sequenced': {
							'plot': True,
							'marker': 'o',
							'color': color_scheme['orange'],
							'label': 'Sequenced'
						},					
					},				
				},
				'ascites': {
					'plot': False,
					'name': 'Ascites',
					'color': '#aaa',
					'padding_top': 1.2,
					'label_column': 'result',
					'label_placement': {
						'x_offset': -0.5,
						'y_offset': 0.6,
						'rotation': 30
					},
					'events': {
						'ascites': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},				
					},				
				},			
			},
		},
	},

	'labs': {
		'ca125': {
			'lab': True,
			'plot': True,
			'name': 'CA12-5',
			'color': color_scheme['orange'],
			'y_scale': 'linear',
			# 'y_lim': [0, 500],
			'hard_cap': False,
			'normal_level': [35], 
		},
		'platelets': {
			'lab': True,
			'plot': True,
			'name': 'Platelets',
			'color': color_scheme['green'],
			# 'normal_level': [150, 360]
		},
		'leuk': {
			'lab': True,
			'plot': False,
			'name': 'Leukocytes',
			'color': color_scheme['dark_red'],
			'normal_level': [3.4,8.2]
		},	
		'hb': {
			'lab': True,
			'plot': True,
			'name': 'Haemoglobin',
			'color': color_scheme['dark_red'],
			# 'normal_level': [117,155],
		},
		'chemotherapy': {
			'plot': False,
			'color': color_scheme['light_green'],
			'explode_chemos': True,
			'simplify_names': True,
		},
		'track_events': {
			'plot': False,
			'y_offset': 0,
			'legend': {
				'mode': None,
				'loc': 'upper left',
				'framealpha': 1.0,
			},
			'tracks': {
				'clinical': {
					'plot': False,				
					'name': 'Clinical',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'diagnosis': {
							'plot': True,
							'marker': 's',
							'color': color_scheme['orange'],
							'label': 'Diagnosis',
						},
						'oper1': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'oper2ids': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'last_date_of_primary_therapy': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['light_green'],
							'label': 'End of primary therapy',
						},					
						'primary_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'2nd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'3rd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'4th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},	
						'5th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},
						'death': {
							'plot': True,
							'marker': 'D',
							'color': '#000',
							'label': 'Death',
						},
						'operation': {
							'plot': True,
							'marker': 'v',
							'color': '#666',
							'label': 'Other operation'
						},
					},
				},
				'radiology': {
					'plot': False,
					'name': 'Radiology',
					'color': '#aaa',
					'padding_top': 1,
					'label_column': 'name',
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},				
					'events': {
						'radiology': {
							'omit_legend': True,
							'plot': True,
							'marker': 'o',
							'color': color_scheme['green'],
							'label': 'Radiology',
						}
					}
				},
				'plasma': {
					'plot': True,
					'name': 'Tykslab plasma',
					'color': '#aaa',
					'padding_top': 2.2,
					'label_column': 'aux_id',
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},
					'events': {
						'tykslab_plasma': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Plasma',
						},
						'ctdna_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#d92518',
							'label': 'ctDNA'
						},
					},				
				},
				'fresh_sample': {
					'plot': False,
					'name': 'Fresh tissue',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'fresh_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},
						'fresh_sample_sequenced': {
							'plot': True,
							'marker': 'o',
							'color': color_scheme['orange'],
							'label': 'Sequenced'
						},					
					},				
				},
				'ascites': {
					'plot': False,
					'name': 'Ascites',
					'color': '#aaa',
					'padding_top': 1.2,
					'label_column': 'result',
					'label_placement': {
						'x_offset': -0.5,
						'y_offset': 0.6,
						'rotation': 30
					},
					'events': {
						'ascites': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},				
					},				
				},			
			},
		},
	},

	'chemo': {
		'ca125': {
			'lab': True,
			'plot': True,
			'name': 'CA12-5',
			'color': color_scheme['orange'],
			'y_scale': 'linear',
			# 'y_lim': [0, 500],
			'hard_cap': False,
			'normal_level': [35], 
		},
		'platelets': {
			'lab': True,
			'plot': False,
			'name': 'Platelets',
			'color': color_scheme['green'],
			# 'normal_level': [150, 360]
		},
		'leuk': {
			'lab': True,
			'plot': False,
			'name': 'Leukocytes',
			'color': color_scheme['dark_red'],
			'normal_level': [3.4,8.2]
		},	
		'hb': {
			'lab': True,
			'plot': False,
			'name': 'Haemoglobin',
			'color': color_scheme['dark_red'],
			# 'normal_level': [117,155],
		},
		'chemotherapy': {
			'plot': True,
			'color': color_scheme['light_green'],
			'explode_chemos': True,
			'simplify_names': True,
		},
		'track_events': {
			'plot': False,
			'y_offset': 0,
			'legend': {
				'mode': None,
				'loc': 'upper left',
				'framealpha': 1.0,
			},
			'tracks': {
				'clinical': {
					'plot': False,				
					'name': 'Clinical',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'diagnosis': {
							'plot': True,
							'marker': 's',
							'color': color_scheme['orange'],
							'label': 'Diagnosis',
						},
						'oper1': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'oper2ids': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'last_date_of_primary_therapy': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['light_green'],
							'label': 'End of primary therapy',
						},					
						'primary_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'2nd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'3rd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'4th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},	
						'5th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},
						'death': {
							'plot': True,
							'marker': 'D',
							'color': '#000',
							'label': 'Death',
						},
						'operation': {
							'plot': True,
							'marker': 'v',
							'color': '#666',
							'label': 'Other operation'
						},
					},
				},
				'radiology': {
					'plot': False,
					'name': 'Radiology',
					'color': '#aaa',
					'padding_top': 1,
					'label_column': 'name',
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},				
					'events': {
						'radiology': {
							'omit_legend': True,
							'plot': True,
							'marker': 'o',
							'color': color_scheme['green'],
							'label': 'Radiology',
						}
					}
				},
				'plasma': {
					'plot': True,
					'name': 'Tykslab plasma',
					'color': '#aaa',
					'padding_top': 2.2,
					'label_column': 'aux_id',
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},
					'events': {
						'tykslab_plasma': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Plasma',
						},
						'ctdna_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#d92518',
							'label': 'ctDNA'
						},
					},				
				},
				'fresh_sample': {
					'plot': False,
					'name': 'Fresh tissue',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'fresh_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},
						'fresh_sample_sequenced': {
							'plot': True,
							'marker': 'o',
							'color': color_scheme['orange'],
							'label': 'Sequenced'
						},					
					},				
				},
				'ascites': {
					'plot': False,
					'name': 'Ascites',
					'color': '#aaa',
					'padding_top': 1.2,
					'label_column': 'result',
					'label_placement': {
						'x_offset': -0.5,
						'y_offset': 0.6,
						'rotation': 30
					},
					'events': {
						'ascites': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},				
					},				
				},			
			},
		},
	},


	'simple': {
		'ca125': {
			'lab': True,
			'plot': True,
			'name': 'CA12-5',
			'color': color_scheme['orange'],
			'y_scale': 'linear',
			'y_lim': [0, 500],
			'hard_cap': False,
			'normal_level': [35], 
		},
		'platelets': {
			'lab': True,
			'plot': False,
			'name': 'Platelets',
			'color': color_scheme['green'],
			'normal_level': [150, 360]
		},
		'leuk': {
			'lab': True,
			'plot': False,
			'name': 'Leukocytes',
			'color': color_scheme['dark_red'],
			'normal_level': [3.4,8.2]
		},	
		'hb': {
			'lab': True,
			'plot': False,
			'name': 'Haemoglobin',
			'color': color_scheme['dark_red'],
			'normal_level': [117,155],
		},
		'chemotherapy': {
			'plot': True,
			'color': color_scheme['light_green'],
			'explode_chemos': True,
			'simplify_names': True,
		},
		'track_events': {
			'plot': True,
			'y_offset': 0,
			'legend': {
				'mode': None,
				'loc': 'upper left',
				'framealpha': 1.0,
			},
			'tracks': {
				'clinical': {
					'plot': True,				
					'name': 'Clinical',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'diagnosis': {
							'plot': True,
							'marker': 's',
							'color': color_scheme['orange'],
							'label': 'Diagnosis',
						},
						'oper1': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'oper2ids': {
							'plot': True,
							'marker': 'v',
							'color': color_scheme['dark_orange'],
							'label': 'IDS / PDS',
						},
						'last_date_of_primary_therapy': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['light_green'],
							'label': 'End of primary therapy',
						},					
						'primary_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'2nd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'3rd_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['violet'], 
							'label': 'Progression',
							'vline': True,
						},
						'4th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},	
						'5th_progression': {
							'plot': True,
							'marker': 'D',
							'color': color_scheme['orange'], 
							'label': 'Progression',
							'vline': True,
						},
						'death': {
							'plot': True,
							'marker': 'D',
							'color': '#000',
							'label': 'Death',
						},
						'operation': {
							'plot': True,
							'marker': 'v',
							'color': '#666',
							'label': 'Other operation'
						},
					},
				},
				'radiology': {
					'plot': True,
					'name': 'Radiology',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},				
					'events': {
						'radiology': {
							'omit_legend': True,
							'plot': True,
							'marker': 'o',
							'color': color_scheme['green'],
							'label': 'Radiology',
						}
					}
				},
				'plasma': {
					'plot': True,
					'name': 'Tykslab plasma',
					'color': '#aaa',
					'padding_top': 2.2,
					'label_column': False,
					'label_placement': {
						'x_offset': 2.4,
						'y_offset': 0.4,
						'rotation': 45
					},
					'events': {
						'tykslab_plasma': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Plasma',
						},
						'ctdna_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#d92518',
							'label': 'ctDNA'
						},
					},				
				},
				'fresh_sample': {
					'plot': False,
					'name': 'Fresh tissue',
					'color': '#aaa',
					'padding_top': 0,
					'label_column': False,
					'events': {
						'fresh_sample': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},
						'fresh_sample_sequenced': {
							'plot': True,
							'marker': 'o',
							'color': color_scheme['orange'],
							'label': 'Sequenced'
						},					
					},				
				},
				'ascites': {
					'plot': False,
					'name': 'Ascites',
					'color': '#aaa',
					'padding_top': 1.2,
					'label_column': 'result',
					'label_placement': {
						'x_offset': -0.5,
						'y_offset': 0.6,
						'rotation': 30
					},
					'events': {
						'ascites': {
							'plot': True,
							'marker': 'o',
							'color': '#234d91',
							'label': 'Fresh tissue / Ascites',
						},				
					},				
				},			
			},
		},
	},
}

# Fix chemotherapy naming, if not already fixed
def fixChemoName(s):

	s = str(s).lower()
	replaces = [  
		['xelox', 'oxaliplatin, capecitabine'],
		['gyn topotekaani-cisplatiini', 'topotecan, cisplatin'],
		['ramusirumabi-paklitakseli', 'ramucirumab, paclitaxel'],
		['capox (colon ca)', 'oxaliplatin, capecitabine'],
		['xelox (colon ca)', 'oxaliplatin, capecitabine'],
		['bev-xel', 'bevacizumab, oxaliplatin, capecitabine'],
		['bevacizumab (colon ca)', 'bevacizumab'],
		['bev-kapesitabiini', 'bevacizumab, capecitabine'],
		['nab-paklitakseli-gem', 'paclitaxel, gemcitabine'],
		['capecitabine (colon ca)', 'capecitabine'],
		['gyn karbo+avastin', 'carboplatin, bevacizumab'],
		['gyn doksorubisiini - karboplatiini', 'doxorubicin, carboplatin'],
		['gyn sisplatiini - gemsitabiini', 'cisplatin, gemcitabine'],
		['gyn paklitakseli - karboplatiini - bevasitsumabi 15mg', 'paclitaxel, carboplatin, bevacizumab'],
		['gyn gemsitabiini vakioannos - karboplatiini - bevasitsumabi "oceans"', 'gemcitabine, carboplatin, bevacizumab'],
		['gyn ifosfamidi lyhyt', 'ifosfamide'],
		['gyn olaparibi (lynparza)', 'olaparib'],
		['erbitux (1.sykli)', 'cetuximab'],
		['erbitux (2.syklistä eteenpäin)', 'cetuximab'],
		['erbitux (2.syklistљ eteenpљin)', 'cetuximab'],
		['olaturamab', 'olaratumab'],
		['etopocide', 'etoposide'],		
		['gyn trastuzumabi', 'trastuzumab'],
		['cabesitabin', 'capecitabine'],
		['trabectidin', 'trabectedin'],
		['citapin', 'citabin'],
		['gyn bevasitsumabi bi-weekly', 'bevacizumab bi-weekly'],
		['bevacizumab maintenance', 'bevacizumab maintenance'],
		['maintenance bevacizumab', 'bevacizumab maintenance'],
		['maintence bevacizumab', 'bevacizumab maintenance'],
		['trastuzumab s.c.', 'trastuzumab s.c.'],
		['trastutsumab s.c.', 'trastuzumab s.c.'],
		['trastutzumab', 'trastuzumab'],
		['trastutsumab', 'trastuzumab'],		
		['paclitazel', 'paclitaxel'],		
	]
	for r in replaces:
		s = s.replace(r[0], r[1])
	s = s.strip()
	return s

# Drop some additional parameters from chemos, if only the substance is relevant
def simplifyChemo(s):
	
	s = s.lower()
	replaces = [
		['liposomal doxorubicin (pld)', 'doxorubicin'],
		['liposomal doxorubicin', 'doxorubicin'],
		['pld', 'doxorubicin'],
		['bi-weekly', ''],
		['weekly', ''],
		['maintenance', ''],
		['s.c.', '']
	]

	for r in replaces:
		s = s.replace(r[0], r[1])

	s = s.strip()
	s = s.capitalize()
	return s

# Therapy names
therapies = ['Carboplatin', 'Carboplatin, paclitaxel', 'Cisplatin', 'Carboplatin, paclitaxel, bevacizumab', 'Paclitaxel', 'Gemsitabin']

# Columns based on ONCOSYS timeline format, see readme for further documentation
output_columns = ['id', 'patient_id', 'cohort_code', 'interval', 'ongoing', 'date', 'date_relative', 'interval_end', 'interval_end_relative', 'interval_length', 'event', 'name', 'result', 'aux_id', 'source_system']

def growth(initial_burden, t):
	'''returns tumor burden based on initial tumor burden (inital_burden) and time (t). Model is somewhat oversimplified'''
	if t <= 0:
		return initial_burden
	else:
		return initial_burden + 10 * np.log(t+10) ** 1.1

def linearGrowth(rng, df, t0, t1, b0, b1):
	''' alters tumor burden from burden b0 to b1 in time t0 to t1'''
	b = b0
	for t in range(t0, t1):
		df.loc[df['t'] == t, 'burden'] = b
		b = (b1 - b0) / (t1 - t0) + b

	df.loc[df['t'] >= t1, 'burden'] = df.apply(lambda row: growth(b1, row['t']-t1+1), axis = 1)

def getCa125(rng, burden, t, mod):
	''' returns ca125 from burden, if timepoint is in presented modulo'''
	if t % mod == 0:
		return max(0, burden * 4 + rng.integers(-10, 10) - 200)
	else:
		return np.nan

def getHb(rng, initial_hb, burden, therapy, t, mod):
	if t % mod == 0:
		return int(initial_hb + rng.integers(-5, 5) - (burden / 100) * 20)
	else:
		return np.nan

def getPlatelets(rng, initial_platelets, burden, therapy, t, mod):
	if t % mod == 0:
		return initial_platelets + rng.integers(-10, 10) + (burden / 100) * 20
	else:
		return np.nan

def getPatientId(rng):
	''' returns patient id '''
	return rng.integers(0, 1000);

def getCohortCode(patient_id):
	''' returns cohort code based on patient id'''
	return f'SPOOF{patient_id}'

def getTherapyCycleId(rng, patient_id, therapy_round):
	return int(f'{patient_id}{therapy_round}{rng.integers(43215,234523523)}')

def getLabId(rng):
	return f'SPOOFLAB_{rng.integers(100000,999999)}'

def getRadiologyEvent(rng):
	return rng.choice(['JA2AT', 'JA3BT', 'JA3AT', 'JA3CT'])

def drawOutcome(rng, nth_outcome=1):
	''' decides the outcome based on number of replase. Primary therapy outcome probabilities from CLOBNET paper'''

	if nth_outcome == 1: # Primary therapy outcome
		
		pCR = 0.486		# Complete response
		pPD = 0.139		# Progressive disease
		pPR = 0.240		# Partial response

	elif nth_outcome > 1 and nth_outcome < 3:

		pCR = 0.4		# Complete response
		pPD = 0.2		# Progressive disease
		pPR = 0.4		# Partial response

	else:

		pCR = 0.2		# Complete response
		pPD = 0.4		# Progressive disease
		pPR = 0.2		# Partial response


	
	pAll = pCR + pPD + pPR
	outcome = rng.choice(['CR', 'PD', 'PR'], p=[pCR/pAll, pPD/pAll, pPR/pAll])

	return outcome

def generatePatient(seed=0):
	'''Generates a patient based on given random seed, returns a complete time series and associated rng'''

	# Set random generator, get patient ID and cohort code
	if seed == 0:
		rng = np.random.default_rng()
		patient_id = getPatientId(rng)
	else:
		rng = np.random.default_rng(seed)
		patient_id = seed

	cohort_code = getCohortCode(patient_id)
	
	# Initial timepoint and array of 10000 days
	t = 0
	day_count = 10000
	days = np.arange(0, day_count)

	# Data frame for background simulated data, which will be sampled to output df
	df = pd.DataFrame(columns=['t'], data=days)

	# Random levels at diagnosis, distributions from CLOBNET paper
	initial_hb = int(max(100, rng.normal(121, 15)))
	initial_platelets = int(max(50, rng.normal(376, 131)))

	# Random imaginary tumor burden at diagnosis. 100 kills.
	burden = rng.integers(low=40, high=70)

	# Add burden and other columns to data frame
	df['burden'] = df.apply(lambda row: growth(burden, row['t']), axis = 1)
	df['therapy'] = np.nan
	df['event'] = np.nan

	day_after_last_round = 0

	for outcome_count in range(1, 5):

		# Treatment strategy
		outcome = drawOutcome(rng, outcome_count)

		# Time point for start of primary therapy
		start_day = rng.integers(low=2, high=10) + day_after_last_round

		# Progression events:
		if outcome_count > 1 and outcome_count < 7:
			progression_events = ['primary_progression', '2nd_progression', '3rd_progression', '4th_progression', '5th_progression']
			df.loc[df['t'] == start_day - rng.integers(low=4, high=15), 'event'] = progression_events[outcome_count-2]

		# Therapy duration
		therapy_duration = 21 * rng.integers(low=1, high=5)

		# Therapy name
		therapy_name = rng.choice(therapies)
		
		if verbose:
			print(f'Outcome #{outcome_count}')
			print('Selected', therapy_name)

		# Add therapy to the df
		df.loc[(df['t'] >= start_day) & (df['t'] < start_day + therapy_duration), 'therapy'] = therapy_name

		# Add some ids
		df['therapy_id'] = getTherapyCycleId(rng, patient_id, outcome_count)
		df['doseId'] = str(df['therapy_id'])+str(outcome)

		# Time point for primary therapy outcome check
		outcome_day = start_day + rng.integers(low=40, high=60)

		burden_after_therapy = (
			relative_burden[outcome][0] + 
			rng.random() * (relative_burden[outcome][1] - relative_burden[outcome][0])
			) / 100

		# If burden > 100, the disease is simulated as primary resistant
		if burden_after_therapy < 100:

			absolute_burden_before_therapy = float(df.loc[df['t'] == start_day, 'burden'])
			absolute_burden_after_therapy = float(absolute_burden_before_therapy * burden_after_therapy)
			linearGrowth(rng, df, start_day, outcome_day, absolute_burden_before_therapy, absolute_burden_after_therapy)


			# Add some time for stable time before next progression
			if outcome == 'CR':
				stable_time = rng.integers(low=90, high=120)
			elif outcome == 'PR':
				stable_time = rng.integers(low=50, high=120)
			else:
				stable_time = rng.integers(low=0, high=50)
				
			linearGrowth(rng, df, outcome_day, outcome_day+stable_time, absolute_burden_after_therapy, absolute_burden_after_therapy*1.1)
			
			day_after_last_round += stable_time

		day_after_last_round += outcome_day

	# Delete df rows after burden gets over 100:
	death = min(df.loc[df['burden'] >= 100].index.tolist())
	df.drop(df[df['t'] > death].index, inplace = True)
	df.loc[df['t'] == death, 'event'] = 'death'

	# Add some CA-125 values for every nth day
	df['ca125'] = df.apply(lambda row: getCa125(rng, row['burden'], row['t'], 15), axis = 1)

	# Interpolate rest to get more smoothed curve
	df['ca125'].interpolate(method='spline', order=2, inplace=True)

	# Min to zero
	df['ca125'] =  df.apply(lambda row: max(row['ca125'], 0), axis=1)

	# Add some hb and platelet values similarly
	df['hb'] = df.apply(lambda row: getHb(rng, initial_hb, row['burden'], row['therapy'], row['t'], 5), axis = 1)
	df['hb'].interpolate(method='spline', order=2, inplace=True)
	df['platelets'] = df.apply(lambda row: getPlatelets(rng, initial_platelets, row['burden'], row['therapy'], row['t'], 5), axis = 1)
	df['platelets'].interpolate(method='spline', order=2, inplace=True)

	df['patient_id'] = patient_id
	df['cohort_code'] = cohort_code

	# Create some plasma sampling
	df['plasma_sampling'] = False
	plasma_sample_count = rng.integers(5, 25)
	plasma_idx = df.sample(n=plasma_sample_count).index.tolist()
	df.loc[plasma_idx, 'plasma_sampling'] = True
	
	# Take some ctDNA with plasma samples
	df['ctdna'] = False
	ctdna_frac = rng.random() * 0.5
	ctdna_idx = df.loc[df['plasma_sampling']].sample(frac=ctdna_frac).index.tolist()
	df.loc[ctdna_idx, 'ctdna'] = True

	# Add some lab ids to plasma samples
	df['lab_id'] = np.nan
	df.loc[df['plasma_sampling'], 'lab_id'] = df.apply(lambda x: getLabId(rng), axis=1)

	# Insert some radiology events
	df['radiology'] = np.nan
	c = rng.integers(5, 15)
	plasma_idx = df.sample(n=c).index.tolist()
	df.loc[plasma_idx, 'radiology'] = df.apply(lambda x: getRadiologyEvent(rng), axis=1)	

	# Day of diagnosis, always t=0
	df.loc[df['t'] == 0, 'event'] = 'diagnosis'

	# PDS or NACT
	treatment_strategy = rng.choice(['PDS', 'NACT'], p=[0.466, 1-0.466])
	time_to_ids = 0
	if treatment_strategy == 'PDS':
		df.loc[df['t'] == 0, 'event'] = 'diagnosis+PDS'
		time_to_ids = 60
	else:
		df.loc[df['t'] == rng.integers(low=20, high=50) + time_to_ids, 'event'] = 'oper2ids'

	# Add some random operations
	for i in range(1, rng.integers(2, 5)):
		empty_days = df.loc[df['event'].isna(), 't'].tolist()
		t = rng.choice(empty_days)
		df.loc[df['t'] == t, 'event'] = 'operation'

	return df, rng

def getOutputDf(patient_df, rng):
	''' Produces downsampled rows for CSV'''

	output_df = pd.DataFrame(columns=output_columns)

	# Clinical events
	df = patient_df.loc[patient_df['event'].notna(), ['event', 't', 'patient_id', 'cohort_code']].copy()
	df.rename(columns={'t': 'date_relative'}, inplace=True)
	df['interval'] = False
	df['aux_id'] = None
	df['ongoing'] = False
	df['source_system'] = 'Spoofer EHR'

	output_df = output_df.append(df)

	# Add oper1 to same date as diagnosis, if necessary
	if df.loc[df['date_relative'] == 0, 'event'][0] == 'diagnosis+PDS':
		output_df.loc[output_df['event'] == 'diagnosis+PDS', 'event'] = 'diagnosis'
		df2 = output_df.loc[output_df['event'] == 'diagnosis'].copy()
		df2['event'] = 'oper1'

		output_df = output_df.append(df2)

	# Hb, Platelet and CA125 levels
	for labtest in ['hb', 'platelets', 'ca125']:

		df = patient_df.loc[patient_df[labtest].notna(), [labtest, 't', 'patient_id', 'cohort_code']].copy()
		df['source_system'] = 'Spoofer'
		df['interval'] = False
		df['event'] = 'laboratory'
		df['name'] = labtest
		df['aux_id'] = None
		df['interval_end_relative'] = None
		df['ongoing'] = False
		df.rename(columns={labtest: 'result', 't': 'date_relative'}, inplace=True)

		output_df = output_df.append(df)

	if filter_lab:
		# Randomly destroy most of the Hb and platelet rows to simulate real-life blood sampling
		output_df.reset_index(inplace=True)
		drop_fraction = 0.99
		dates = patient_df.sample(frac=drop_fraction)
		date_array = np.array(dates['t'])

		# Add a couple of intervals with daily sampling (e.g. hospital stays)
		for d in range(0, rng.integers(low=5, high=10)):
			duration = rng.integers(low=5, high=15)
			start = rng.choice(date_array)
			end = start + duration 
			before_array = date_array < start
			after_array = date_array > end
			date_array = date_array[before_array | after_array]

		drop_idxs = output_df[(output_df['date_relative'].isin(date_array) & (output_df['name'].isin(['hb', 'platelets'])))].index
		output_df.drop(drop_idxs, inplace=True)

		# Remove from ca125 values also, keep stuff mostly around detected progressions

		# Select dates of progressions
		progression_dates = patient_df.loc[patient_df['event'].isin(['primary_progression', '2nd_progression', '3rd_progression', '4th_progression', '5th_progression']), 't'].tolist()
		all_dates = np.array(dates['t'])
		filter_array = all_dates > 0
		for progression_date in progression_dates:

			# Select interval around progression date
			start = progression_date - rng.integers(low=5, high=25)
			end = progression_date + rng.integers(low=25, high=50)
			before_array = all_dates < start
			after_array = all_dates > end
			filter_array = filter_array & (before_array | after_array)

		all_dates = all_dates[filter_array]
		drop_idxs = output_df[(output_df['date_relative'].isin(all_dates) & (output_df['name'].isin(['ca125'])))].index
		output_df.drop(drop_idxs, inplace=True)

		# From the ca125, drop still some to reduce the sampling frequency
		drop_fraction = 0.6
		dates = output_df.loc[output_df['name'] == 'ca125'].sample(frac=drop_fraction)
		drop_idxs = dates['date_relative'].index
		output_df.drop(drop_idxs, inplace=True)

	# Chemotherapies
	df = patient_df.loc[patient_df['therapy'].notna(), ['therapy', 't', 'patient_id', 'cohort_code', 'therapy_id']].copy()
	df.rename(columns={'t': 'date_relative', 'therapy_id': 'aux_id', 'therapy': 'name'}, inplace=True)
	df['source_system'] = 'Spoofer'
	df['interval'] = True
	df['event'] = 'chemotherapy_cycle'
	df['interval_length'] = 7
	df['interval_end_relative'] = df['date_relative'] + 7	
	output_df = output_df.append(df)	

	# Plasma sampling
	for sampling in [('plasma_sampling', 'tykslab_plasma'), ('ctdna', 'ctdna_sample')]:
		df = patient_df.loc[patient_df[sampling[0]], ['lab_id', 't', 'patient_id', 'cohort_code']].copy()
		df['source_system'] = 'Spooflab'
		df['interval'] = False
		df['event'] = sampling[1]
		df.rename(columns={'lab_id': 'aux_id', 't': 'date_relative'}, inplace=True)

		output_df = output_df.append(df)
		
	# Radiology
	df = patient_df.loc[patient_df['radiology'].notna(), ['radiology', 't', 'patient_id', 'cohort_code']].copy()
	df['source_system'] = 'SpoofCT'
	df['interval'] = False
	df['event'] = 'radiology'
	df.rename(columns={'t': 'date_relative', 'radiology': 'name'}, inplace=True)
	
	output_df = output_df.append(df)
	
	return output_df

def createPlot(df, figure_type, patient_id, verbose=True):
 
   # Fix some chemo names
   df.loc[df['event'].isin(['chemotherapy_cycle', 'chemotherapy_dose']), 'name'] = df.apply(lambda x: fixChemoName(x['name']), axis=1)

   configs = configDicts[figure_type]

   # number of sublots, lab label array
   n_subplots, current_subplot, labs  = 0, 0, []
   for key in configs:
      if configs[key]['plot']:
         n_subplots += 1
      if 'lab' in configs[key] and configs[key]['lab']:
         labs.append(key)

   # Remove chemo plot if no chemotherapy exists
   chemos_exist = True
   if len(df.loc[(df['event'].isin(['chemotherapy_dose', 'chemotherapy_cycle', 'parpi_treatment'])) & (df['patient_id'] == patient_id)]) == 0:
      chemos_exist = False
      n_subplots = n_subplots - 1

   # Create the main plot
   fig = Figure(figsize=[12, 6])
   axs = fig.subplots(n_subplots)

   # Plot clinical events to various tracks
   if configs['track_events']['plot']:

      # Construct the tracks
      tracks, track_colors, track_names, track_ticks = [], [], [], []
      track_padding = 0
      for pos, event in enumerate(configs['track_events']['tracks']):
         if configs['track_events']['tracks'][event]['plot']:
            tracks.append(event)
            track_names.append(configs['track_events']['tracks'][event]['name'])
            track_colors.append(configs['track_events']['tracks'][event]['color'])
            track_ticks.append(pos + configs['track_events']['y_offset'] + track_padding)
            track_padding += configs['track_events']['tracks'][event]['padding_top']

      # Set plot borders and Y ticks and Y range
      axs[current_subplot].set_yticks(track_ticks)
      axs[current_subplot].set_yticklabels(track_names)

      # Legend items
      legend_markers, legend_colors, legend_labels = [], [], []
      
      track_padding = 0
      for i, track in enumerate(tracks):

         current_track = configs['track_events']['tracks'][track]

         # Add solid horizontal line for track
         axs[current_subplot].axhline(y=track_padding+i+configs['track_events']['y_offset'], linestyle="--", linewidth=1, color=track_colors[i])

         # Get events to plot to this track
         events = []
         for subset in current_track['events']:
            if current_track['events'][subset]['plot']:
                  if len(df.loc[(df['event'] == subset) & (df['patient_id'] == patient_id)]) > 0:
                     events.append(subset)

                     # Add item to legend, if no exists for the same name (e.g. "sequenced" might be on multiple tracks)
                     if not ('omit_legend' in current_track['events'][subset] and current_track['events'][subset]['omit_legend']):
                        if current_track['events'][subset]['label'] not in legend_labels:
                           legend_markers.append(current_track['events'][subset]['marker'])
                           legend_colors.append(current_track['events'][subset]['color'])
                           legend_labels.append(current_track['events'][subset]['label'])

         # Columns to be selected from the data frame. At least relative date, possibly also labels
         columns  = ['date_relative']
         if current_track['label_column']:
            columns.append(current_track['label_column'])

         for event in events:

            # Select data
            event_data = df.loc[(df['event'] == event) & (df['patient_id'] == patient_id), columns]
            if len(event_data) > 0:
               color = current_track['events'][event]['color']
               marker = current_track['events'][event]['marker']
               annotation = current_track['label_column']

               # Plot the single timepoints to their track
               last_x_coordinate = -1000
               for e_index, e in event_data.iterrows():
                  date_position = e['date_relative']
                  y_position = track_padding+i+configs['track_events']['y_offset']

                  axs[current_subplot].scatter(
                     date_position,
                     y_position,
                     color=color,
                     marker=marker,
                     s=72,
                     zorder=99)

                  # Draw a vertical line over whole plot for some timepoints like progressions, end of primary therapy
                  if 'vline' in current_track['events'][event] and current_track['events'][event]['vline']:
                     for ax in axs:
                        ax.axvline(e['date_relative'], color='#999', linestyle='dashdot', zorder=-1)

                  if annotation is not False:

                     # Uppercase and handle nans
                     annotation_text = str(e[annotation]).upper()
                     if annotation_text == 'NAN': 
                        annotation_text = ""

                     # Get coordinates for annotation
                     x_offset = current_track['label_placement']['x_offset']
                     y_offset = current_track['label_placement']['y_offset']
                     rotation = current_track['label_placement']['rotation']
                     x_coordinate = e['date_relative']+x_offset

                     # (try to) handle overlapping annotations
                     if x_coordinate - last_x_coordinate < 5:
                        y_offset_label = 0.7
                     else:
                        y_offset_label = 0.0
                     last_x_coordinate = x_coordinate

                     y_coordinate = i+configs['track_events']['y_offset']+y_offset+track_padding+y_offset_label

                     axs[current_subplot].annotate(
                        annotation_text,
                        (x_coordinate, y_coordinate),
                        rotation=rotation,
                        fontsize=7
                        )

         track_padding += current_track['padding_top']

      # Add padding under the lowest and over the highest tracks
      axs[current_subplot].set_ylim([-1, len(tracks)+track_padding+2])

      # Construct the legend for the tracks
      handles = []
      legend_config = configs['track_events']['legend']
      for m, c, l in zip(legend_markers, legend_colors, legend_labels):
         patch = mlines.Line2D([], [], color=c, label=l, marker=m, linewidth=0)  
         handles.append(patch)

      axs[current_subplot].legend(framealpha=legend_config['framealpha'], handles=handles, loc=legend_config['loc'], mode=legend_config['mode'], ncol=math.ceil(len(handles)/2))

      current_subplot += 1

   # Plot chemotherapy GANTT: cycle subset from time series data, sorted
   chemo_configs = configs['chemotherapy']
   if chemo_configs['plot'] and chemos_exist:
      
      # In order to represent single chemo doses from e.g. manually imported data, collapse them together with chemo cycles with narrow interval length
      df.loc[(df['event'] == 'chemotherapy_dose') & (df['patient_id'] == patient_id), 'interval_length'] = 2
      df.loc[(df['event'] == 'chemotherapy_dose') & (df['patient_id'] == patient_id), 'event'] = 'chemotherapy'
      df.loc[(df['event'] == 'chemotherapy_cycle') & (df['patient_id'] == patient_id), 'event'] = 'chemotherapy'

      chemo_track = 0
      for chemo_event in ['parpi_treatment', 'chemotherapy']:
         chemos = df.loc[(df['event'] == chemo_event) & (df['patient_id'] == patient_id)].copy()

         # Order per line to decide the chemo track
         chemos['order'] = 0

         # If no interval is calculated for parpis beforehand but end is defined, calculate it
         chemos.loc[(chemos['event'] == 'parpi_treatment') & (chemos['interval_end_relative'] > 0) & (chemos['interval_length'].isna()), 'interval_length'] = chemos['interval_end_relative'] -  chemos['date_relative']

         # If wanted, blow chemos like 'carboplatin, paclitaxel' to own rows containing only single substance.
         # Makes for better readability if multiple different combinations exist
         target_column = 'name'
         
         if chemo_configs['explode_chemos'] and len(chemos) > 0:
            chemos['single_name'] = chemos.apply(lambda x: x['name'].split(', '), axis=1)
            chemos = chemos.explode('single_name')
            target_column = 'single_name'

         # Simplify chemotherapy names, for example drop "weekly" and "s.c." attributes
         if chemo_configs['simplify_names'] and len(chemos) > 0:
            chemos[target_column] = chemos.apply(lambda x: simplifyChemo(x[target_column]), axis=1)

         # Get different chemo names ordered by their first occurence
         names = chemos.groupby([target_column])['date_relative'].min().to_frame()
         names.sort_values(by=['date_relative'], inplace=True, ascending=True)
         name_order = names.index.tolist()

         if len(name_order) > 0:

            # Sort chemo data by their occurence
            chemos['order'] = chemos.apply(lambda x: name_order.index(x[target_column]), axis=1)
            chemos.sort_values(by=['order'], inplace=True, ascending=False)

            # Plot chemo
            axs[current_subplot].barh(
               chemos[target_column],
               chemos['interval_length'],
               left=chemos['date_relative'],
               color=chemo_configs['color'],
               height=0.4,
               zorder=3
               )

            # Add horizonal lines for each track
            for i in range(0, len(name_order)):
               axs[current_subplot].axhline(y=i+chemo_track, color='#999', linewidth=1, linestyle="--", zorder=2)
            chemo_track += len(name_order)

         # Annotate if parpis going on after last checkup
         ongoing_parpi = chemos.loc[(chemos['ongoing'] == 't') & (chemos['event'] == 'parpi_treatment'), [target_column, 'interval_end_relative', 'order']]
         if len(ongoing_parpi) == 1:
            axs[current_subplot].annotate(
               "",
               xycoords='data',
               textcoords='data',
               xytext=(ongoing_parpi['interval_end_relative']-10, ongoing_parpi['order']),
               xy=(ongoing_parpi['interval_end_relative'], ongoing_parpi['order']),
               arrowprops=dict(
                  headwidth=20,
                  headlength=20,
                  color='#1b5e44'
                  ), 
               zorder=99)

      # Add last date of primary therapy shading and border:
      primary_therapy = df.loc[(df['event'] == 'last_date_of_primary_therapy') & (df['patient_id'] == patient_id), 'date_relative'].tolist()
      if len(primary_therapy) > 0:
         for ax in axs:
            ax.axvspan(0, primary_therapy[0], alpha=1, color='#cae8d8', linestyle='--', zorder=-1)
            ax.axvline(primary_therapy[0], color='#999', linestyle='dashdot', zorder=-1)

      current_subplot += 1

   # Plot laboratory values
   for lab in labs:
      if configs[lab]['plot']:

         values = df.loc[(df['patient_id'] == patient_id) & (df['name'] == lab), 'result'].copy()

         # Set Y axis
         if 'y_scale' in configs[lab]:
            axs[current_subplot].set_yscale(configs[lab]['y_scale'])

         if 'y_lim' in configs[lab]:
            axs[current_subplot].set_ylim(configs[lab]['y_lim'])

            # To show wether there are datapoints which are not included in the limited Y axis
            if 'hard_cap' in configs[lab] and configs[lab]['hard_cap']:
               values = values.apply(lambda x: min(x, configs[lab]['y_lim'][1]))

         # Add reference levels to lab plots
         if 'normal_level' in configs[lab]:
            for level in configs[lab]['normal_level']:
               axs[current_subplot].axhline(y=level, color='#aaa', linestyle=":", zorder=2)

         timepoints = df.loc[(df['patient_id'] == patient_id) & (df['name'] == lab), 'date_relative']
         axs[current_subplot].plot(timepoints, values, color=configs[lab]['color'], linewidth=2, marker='o')
         axs[current_subplot].set_ylabel(configs[lab]['name'])
         
         current_subplot += 1 

   # Remove X axis labels and bottom borders for every subplot except the lowest one. Remove right border
   for i in range(0, len(axs) - 1):
      axs[i].set_xticks([])
      axs[i].spines['bottom'].set_visible(False)
   
   for i in range(1, len(axs)):
      axs[i].spines['top'].set_visible(False)

   for i in range(0, len(axs)):
      axs[i].spines['right'].set_visible(False)
   # Set X axis label
   axs[-1].set_xlabel('Days from diagnosis')
   for ax in axs:
   
      # extend X limits to view min or max day annotations well
      ax.set_xlim(-30, max(df.loc[df['patient_id'] == patient_id, 'date_relative'])+20)

      # add month shading
      for d in range(0, int(max(df.loc[df['patient_id'] == patient_id, 'date_relative'])), 60):
         ax.axvspan(0+d, 30+d, color='#f0f0f0', zorder=-1)

      # add year borders
      for d in range(0, int(max(df.loc[df['patient_id'] == patient_id, 'date_relative'])), 360):
         ax.axvspan(0+d, 1+d, color='#ccc', zorder=-1)   

   fig.tight_layout()
   fig.subplots_adjust(wspace=0)

   return fig

def createDataSet(start_seed, end_seed, output_file = 'output.csv', verbose=True):

	# Output data frame
	odf = pd.DataFrame(columns=output_columns)

	for x in range(start_seed, end_seed):

		try:
			# Generate a patient
			if verbose:
				print(f'**** Spoofing patient {x} ****')
			df, rng = generatePatient(x)

			# Update data to output data frame
			df2 = getOutputDf(df, rng)

			odf = odf.append(df2, ignore_index=True)

		except:
			print(f'Generator failed for random seed {x}')
	
	odf.to_csv(output_file)


def createSinglePatientDataset(seed, verbose=True):

	global output_columns
	seed = int(seed)

	# Output data frame
	odf = pd.DataFrame(columns=output_columns)

	try:
		# Generate a patient
		if verbose:
			print(f'**** Spoofing patient {seed} ****')
		
		df, rng = generatePatient(seed)

		# Update data to output data frame
		df2 = getOutputDf(df, rng)

		odf = odf.append(df2, ignore_index=True)

		return odf, True

	except:
		return False, False

# createDataSet(0, 10, 'output2.csv')