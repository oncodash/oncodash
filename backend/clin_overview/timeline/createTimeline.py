import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import math, sys

color_scheme = {
	'orange': '#e88700',
	'dark_orange': '#e35300',
	'light_green': '#50bf86',
	'violet': '#500091',
	'green': '#30a64c',
	'dark_red': '#a32e00',
}

configs = {
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
}

# Fix chemotherapy naming, if not already fixed
def fixChemoName(s):

	s = s.lower()
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

def createTimeline(df, patient_id, filetype=None, output_folder=None, verbose=True):
		
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
	fig, axs = plt.subplots(n_subplots, figsize=(16,3*n_subplots))

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

	if verbose: print(patient_id)
	
	plt.tight_layout()
	plt.subplots_adjust(wspace=0)

	# Save or show the plot
	if filetype is not None and output_folder is not None:
		plt.savefig(f'{output_folder}/{patient_id}.{filetype}')
	
	else:
		plt.show()
	
	plt.close()

# Load the timeline file
data_file = 'output.csv'
output_folder = '../output'
df = pd.read_csv(data_file)

# Filter out data before the diagnosis - 20 days and sort by patients and dates, handle nans
df = df.loc[df['date_relative'] >= -20]
df.sort_values(by=['patient_id', 'date_relative'], inplace=True, ascending=True)
df['name']=df['name'].fillna("")

# Fix some chemo names
df.loc[df['event'].isin(['chemotherapy_cycle', 'chemotherapy_dose']), 'name'] = df.apply(lambda x: fixChemoName(x['name']), axis=1)

# Make timelines

#to loop all the patients
patients = df['patient_id'].unique()
for patient in patients:
	createTimeline(df, patient, 'png', 'timelines/')