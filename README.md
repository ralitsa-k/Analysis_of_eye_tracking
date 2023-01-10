# Analysis_of_eye_tracking
Analysing eye tracking data for a Bandit task.

The bandit task is explained in my repository (Shiny-app-results) where some of the behavioural results are presented as well. 

This python code deals with gathering and combining the data set from Tobii eye-tracker which uses 'titta' toolbox to record data. 

My python code:
- reads in the data with the appropriate data, assigning headers
- combines the data with triggers (that mark the start and end of each trial)
- removes trial where data was not recorded
- plots the distribution of gaze data 
- removes outlier trials by getting both X and Y coordinate systems, z-scoring the data and removing everything above 3 SDs
- counts the number of trials and reports how many had missing data 

- Extracts the data that is the gaze during a stimulus was on the screen or
- Extracts the data which is the first gaze, right after a stimulus was chosen 

- Plots a scatterplot representing the location the participant looked at after selecting a stimulus 


My R code: 
- proceeds to get statistics about 'preference' from gaze data 
- if a participant looked more at a stimulus until half-time within a trial, maybe it was preferred more (ref. tbc)
- on each trial an 'eye-choice' is constructed which is is 0 or 1 for a stimulus being chosen (by average gaze times) 
