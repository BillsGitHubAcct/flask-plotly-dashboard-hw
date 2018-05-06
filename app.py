import datetime
from datetime import date
import numpy as np
import pandas as pd
import os
from flask import Response, Flask, jsonify, render_template
import json




#################################################
# Database Setup
#################################################


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# panda reads from csv files
df_otu = pd.read_csv("belly_button_biodiversity_otu_id.csv")
li_col_names = pd.read_csv("belly_button_biodiversity_samples.csv").columns.tolist()
df_meta = pd.read_csv("Belly_Button_Biodiversity_Metadata.csv")
df_wfreq = df_meta
df_sample = pd.read_csv("belly_button_biodiversity_samples.csv")
		
@app.route('/')
def index():
	"""
	
	"""
	return render_template('index.html')

@app.route("/names")
def sample_names():
	"""
	Return list of sample names.
	"""
	#samples names equate to columns in samples data set
	names = li_col_names[1:len(li_col_names)-1] # skip column "otu_id" at 0th element
	return jsonify(names)
	
	
# @app.route("/otu")
# def otus():
	# """
		# Return a json representation of otu 
	# """
	# otu = df_otu["lowest_taxonomic_unit_found"].tolist()
	
	# return jsonify(otu)
	
@app.route("/metadata/<sample>")
def meta(sample):
	"""
		Return a json representation of meta data from single sample
	"""
	number_part = int(sample.split("_")[1])
	meta_sel = df_meta.loc[df_meta['SAMPLEID'] == number_part]
	
	meta_dict = {
        "AGE": meta_sel['AGE'][0],
        "BBTYPE": meta_sel['BBTYPE'][0],
        "ETHNICITY": meta_sel['ETHNICITY'][0],
        "GENDER": meta_sel['GENDER'][0],
        "LOCATION": meta_sel['LOCATION'][0],
        "SAMPLEID": int(meta_sel['SAMPLEID'][0])
    }
	return jsonify(meta_dict)
	
@app.route("/wfreq/<sample>")
def wfreq(sample):
	"""
		Return a json representation of wash freq from single sample
	"""
	wfreq_sel = df_wfreq.loc[df_wfreq['SAMPLEID'] == int(sample.split("_")[1])]
	wfreq = [int(wfreq_sel['WFREQ'][0])]
	
	return jsonify(wfreq)
	
@app.route('/samples/top10/<sample>')
def sample_t10(sample):
	"""
		Returns JSON data for Pie Chart containing Top Ten samples for `otu_ids`
		and sample values for a sample name...also contains join with otu table
		for getting hover information
	"""
	# selection on column that sample references
	sample_sel = df_sample.loc[df_sample[sample] > 0]
	# merge with otu to get description for hover text
	sample_sel = sample_sel.merge(df_otu, how='left', on='otu_id')
	#print(sample_sel)
	# Sort descending and keep the top ten
	sample_sort = sample_sel.sort_values([sample], ascending=[False]).head(10)
	#print(sample_sort)
	sample_dict = [{'labels': [x for x in sample_sort['otu_id']]
				   ,'values': [x for x in sample_sort[sample]]
				   ,'type': 'pie'
				   # Note the following WORKS in adding the otu desc to the hoverinfo
				   # however it also adds the text to the labels on the chart which is ugly
				   # and I could not figure out how to keep that from happening
				   # therefore it is commented out
				   #,'text': [x for x in sample_sort['lowest_taxonomic_unit_found']]
				   #,'hoverinfo' : 'label + text + values'
				   
				   }]
	#print(sample_dict)
				   
	return jsonify(sample_dict)
	
@app.route('/samples/all/<sample>')
def sample_all(sample):
	"""
		Return JSON data for Scatter Plot containing sorted lists for `otu_ids`
		and `sample_values for a sample type...also contains join with otu table
		for getting hover information
	"""
	# selection on column that sample references
	sample_sel = df_sample.loc[df_sample[sample] > 0]
	# merge with otu to get description for hover text
	sample_sel = sample_sel.merge(df_otu, how='left', on='otu_id')
	#print(sample_sel)
	# Format data and attributes for plotly.js scatter plot call
	sample_dict = [{'x': [x for x in sample_sel['otu_id']]
					,'y': [x for x in sample_sel[sample]]
					,'type': 'scatter'
					,'mode': 'markers'
					,'marker': {'size': [x*.5 for x in sample_sel[sample]]
					,'color': [x for x in sample_sel['otu_id']]}
					,'text': [x for x in sample_sel['lowest_taxonomic_unit_found']]
						   
				   }]
					   
	return jsonify(sample_dict)
	
if __name__ == '__main__':
    app.run(debug=True)

