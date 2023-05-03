from scipy.interpolate import interpn
from pyem import geom
import numpy as np
import pandas as pd
import random as rd

#if you don't have pyem you could also define the pyem rot2euler and expmap functions here

#to avoid issues first glue together your particle stack and the passthrough info
dsd= dataset.Dataset.load('/my/folder/location/cryosparc_P59_J470_009_particles.cs')
dsp= dataset.Dataset.load('/my/folder/location/P59_J470_passthrough_particles.cs')
ds=dsd.innerjoin(dsp)

posenumpy=np.array(ds['alignments3D/pose'])
posenumpy_degrees=np.zeros(posenumpy.shape,dtype='single')
for i in range (len(posenumpy_degrees)):
    posenumpy_degrees[i]=np.rad2deg(rot2euler(expmap(posenumpy[i])))
numpy_hist,x_e,y_e=np.histogram2d(posenumpy_degrees.T[0],posenumpy_degrees.T[1],bins=[360,180],density=False)
numpy_dens = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , numpy_hist , np.vstack([posenumpy_degrees.T[0],posenumpy_degrees.T[1]]).T , method = "linear", bounds_error = False)

to_keep_bool=np.zeros(numpy_dens.shape,dtype='bool')
for i in range (len(numpy_dens)):
    if numpy_dens[i]>15:    #this value will depend on your dataset. In this case it was equal to the mean of numpy_dens, particles belonging to an orientation occuring fewer than 15 particles / °² will all be kept.
      if rd.uniform(0,numpy_dens[i]) > 15:
         to_keep_bool[i]=False
      else:
         to_keep_bool[i]=True
    else:
         to_keep_bool[i]=True

ds_culled=ds.take(to_keep_bool)
ds_culled.save('/my/folder/location/pose_culled.cs')

#don't forget to copy your particles csg file, and have all entries point to pose_culled.cs and update the particle numbers
