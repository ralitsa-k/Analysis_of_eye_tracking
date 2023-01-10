library(tidyverse)
detach(package:plyr)

`%!in%` = Negate(`%in%`)

color1 = "#4d9699"
color2 = '#ff0659'
color3 = '#5f6c11'
# Average looking times within a trial (while the stimulus is on)
# Looked more at more preferred stimulus?  ------

gaze_data = list()
subj_id = vector()
for (i in 3:37){
  if (i < 10){
    subj_id[[i-2]] = paste0('00',i)
  } else {
    subj_id[[i-2]] = paste0('0', i)
  }

  gaze_data[[(i - 2)]] <- read_csv(paste0('Y:/TOOLS/runEYETRACKING/analyse_eyetracking/Analysis_of_eye_tracking/data/',
                                                    subj_id[[i-2]], '_gaze_within_stim.csv')) %>%
    mutate(id = subj_id[[i-2]])
}

big_data1 = do.call(rbind, gaze_data)

a = setdiff(c(1:37), c(11,12,16,20))


big_gaze_data1 <- big_data1 %>%
  filter(xL_zscore > -3,
         xR_zscore > -3,
         yL_zscore > -3,
         yR_zscore > -3) %>%
  filter(id %!in% c('011','012','016','020')) %>%
  group_by(id, trial_id) %>%
  mutate(ngaze = n()) %>%
  mutate(idx_ns = seq(1:ngaze)) %>%   # Remove the second half (time) of each trial 
  filter(idx_ns > floor(ngaze/2))

big_data_gaze <- big_gaze_data1 %>%
  group_by(trigger_n, id) %>%
  summarise(mean_xL = mean(xL_zscore),
            mean_xR = mean(xR_zscore),
            mean_yL = mean(yL_zscore),
            mean_yR = mean(yR_zscore)) 

ggplot(data = big_data_gaze) +
  geom_point(aes(x = mean_xR, y = mean_yR, color = 'right'), size = 3) +
  geom_point(aes(x = mean_xL, y = mean_yL, color = 'left'), size = 3) +
  geom_vline(xintercept = 0) +
  facet_wrap(~factor(trigger_n)) 

big_gaze_data1 %>%
  ggplot(aes(x = xR_zscore)) +
  geom_density() +
  facet_wrap(~id)

names(big_data1)

# Statistics on distance of gaze from middle according to condition 

stim_eye_pref <- big_gaze_data1 %>%
  group_by(id, trigger_indx, trial_id, trigger_n) %>%
  summarise(mean_loc = mean(xR_zscore)) %>%
  mutate(eye_choice = ifelse(mean_loc < 0, '0', '1')) %>%
  separate(trigger_n, into = c('stim1', 'stim2'), -1, remove = FALSE) %>%
  mutate(sub = 'sub-') %>%
  mutate(participant = paste0(sub, id)) %>%
  mutate(stim1 = as.numeric(stim1), stim2 = as.numeric(stim2))
  

# Load behavioural data 

behav_data <- read_csv('Y:/TOOLS/runEYETRACKING/analyse_eyetracking/behav_data_combined.csv') %>%
  mutate(first_observer = ifelse(group_1 == perceptual_result, 'in-group','out-group'),
         second_observer = ifelse(first_observer == 'in-group', 'out-group', 'in-group'),
         block_soc = ifelse(block == 2, first_observer,
                            ifelse(block == 3, second_observer, 'baseline'))) %>%
  select(ID, participant, block_soc, trial_id, left_rew_dbl, right_rew_dbl, trial_n) 

# select(ID, participant, stimuliShown, block, stim1, stim2, response, rt, left_rew_dbl, right_rew_dbl, typeOfChoice,
 #        trial_id, trial_n, risky, correct, riskChosen, highChosen)


behav_and_eye <- behav_data %>%
  right_join(stim_eye_pref) %>%
  select(!contains('latent'))

