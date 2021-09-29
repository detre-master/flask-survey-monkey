# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 17:21:50 2021

@author: Detre
"""
import pandas as pd
import re
import os
from collections import Counter




def download_clean_survey():
    pass


def survey_monkey_analysis(dirname,f):
    """
       Function used to clean a given survey produced from Survey Monkey
    """
    so = pd.read_excel(os.path.join(dirname.replace("\\routes",''),'temp',f), header=[0,1])    

    # Get the questions and associated options
    qo_df = so.columns.to_frame(index=0, name=["question",'options'])
    
    # Find all columns with no associated option (i.e Unnamed...)
    # Replace all 'Unnamed' column names with level 0 names
    unnamed_df = qo_df[qo_df["options"].str.contains("Unnamed:")]
    
    unnamed_dict = {}
    for row in unnamed_df.values:
        unnamed_dict[row[1]] = row[0]
    
    # Function to rename all 'Unnamed..' columns to level 0 name
    def rename_unnamed(x):
        if x in unnamed_dict.keys():
            return re.sub(x,unnamed_dict[x],x)
        else:
            return x
        
    # Rename the columns
    so = so.rename(columns=lambda x: rename_unnamed(x))
    
    # Update the questions and associated options
    qo_df = so.columns.to_frame(index=0, name=["question",'options'])
    
    
    # All ID related columns
    id_vars = list(unnamed_df["question"])
    qo_df
    
    # Construct id_vars df
    id_vars_df = so[id_vars][id_vars[0]]
    
    for idx, col in enumerate(id_vars):
        if idx != 0:
            id_vars_df = id_vars_df.join(so[id_vars][col])
    
    
    # All questions
    all_questions = list(qo_df[~qo_df["question"].isin(id_vars)]["question"])
    all_questions = list(Counter(all_questions).keys())
    
    # Created the holder for all the data
    # Use the first question in `all_questions`
    
    # Append question to id_vars to select the subset dataframe
    id_vars.append(all_questions[0])
    
    #  DF for given question
    question_resp_df = so[id_vars][all_questions[0]]
    
    # Join the id_vars_df and the question_resp_df 
    question_df = id_vars_df.join(question_resp_df)
    
    # Remove the question that was used to select the subset df
    id_vars.pop()
    
    # Melt (unpivot)
    final_melted_df = pd.melt(question_df, id_vars=id_vars, var_name="Response",value_name="Answer")
    
    # Add the question Column
    final_melted_df["Question"] = all_questions[0]
    
    
    
    
    # Loop over all the questions
    for idx, question in enumerate(all_questions):
        if idx != 0:
            # Append question to id_vars to select the subset dataframe
            id_vars.append(question)
            
            #  DF for given question
            question_resp_df = so[id_vars][question]
            
            # Join the id_vars_df and the question_resp_df 
            question_df = id_vars_df.join(question_resp_df)
            
            # Remove the question that was used to select the subset df
            id_vars.pop()
            
            # Melt (unpivot)
            melted_df = pd.melt(question_df, id_vars=id_vars, var_name="Response",value_name="Answer")
            
            # Add the question Column
            melted_df["Question"] = question
            
            
            # Append the question data to holder
            final_melted_df = final_melted_df.append(melted_df, ignore_index=True)
    
    
    # No. of respondents per question
    respondents_ = final_melted_df[final_melted_df["Answer"].notna()]
    no_respondents_df = respondents_.groupby("Question")["Respondent ID"].nunique().reset_index()
    no_respondents_df = no_respondents_df.rename(columns = {"Respondent ID":"No. of Responsses"})
    
    # No of respondents that gave same answer to a question
    same_answer_df = final_melted_df.groupby(["Question","Response","Answer"])["Respondent ID"].nunique().reset_index()
    same_answer_df = same_answer_df.rename(columns={"Respondent ID":"No. of same answers"})
    #same_answer_df["No. of same answers"].fillna(0,inplace=True)
    
    # Final merge of No. of respondents and 
    merge_1 = pd.merge(left=final_melted_df,right=no_respondents_df,how="left",left_on="Question",right_on="Question")
    merge_2 = pd.merge(left=merge_1, right=same_answer_df,how="left", left_on=["Question","Response","Answer"],
             right_on=["Question","Response","Answer"])
    
    merge_2["No. of same answers"].fillna(0,inplace=True)

    return merge_2


    