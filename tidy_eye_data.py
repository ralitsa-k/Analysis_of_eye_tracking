# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 13:13:05 2022

@author: ralitsaa
"""
import csv
from scipy.stats import zscore
import pickle
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

header = ['device_time_stamp',
         'system_time_stamp',
         'left_gaze_point_on_display_area_x',
         'left_gaze_point_on_display_area_y',
         'left_gaze_point_in_user_coordinate_system_x',
         'left_gaze_point_in_user_coordinate_system_y',
         'left_gaze_point_in_user_coordinate_system_z',
         'left_gaze_origin_in_trackbox_coordinate_system_x',
         'left_gaze_origin_in_trackbox_coordinate_system_y',
         'left_gaze_origin_in_trackbox_coordinate_system_z',
         'left_gaze_origin_in_user_coordinate_system_x',
         'left_gaze_origin_in_user_coordinate_system_y',
         'left_gaze_origin_in_user_coordinate_system_z',
         'left_pupil_diameter',
         'left_pupil_validity',
         'left_gaze_origin_validity',
         'left_gaze_point_validity',
         'right_gaze_point_on_display_area_x',
         'right_gaze_point_on_display_area_y',
         'right_gaze_point_in_user_coordinate_system_x',
         'right_gaze_point_in_user_coordinate_system_y',
         'right_gaze_point_in_user_coordinate_system_z',
         'right_gaze_origin_in_trackbox_coordinate_system_x',
         'right_gaze_origin_in_trackbox_coordinate_system_y',
         'right_gaze_origin_in_trackbox_coordinate_system_z',
         'right_gaze_origin_in_user_coordinate_system_x',
         'right_gaze_origin_in_user_coordinate_system_y',
         'right_gaze_origin_in_user_coordinate_system_z',
         'right_pupil_diameter',
         'right_pupil_validity',
         'right_gaze_origin_validity',
         'right_gaze_point_validity']

DF_list= list()
DF_stamps = list()
# Define the paths 
path_data_main='Y:/DATA/sourcedata'
path=path_data_main+'/'
save_path ='Y:/TOOLS/runEYETRACKING/analyse_eyetracking/Analysis_of_eye_tracking/data/'
if not os.path.exists(f'{save_path}/'):
    os.mkdir(f'{save_path}/')
# Read the headers 
timestamp_file = open(f'{save_path}/header_sub-032.csv')
time_reader = csv.reader(timestamp_file)
headers = pd.read_csv(f'{save_path}/header_sub-032.csv',header=None)

full_behav_data = pd.read_csv('Y:/DATA/derivatives/behav/full_data.csv')

path_list = [];
for s in range(3,38): #loop through subjects
    # add zeros to start of each number to get participant IDs
    id_part=str(s).zfill(3);
    print(f'loading subject {id_part}')
    # path for each participant
    path_list.append(f'{path_data_main}/sub-{id_part}/sub-{id_part}_task_socPEIRS_eyetracking.pkl')
        
    curr_behav_data = full_behav_data[full_behav_data.participant == f'sub-{id_part}']

    # load if participant has this data file 
    if os.path.isfile(path_list[s-3]):
        f = open(path_list[s-3], 'rb');
        gaze_data_container = pickle.load(f);
        msg_container = pickle.load(f);

        # make a data frame from the eyetracking data (no triggers) using headers from pickle 
        df = pd.DataFrame(gaze_data_container, columns=header);
        # load the timepoints when the operator-defined triggers were started 
        df1 = pd.DataFrame(msg_container, columns=['times', 'triggers']);
        # create a folder to save the data 


        # select columns of itnerest. Coordinate systems to use later 
        subset_df = df[['system_time_stamp', 'device_time_stamp',          
             'left_gaze_point_in_user_coordinate_system_x', 
             'right_gaze_point_in_user_coordinate_system_x',
             'left_gaze_point_in_user_coordinate_system_y', 
             'right_gaze_point_in_user_coordinate_system_y',
             'left_pupil_diameter']];
    
        # Remove NAs  from eye gaze data
        size_raw = df.shape[0];
        
        # Remove missing data from RightGaze and from LeftGaze
        subset_df2 = subset_df.dropna()
        size_no_nas = subset_df2.shape[0];
        print(str(round(((size_raw-size_no_nas )/ size_raw) * 100)) + '% of data with NAs')
        subset_df = subset_df2;
    
        # Trigger data ---------------------------------------------------------------------------------------------
        # Select only onset and offset triggers (tidy data)
        df_triggers = df1[df1['triggers'].str.contains('onset|offset') == True];
        # eyetracker specific triggers 
        #  
        df_triggers_spl = df_triggers.triggers.str.split(pat = '_', expand=True);
        df_triggers_spl.columns = ['trigger_n','occ'];
        df_triggers = pd.concat([df_triggers, df_triggers_spl], axis=1);
        df_triggers = df_triggers.rename(columns = {'times':'system_time_stamp'})
        
        # Combine triggers data with gaze data 
        # sort in such a way that triggers are in the right position (preceding the trial gazes)
        eye_data = pd.merge(df_triggers, subset_df, how='outer', on='system_time_stamp')
        eye_data = eye_data.sort_values('system_time_stamp')
        
        # Identify gaze data by the appropriate (current) trigger 
        eye_data.trigger_n.fillna(method='ffill', inplace=True)
        eye_data = eye_data.dropna(subset=['trigger_n'])
        
        # Get the index of an onset of a trial only 
        ind_onset = eye_data.occ.str.contains('onset',na=False)
        # Get a variable that gives a unique identifier to each trigger (for later group by and stats)
        i = eye_data.trigger_n    
        eye_data['trigger_indx'] = i.ne(i.shift()).cumsum()
        eye_data = eye_data.astype({'trigger_n':'int'})
        df = eye_data;
        
        # If gaze data has NAs
        #  eye_data[eye_data.columns[[eye_data.columns.str.contains(pat = 'user')]]].fillna(method = 'ffill', inplace = True)
  
        # Select only triggers of stimulus onset 
        stim_gaze = eye_data.loc[eye_data['trigger_n'] <= 85] 
        # some participants have stim trigger 84 (check word document in project folder about triggers)
        stim_gaze = stim_gaze.loc[stim_gaze['trigger_n'] >= 10]
        
        # Index trial_id 540 in total 
        i = stim_gaze.trigger_indx    
        stim_gaze['trial_id'] = i.ne(i.shift()).cumsum()
        
        # Count number of trials
        # Find trials in which Selection screen started (all trials really)
        # solution #2  stim_dat = df_triggers.triggers.str.startswith('2_onset',na=False)
        stim_num = df_triggers.triggers == "2_onset"
        print('Number of trials is ' + str(sum(stim_num)))
        
        print('Number of unique trial_ids is ', stim_gaze.trial_id.nunique())
        
        # Keep only gaze data (trigger identifier is added as a separate column at this stage)
        stim_gaze = stim_gaze.dropna(subset=['device_time_stamp'])
        print('Number of trial_ids that have eye data is ', stim_gaze.trial_id.nunique())

        # ids of trials with existing eye data 
        present_data = pd.DataFrame();
        present_data['trial_id'] = pd.DataFrame(stim_gaze.trial_id.unique())
        present_data.participant = f'sub-{id_part}'
        present_data.to_csv(f'{save_path}/{id_part}_trials_with_present_gazedata_while_stimulus_on.csv')

        
        # Definind the onset of a trial, fill the rows of gaze data with the id of this trial
        stim_gaze.triggers.fillna(method='ffill', inplace=True)
        eye_data = stim_gaze.dropna(subset=['left_gaze_point_in_user_coordinate_system_x'])
  
        # Find only the first gaze when stimulus pair appears
        eye_data['change_indx'] = eye_data.trigger_indx.diff()
        first_look = eye_data[eye_data.trigger_indx.shift() != eye_data.trigger_indx]

    
        # Remove outlier gazes 
        first_look = first_look.assign(xL_zscore = zscore(first_look.left_gaze_point_in_user_coordinate_system_x))
        first_look = first_look.assign(xR_zscore = zscore(first_look.right_gaze_point_in_user_coordinate_system_x))
        first_look = first_look.query('xL_zscore < 2.56 & xR_zscore < 2.56')
        
        first_look = first_look.assign(yL_zscore = zscore(first_look.left_gaze_point_in_user_coordinate_system_y))
        first_look = first_look.assign(yR_zscore = zscore(first_look.right_gaze_point_in_user_coordinate_system_y))
        first_look = first_look.query('yL_zscore < 2.56 & yR_zscore < 2.56')

        first_look.to_csv(f'{save_path}/{id_part}_FirstGaze_stimOn.csv')

        
        # Get average gaze between stim-on and choice
        within_stim = eye_data;
        # Remove outliers from data between stimulus onset and selection 
        within_stim = within_stim.assign(xL_zscore = zscore(within_stim.left_gaze_point_in_user_coordinate_system_x))
        within_stim = within_stim.assign(xR_zscore = zscore(within_stim.right_gaze_point_in_user_coordinate_system_x))
        within_stim = within_stim.query('xL_zscore < 2.56 & xR_zscore < 2.56')
        
        within_stim = within_stim.assign(yL_zscore = zscore(within_stim.left_gaze_point_in_user_coordinate_system_y))
        within_stim = within_stim.assign(yR_zscore = zscore(within_stim.right_gaze_point_in_user_coordinate_system_y))
        within_stim = within_stim.query('yL_zscore < 2.56 & yR_zscore < 2.56')
        
        within_stim_means = within_stim.groupby(['trial_id','trigger_n'])['left_gaze_point_in_user_coordinate_system_x',
                                                            'right_gaze_point_in_user_coordinate_system_x'].mean()

        gaze_for_each_stim = within_stim.groupby(['trigger_n'])['xL_zscore',
                                                            'xR_zscore',
                                                            'yL_zscore',
                                                            'yR_zscore'].mean()
        
        
        
        within_stim.to_csv(f'{save_path}/{id_part}_gaze_within_stim.csv')

        


        # # Plot 
        # xdata = stim_gaze['left_gaze_point_in_user_coordinate_system_x']
        # ydata = stim_gaze['right_gaze_point_in_user_coordinate_system_x']
        # xdata_z = stim_gaze['xL_zscore']
        # ydata_z = stim_gaze['xR_zscore']
    
        # bins = np.linspace(-10, 10, 100)
        
        # plt.hist(xdata, bins, alpha=0.5, label='L_gaze')
        # plt.hist(ydata, bins, alpha=0.5, label='R_gaze')
        # plt.legend(loc='upper right')
        # plt.title('left and right eyes')
        # plt.savefig(f'{save_path}/sub-{id_part}/{id_part}_looked_left_and_right.png')
        # plt.close()
        
        # plt.hist(xdata_z, bins, alpha=0.5, label='L_zscored')
        # plt.hist(ydata_z, bins, alpha=0.5, label='R_zscored')
        # plt.legend(loc='upper right')
        # plt.title('Z scored left and right eyes')
        # plt.savefig(f'{save_path}/sub-{id_part}/{id_part}_eyegaze_checks.png')
        # plt.close()
        
        
        # stim_gaze_41 = stim_gaze.loc[stim_gaze['trigger_n'] == 41] 

        # # Scatterplots of data 
        # x = stim_gaze_41.xL_zscore
        # y = stim_gaze_41.yL_zscore
        # plt.scatter(x, y,c='green')

        # stim_gaze_14 = stim_gaze.loc[stim_gaze['trigger_n'] == 14] 
        # x2 = stim_gaze_14.xL_zscore
        # y2 = stim_gaze_14.yL_zscore
        # plt.scatter(x2, y2,c='red')
        # plt.show()
        
        # plt.hist(x,bins)
        # plt.hist(x2, bins)
        
        
        
        
        # # Check the stimulus looked at during feedback, it should be the one chosen 
        # feed_gaze = df.loc[df['trigger_n'] == 3]
        # i = feed_gaze.trigger_indx    
        # feed_gaze = feed_gaze.assign(trial_id = i.ne(i.shift()).cumsum())   # give it trial_id column
        # feed_next = feed_gaze.shift(-1)
        # feed_onset = feed_next.loc[feed_gaze.triggers == '3_onset'] 
        # choice_d = curr_behav_data.loc[:,('trial_id', 'response')]
        # choices_and_gaze = pd.merge(feed_onset, choice_d, on = 'trial_id')
        # choices_and_gaze = choices_and_gaze.dropna(subset=['left_pupil_diameter'])
        
        # choices_and_gaze = choices_and_gaze.assign(xL_zscore = zscore(choices_and_gaze.left_gaze_point_in_user_coordinate_system_x))
        # choices_and_gaze = choices_and_gaze.assign(xR_zscore = zscore(choices_and_gaze.right_gaze_point_in_user_coordinate_system_x))
        # choices_and_gaze = choices_and_gaze.query('xL_zscore < 2.56 & xR_zscore < 2.56')
        # choices_and_gaze = choices_and_gaze.query('xL_zscore > -2.56 & xR_zscore > -2.56')
        
        # choices_and_gaze = choices_and_gaze.assign(yL_zscore = zscore(choices_and_gaze.left_gaze_point_in_user_coordinate_system_y))
        # choices_and_gaze = choices_and_gaze.assign(yR_zscore = zscore(choices_and_gaze.right_gaze_point_in_user_coordinate_system_y))
        # choices_and_gaze = choices_and_gaze.query('yL_zscore < 2.56 & yR_zscore < 2.56')
        # choices_and_gaze = choices_and_gaze.query('yL_zscore > -2.56 & yR_zscore > -2.56')

        # choices_and_gaze_left = choices_and_gaze.loc[choices_and_gaze['response'] == 0] 

        # # Scatterplots of data 
        # x = choices_and_gaze_left.xL_zscore
        # y = choices_and_gaze_left.yL_zscore
        # plt.scatter(x, y,c='green')
        # choices_and_gaze_right = choices_and_gaze.loc[choices_and_gaze.response == 1] 
        # x2 = choices_and_gaze_right.xL_zscore
        # y2 = choices_and_gaze_right.yL_zscore
        # plt.scatter(x2, y2,c='red')
        # plt.savefig(f'{save_path}/{id_part}_looked_left_and_right_at_feedback.png')
        # plt.cla()
        # bins = np.linspace(-3, 3, 30)
        # plt.hist(x,bins)
        # plt.hist(x2, bins)
        # plt.savefig(f'{save_path}/{id_part}_eyegaze_checks_at_feedback.png')
        # plt.cla()
     
    else:
        continue;
    
    
    # Find gaze right over left on each trial 
    
    
    # trigger_n is the same as trigger integer on each trial - double check 

