# -*- coding: utf-8 -*-
"""

@author: Detre Team


"""


import os
import pandas as pd
from flask import Flask, flash ,request, redirect, render_template, session, send_file, url_for
from forms.forms import SurveyMonkeyForm
from utils.survey_monkey import survey_monkey_analysis
from werkzeug.utils import secure_filename



app = Flask(__name__)


app.config["SECRET_KEY"] = 'ThiSiSNotASecureKeY'

dirname = os.path.dirname(__file__)

@app.route("/")
def home():
    form = SurveyMonkeyForm()
    return render_template("survey.html",form=form)


@app.route("/survey", methods=["GET","POST"])
def survey():
    """
    POST : Handle the uploaded Survey Monkey file
    GET  : Upload page for `Survey Monkey` file.
    """
    
    form = SurveyMonkeyForm()
    if request.method == "POST":
        file = request.files['file']
        
        f    = secure_filename(file.filename)
        
        file.save(os.path.join(dirname,'temp',f))
        
        filename_    = os.path.join(dirname,'temp',f) 
        
        try:
            survey_df    = pd.read_excel(filename_, header=[0,1])
        except Exception as e:
             
            
             flash("Could not read given file.",'danger')
             return redirect(url_for("home")), 405
         
        # Check if indeed a survey monkey file
        # Any column `respondent id`
        survey_columns = survey_df.columns.to_frame(index=0, name=["question",'options'])
        
        if sum(survey_columns["question"].str.strip().str.lower() == "respondent id") == 1:
            
            session["name"] = f
            return redirect(url_for("survey_analysis"))
        else:
             
             flash('Not a `Survey Monkey` survey','danger')
             return redirect(url_for("home")), 405
        
    
    return render_template("survey.html",form=form)


@app.route("/survey/analysis", methods=["GET"])
def survey_analysis():
    """
    API that runs the data cleaning on the Survey Monkey entries
    """
   
    if session.get('name'):
       
       # Get the clean survey
       try:
           clean_survey = survey_monkey_analysis(dirname,session["name"]) 
           
           # save the clean survey
           f     = "clean-" + session["name"]
           file_ = os.path.join(dirname,'temp',f)
           clean_survey.to_excel(file_, engine='openpyxl')
           
           session["survey_name"] = f
           return send_file(file_, attachment_filename="Clean Survey Monkey Output.xlsx", as_attachment=True), 200
       
       except Exception as e:
             
             flash("Something went wrong while cleaning your survey.",'danger')
             return redirect(url_for("home")), 500           
       
    else:
       return redirect(url_for("survey")) 
   
    
   
@app.route("/survey/analysis", methods=["GET"])
def download_survey():
    """
    Download the cleaned `Survey Monkey` file
    """
    if session.get("survey_name"):
        try:
            file_ = os.path.join(dirname,'temp',session["survey_name"])
            return send_file(file_, attachment_filename="Clean Survey Monkey Output.xlsx", as_attachment=True), 200
        except:
            flash("Error occurred while downloading the survey.",'danger')
            return redirect(url_for("home")), 500 
    else:
        return redirect(url_for("survey")) 
    
    
    
if __name__ == "__main__":
    app.run(debug=True)