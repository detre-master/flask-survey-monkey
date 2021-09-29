# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 11:08:53 2021

@author: 27608
"""


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired




class SurveyMonkeyForm(FlaskForm):
    """
    Form for Survey Monkey file upload
    """
    
    survey_m =  FileField(validators=[FileRequired()])