# This spoofer simulates patients with some growth model, medicates them and simulates also lab values.
# The simulation time series are then down-sampled to represent more real-life data.
# Ascites, end of primary therapy and fresh tissue timepoints are still missing.

import numpy as np
import pandas as pd

verbose = True
filter_lab = True

# Burden decrease per outcome, imaginary
relative_burden = {
	'CR': [0, 30],
	'PR': [30, 50],
	'PD': [50, 110]
}

# Therapy names
therapies = ['Carboplatin', 'Carboplatin, paclitaxel', 'Cisplatin', 'Carboplatin, paclitaxel, bevacizumab', 'Paclitaxel', 'Gemsitabin']

# Columns based on ONCOSYS timeline format, see readme for further documentation
output_columns = ['id', 'patient_id', 'cohort_code', 'interval', 'ongoing', 'date', 'date_relative', 'interval_end', 'interval_end_relative', 'interval_length', 'event', 'name', 'result', 'aux_id', 'source_system']

output_file = 'output.csv'

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

# Output data frame
odf = pd.DataFrame(columns=output_columns)

for x in range(69, 96):

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