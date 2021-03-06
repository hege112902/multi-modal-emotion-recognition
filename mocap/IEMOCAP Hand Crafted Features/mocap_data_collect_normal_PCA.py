import numpy as np
from sklearn.decomposition import PCA, IncrementalPCA

from features import *
from helper import *


batch_size = 64
nb_feat = 34
nb_class = 4
nb_epoch = 80

optimizer = 'Adadelta'


code_path = os.path.dirname(os.path.realpath(os.getcwd()))
emotions_used = np.array(['ang', 'exc', 'neu', 'sad'])
data_path = code_path + "/../data/sessions/"
sessions = ['Session1', 'Session2']
# sessions = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']
framerate = 16000

def get_mocap_rot(path_to_mocap_rot, filename, start,end):
    f = open(path_to_mocap_rot + filename, 'r').read()
    f = np.array(f.split('\n'))
    mocap_rot = []
    mocap_rot_avg = []
    f = f[2:]
    counter = 0
    for data in f:
        counter+=1
        data2 = data.split(' ')
        if(len(data2)<2):
            continue
        if(float(data2[1])>start and float(data2[1])<end):
            mocap_rot_avg.append(np.array(data2[2:]).astype(np.float))
        if(float(data2[1])>end):
            break      
    mocap_rot_avg = np.array_split(np.array(mocap_rot_avg), 200)
    for spl in mocap_rot_avg:
        mocap_rot.append(np.mean(spl, axis=0))
    return np.array(mocap_rot)


def read_iemocap_mocap():
    data = []
    ids = {}
    for session in sessions:
        path_to_wav = data_path + session + '/dialog/wav/'
        path_to_emotions = data_path + session + '/dialog/EmoEvaluation/'
        
        path_to_mocap_rot = data_path + session + '/dialog/pca/MOCAP_rotated/'

        files2 = os.listdir(path_to_wav)

        files = []
        for f in files2:
            if f.endswith(".wav"):
                if f[0] == '.':
                    files.append(f[2:-4])
                else:
                    files.append(f[:-4])
                    

        for f in files:       
            print(f)
            mocap_f = f
            if (f== 'Ses05M_script01_1b'):
                mocap_f = 'Ses05M_script01_1' 
            
            emotions = get_emotions(path_to_emotions, f + '.txt')

            for ie, e in enumerate(emotions):
                '''if 'F' in e['id']:
                    e['signal'] = sample[ie]['left']
                else:
                    e['signal'] = sample[ie]['right']'''
                
                e['mocap_rot'] = get_mocap_rot(path_to_mocap_rot, mocap_f + '.txt', e['start'], e['end'])
                if e['emotion'] in emotions_used:
                    if e['id'] not in ids:
                        data.append(e)
                        ids[e['id']] = 1

                        
    sort_key = get_field(data, "id")
    return np.array(data)[np.argsort(sort_key)]
   
data = read_iemocap_mocap()

import pickle
with open(data_path + '/../'+'data_collected.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

