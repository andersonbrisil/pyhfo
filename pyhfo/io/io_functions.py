# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:12:23 2015

@author: anderson
"""

import h5py
import numpy as np
import RHD
import scipy.io as sio

def make_dict(data,sample_rate,n_channel,ch_labels,time_vec,bad_channels):
    ''' 
    Make a dictionary 
    data: numpy array - points x channels
    sample_rate: int
    n_channes: int
    ch_labels: list of strings
    time_vec: numpy array - (points,)
    bad_channels: list of int
    '''
    Data_dict = {"data": data, "sample_rate": sample_rate, "n_channels": n_channel, 
                 "ch_labels": ch_labels, "time_vec": time_vec, 
                 "bad_channels": bad_channels} 
    return Data_dict
    
    
def open_dataset(file_name,dataset_name):
    '''
    open a dataset in a specific file_name, return Data_dict
    '''
    # reading h5 file
    h5 = h5py.File(file_name,'r+')
    # loading dataset
    dataset = h5[dataset_name]
    # Sample Rate attribute
    sample_rate = dataset.attrs['SampleRate[Hz]']
    n_points         = dataset.shape[0]
    end_time         = n_points/sample_rate
    # Time vector
    time_vec         = np.linspace(0,end_time,n_points,endpoint=False)
    # Check if has 'Bad_channels' attribute, if not, create one empty
    if len([x for x in dataset.attrs.keys() if x == 'Bad_channels']) == 0:
        dataset.attrs.create("Bad_channels",[],dtype=int)
    # Load bad channels
    bad_channels = dataset.attrs["Bad_channels"]    
    # Creating dictionary
    Data_dict = make_dict(dataset[:],sample_rate,dataset.shape[1],dataset.attrs['Channel_Labels'],time_vec,bad_channels)
    h5.close()
    return Data_dict
    
def save_dataset(Data_dict,file_name,dataset_name):
    '''
    save Data_dic in a dataset in a specific file_name
    '''
    h5 = h5py.File(file_name,'a')
    data = Data_dict['data']
    dataset  = h5.require_dataset(dataset_name,data=data, shape = data.shape, dtype= data.dtype)
    dataset.attrs.create('SampleRate[Hz]',Data_dict['sample_rate'])
    dataset.attrs.create('Bad_channels',Data_dict['bad_channels'])
    dataset.attrs.create('Channel_Labels', Data_dict['ch_labels'])
    h5.close()
    
def loadRDH(filename):
    ''' 
    Created to load 64 channels at port A -  code need change if use diferent configuration. 
    It use RHD.py file to read and return Data_dict
    '''
    # load file
    myData = RHD.openRhd(filename)
    # get sample rate
    sample_rate = myData.sample_rate
    # get channels 
    myChannels = myData.channels
    # create a empty signal
    signal = np.zeros((myChannels['A-000'].getTrace().size,64))
    signal[:] = np.NAN
    labels = [] 
    for ch in range(64):
        if ch < 10:
            label = "A-00" + str(ch)
        else:
            label = "A-0" + str(ch)
        signal[:,ch] = myChannels[label].getTrace()
        labels.append(label)
    
    # Time vector   
    n_points  = signal.shape[0]
    end_time  = n_points/sample_rate
    time_vec  = np.linspace(0,end_time,n_points,endpoint=False)
    Data_dict = make_dict(signal,sample_rate,signal.shape[1],labels,time_vec,[])
    return Data_dict
    


    


def loadMAT(slice_filename,parameters_filename):
    '''
    Created to convert .mat files with specific configuration for ECoG data of Newcastle Hospitals and create a dict.
    If you want to load other .mat file, use scipy.io. loadmat and make_dict
    '''
    mat = sio.loadmat(parameters_filename, struct_as_record=False, squeeze_me=True)
    parameters = mat['parameters']
    n_channel =  parameters.num_channels
    ch_labels = parameters.channels
    sample_rate = parameters.sr
    f = sio.loadmat(slice_filename, struct_as_record=False, squeeze_me=True)
    Data = f['Data']
    time_vec = Data.time_vec
    signal = Data.raw.T
    Data_dict = make_dict(signal,sample_rate,n_channel,ch_labels,time_vec,[])
    return Data_dict