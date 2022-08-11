from flask import Flask, send_file, Response
from spoofer import *
import base64
from io import BytesIO

app = Flask(__name__)

# Load & sort the timeline file
data_file = 'output2.csv'
clinical_df = pd.read_csv(data_file)
clinical_df = clinical_df.loc[(clinical_df['date_relative'] >= -20)]
clinical_df.sort_values(by=['patient_id', 'date_relative'], inplace=True, ascending=True)
clinical_df['name']=clinical_df['name'].fillna("")

# Either load the data from loaded dataset or generate it dynamically
def getPatientData(patient_id):

   patient_id = int(patient_id)
   global clinical_df
   df = clinical_df.loc[(clinical_df['patient_id'] == int(patient_id))]
   success = True
   # Fallback if patient_id not found
   if len(df) == 0:
      df, success = createSinglePatientDataset(patient_id)

   return df, success   

# Get all the data as JSON
@app.route('/patient/<patient_id>/data')
def returnData(patient_id):
   
   df, success = getPatientData(patient_id)   
   if success == False:
      return ('Failure')

   # Return the data as JSON
   return Response(df.to_json(orient='records'), mimetype='application/json')

# Get only certain event type (laboratory, chemotherapy etc, check readme.md)
@app.route('/patient/<patient_id>/data/<data_type>')
def returnSpecifiData(patient_id, data_type):

   df, success = getPatientData(patient_id)   
   if success == False:
      return ('Failure')

   df = df.loc[(clinical_df['event'] == data_type) & (df['patient_id'] == int(patient_id))]

   return Response(df.to_json(orient='records'), mimetype='application/json')

# Get timeline data plots
@app.route('/patient/<patient_id>/plot/<figure_type>')
def createTimeline(patient_id, figure_type, verbose=True):

   df, success = getPatientData(patient_id)   
   if success == False:
      return ('Failure')

   # Fetch the matplotlib figure object
   fig = createPlot(df, figure_type, int(patient_id))

   # Save to buffer
   buf = BytesIO()
   fig.savefig(buf, format="svg")

   # return the buffered svg as base64-sourced img tag
   data = base64.b64encode(buf.getbuffer()).decode("ascii")
   return f"<img src='data:image/svg+xml;base64,{data}'>"

if __name__ == '__main__':
   app.run()