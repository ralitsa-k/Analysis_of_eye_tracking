

% Read data with info on choice 
behav_table_conds = readtable(['Y:/DATA/derivatives/behav/full_data_all_trials.csv']);
eye_dir = 'Y:\DATA\derivatives\eyetracking\';

% from behavioural data get IDs
used_ids = unique(behav_table_conds.ID);

% Get names of gaze data files to extract present IDs
files = dir('Y:\DATA\derivatives\eyetracking\*.mat');
for i = 1:length(files)
    sjs_eye_present(i) = extractBetween(files(i).name,"_",".");
end
% intersect IDs in gaze and behav data
ids_both = intersect(used_ids,sjs_eye_present);

% Load gaze data 
for i = 1:length(ids_both)
   % df_eyes(i) = load([eye_dir,'gazedata_',ids_both{i},'.mat']);
    df_eyes(i).IDs = ids_both{i};
end
header = readtable([eye_dir,'stamptime_',ids_both{1},'.csv']);
df_eyes.IDs = cell2mat([ids_both]);
save([eye_dir,'all_eyedata.mat'], 'df_eyes','-v7.3')

