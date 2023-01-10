import pickle
import pandas as pd
from pathlib import Path
import scipy.io
import os

for s in range(37,38): #loop through subjects from 301 to 303
    print(s)
    id_part=str(s).zfill(3);

    path_data_main='Y:/DATA/sourcedata'
    save_path ='Y:/TOOLS/runEYETRACKING/analyse_eyetracking/Analysis_of_eye_tracking/data/'

    path=path_data_main+'/'
    print(path)
    #path=path_data_main
    os.chdir(path)
            

    #path = os.path.join(main_data_path, id_part)
    #os.mkdir(path)
    if Path(f'{path_data_main}/sub-{id_part}/sub-{id_part}_task_socPEIRS_eyetracking.pkl').is_file():
        filename=f'{path_data_main}/sub-{id_part}/sub-{id_part}_task_socPEIRS_eyetracking.pkl'
        print(filename)

        datafile=f'//gazedata_sub-{id_part}.mat'
        stampsfile=f'/stamptime_sub-{id_part}.csv'
        headerfile=f'/header_sub-{id_part}.csv'
        datafile2=f'/gazedata_sub-{id_part}.csv'

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

        f = open(filename, 'rb')
        gaze_data_container = pickle.load(f)
        msg_container = pickle.load(f)

        df = pd.DataFrame(gaze_data_container, columns=header)

        #scipy.io.savemat(save_path+datafile,mdict={'gaze_data_container': gaze_data_container})

        df = pd.DataFrame(msg_container)
        df.to_csv(save_path+stampsfile,header=None,index=False)

        df = pd.DataFrame(gaze_data_container)
        df.to_csv(save_path+datafile2,header=None,index=False)

    else:
        continue;
        
headers = pd.DataFrame(header)
headers.to_csv(save_path+headerfile, header=None,index=False)