# If a stimulus was looked at on average longer than the other one, it is considered chosen 
eye_pref_cleaned <- behav_and_eye %>%
  mutate(
   trigger_integer = trigger_n,
    # amount of points won on this trial
    reward = ifelse(eye_choice == 0, left_rew_dbl, right_rew_dbl),
    stim_chosen = as.numeric(ifelse(eye_choice == 0, stim1,
                                    ifelse(eye_choice == 1, stim2,0))),
    stim_unchosen = as.numeric(ifelse(eye_choice == 0, stim2, stim1)),
    # response is 0 (left) or 1 (right)
    response = ifelse(eye_choice == 'None', NA, eye_choice),
    ID = participant,
    forced = rep(0), # just added to mimic PEIRS
    trial_cont = trial_n
  ) %>%
  mutate(typeOfChoice = case_when(grepl("12|21", trigger_integer) ~ 1,
                                  grepl("13|31", trigger_integer) ~ 2,
                                  grepl("14|41", trigger_integer) ~ 3,
                                  grepl("23|32", trigger_integer) ~ 4,
                                  grepl("24|42", trigger_integer) ~ 5,
                                  grepl("34|43", trigger_integer) ~ 6),
         correct1 = ifelse(trigger_integer %in% c('13','31') & stim_chosen == 1, 1,
                           ifelse(trigger_integer %in% c('14','41') & stim_chosen == 1, 1,
                                  ifelse(trigger_integer %in% c('23','32') & stim_chosen == 2, 1,
                                         ifelse(trigger_integer %in% c('24','42') & stim_chosen == 2, 1,0)))),
         highChosen = ifelse(typeOfChoice %in% c(2,3,4,5), correct1, NA),
         risky1 = ifelse(trigger_integer %in% c('12','21') & stim_chosen == 1, 1,
                         ifelse(trigger_integer %in% c('34','43') & stim_chosen == 3, 1, 0)),
         risky = ifelse(typeOfChoice %in% c(1, 6), risky1, NA),
         risky = ifelse(is.na(response), NA, risky),
         riskChosen = risky,
         TrialType_num = ifelse(trigger_integer %in% c(1,6), 2,
                                ifelse(trigger_integer  %in% c(2,3,4,5), 3, 0)),
         win = ifelse(typeOfChoice == 1, 1,
                      ifelse(typeOfChoice == 6, -1, NA)),
         trial = trial_cont,
         choices = ifelse(response == 1,0,1),
         correct = highChosen,
         stimuliShown = trigger_integer) %>%
  mutate(pair_type = ifelse(typeOfChoice == 1, 'both_high',
                            ifelse(typeOfChoice == 6, 'both_low',
                                   'different'))) %>%
  dplyr::select(stimuliShown, stim1, stim2, pair_type,  response, reward, ID, participant, stim_chosen, 
                typeOfChoice, highChosen, riskChosen,
                forced, choices, win, correct, risky, trial, trial_cont, trial_id, block_soc, 
                trial_n, trigger_integer, eye_choice,participant, left_rew_dbl, right_rew_dbl)


# Plot eye Correct --------
perc_correct <- eye_pref_cleaned %>%
  group_by(ID) %>% count(correct) %>% filter(correct != 'NA') %>%
  mutate(sum_all = sum(n)) %>%  filter(correct == 1) %>%
  summarise(perc = (n*100)/sum_all) %>% arrange(perc)

perc_correct$ID = factor(perc_correct$ID, levels = perc_correct$ID)
# get number of correct trials (from two different Expected Values - choose the stim with higher)
# Plot S1
perc_correct %>%
  ggplot(aes(x = ID, y = perc)) +
  geom_bar(stat = 'identity', fill = color1) +
  theme(axis.text.x = element_text(angle = 45)) +
  labs(y = 'Percentage correct') +
  scale_y_continuous(breaks = seq(0,100,10), limits = c(0,100)) +
  geom_text(aes(label=round(perc,1)), vjust=-1, size = 4)

write.csv(perc_correct, 'perc_correct_eyegaze.csv')

data_2b <- eye_pref_cleaned

sjs = length(unique(eye_pref_cleaned$ID))

data_2b %>% 
  filter(block_soc == 'out-group') %>%
  mutate(bins = rep(1:5,each =  36, times = length(sjs))) %>%
  filter(typeOfChoice %in% c(1,6)) %>%
  group_by(pair_type, bins,participant) %>%
  mutate(c_bins = n())



