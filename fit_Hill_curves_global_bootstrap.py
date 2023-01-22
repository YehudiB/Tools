import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.utils import resample
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
#warnings.filterwarnings(action='ignore')

data = {
  "x": [0.038836109,0.097090273,0.242725683,0.606814208,1.51703552,3.7925888,9.481472,23.70368,59.2592,148.148,370.37,0.038836109,0.097090273,0.242725683,0.606814208,1.51703552,3.7925888,9.481472,23.70368,59.2592,148.148,370.37,0.038836109,0.097090273,0.242725683,0.606814208,1.51703552,3.7925888,9.481472,23.70368,59.2592,148.148,370.37],
  "y1": [0.003666667,0.002666667,0.003666667,0.011666667,0.040666667,0.175666667,0.460666667,0.567666667,0.675666667,0.703666667,0.727666667,0.001666667,0.000666667,-0.000333333,0.007666667,0.035666667,0.173666667,0.459666667,0.548666667,0.694666667,0.755666667,0.635666667,-0.007333333,-0.006333333,-0.006333333,-0.002333333,0.031666667,0.167666667,0.455666667,0.552666667,0.580666667,0.636666667,0.628666667],
  "y2": [0.0015,-0.0015,0.0005,0.0075,0.0415,0.1805,0.4565,0.5435,0.5905,0.6075,0.6845,-0.0045,-0.0025,-0.0035,0.0025,0.0345,0.1725,0.4515,0.5535,0.5905,0.6445,0.7635,-0.0035,-0.0015,0.0005,0.0055,0.0415,0.1905,0.5045,0.5955,0.6275,0.6575,0.6915],
  "y3": [0.002333333,0.000333333,0.000333333,0.012333333,0.053333333,0.239333333,0.591333333,0.704333333,0.783333333,0.804333333,0.771333333,0.001333333,-0.001666667,-0.002666667,0.010333333,0.056333333,0.236333333,0.559333333,0.615333333,0.805333333,0.837333333,0.835333333,-0.003666667,-0.010666667,-0.001666667,0.009333333,0.049333333,0.231333333,0.565333333,0.716333333,0.859333333,0.923333333,0.874333333],
  "f1":[-0.004333333,-0.004333333,-0.005333333,-0.005333333,-0.001333333,0.018666667,0.123666667,0.355666667,0.582666667,0.644666667,0.645666667,0.006666667,0.003666667,0.001666667,-0.005333333,0.000666667,0.022666667,0.137666667,0.380666667,0.557666667,0.652666667,0.631666667,-0.005333333,-0.006333333,-0.008333333,-0.009333333,-0.005333333,0.015666667,0.118666667,0.348666667,0.510666667,0.571666667,0.563666667],
  "f2":[-0.0025,-0.0035,-0.0045,-0.0035,-0.0055,0.0175,0.1295,0.3745,0.5595,0.6135,0.6485,-0.0075,-0.0065,-0.0105,-0.0045,-0.0075,0.0185,0.1415,0.3635,0.5595,0.5905,0.6655,-0.0045,-0.0045,-0.0015,-0.0055,-0.0035,0.0205,0.1335,0.3665,0.5575,0.6115,0.6905],
  "f3":[-0.003666667,-0.004666667,-0.000666667,-0.002666667,-0.001666667,0.026333333,0.157333333,0.490333333,0.665333333,0.723333333,0.718333333,-0.006666667,-0.008666667,-0.008666667,-0.008666667,-0.007666667,0.013333333,0.120333333,0.416333333,0.587333333,0.639333333,0.826333333,-0.002666667,-0.008666667,-0.004666667,-0.006666667,-0.002666667,0.027333333,0.164333333,0.477333333,0.672333333,0.749333333,0.691333333]
}
df = pd.DataFrame(data)
comboX = pd.concat(objs=[df['x'],df['x'],df['x']]).T.values

def bootstrap(df,n):
    # Defining number of iterations for bootstrap resample
    n_iterations = 1000
    
    bootstrapped_stats = pd.DataFrame()
    data1 = df[['x', df.columns[n*3+1]]]
    data2 = df[['x', df.columns[n*3+2]]]
    data3 = df[['x', df.columns[n*3+3]]]
    
    for i in range(n_iterations):
        train1 = resample(data1, replace=True, n_samples=len(data1))
        train2 = resample(data1, replace=True, n_samples=len(data2))
        train3 = resample(data1, replace=True, n_samples=len(data3))
        train = pd.concat(objs=[train1,train2,train3])
        x_train = train.iloc[:, 0].T.values
        y_train = train.iloc[:, 1].T.values
        
        # Fitting linear regression model
        popt_hill,pcov_hill=curve_fit(comboFunc,x_train,y_train,maxfev=2500,p0=[5,0.01,0,1,0,1,0,1])
        
        temp_res={"ec50":[popt_hill[0]],"hill":[popt_hill[1]],"min1":[popt_hill[2]],"max1":[popt_hill[3]]}
        bootstrapped_stats_i = pd.DataFrame(temp_res)
        bootstrapped_stats = pd.concat(objs=[bootstrapped_stats,bootstrapped_stats_i])
    
    bootstrapped_stats= bootstrapped_stats.sort_values(by=['ec50'],ignore_index=True)
    interval = [bootstrapped_stats.at[24,'ec50'],bootstrapped_stats.at[974,'ec50']]
    return interval

def mod1(data, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3): # not all parameters are used here
        return min_res1+(max_res1-min_res1)/(1+np.power((ec50/data),hill))


def mod2(data, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3): # not all parameters are used here
        return min_res2+(max_res2-min_res2)/(1+np.power((ec50/data),hill))

def mod3(data, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3): # not all parameters are used here
        return min_res3+(max_res3-min_res3)/(1+np.power((ec50/data),hill))

def comboFunc(comboData, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3):
    # single data set passed in, extract separate data
    extract1 = comboData[:33] # first data
    extract2 = comboData[33:66] # second data
    extract3 = comboData[66:]
    
    result1 = mod1(extract1, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3)
    result2 = mod2(extract2, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3)
    result3 = mod3(extract2, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3)

    return np.concatenate((result1, result2, result3))


# some initial parameter values
initialParameters = np.array([5,0.01,0,1,0,1,0,1])

# curve fit the combined data to the combined function
comboY = pd.concat(objs=[df['y1'],df['y2'],df['y3']]).T.values
fittedParameters, pcov = curve_fit(comboFunc, comboX, comboY, initialParameters)

# values for display of fitted function
ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3 = fittedParameters
print(fittedParameters)
ec50CI=bootstrap(df,0)
print("ec50 CI [ %f , " " %f,]" % (ec50CI[0],ec50CI[1]))

#draw first bunch of curves
x = np.geomspace(min(comboX), max(comboX), num=50)
y_fit_1 = mod1(x, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3) 
y_fit_2 = mod2(x, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3) 
y_fit_3 = mod3(x, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3)

plt.clf()
cmap = mpl.cm.get_cmap('magma')
plt.figure(figsize=(8,5))
plt.xscale("log")
plt.scatter(df['x'].T.values,df['y1'].T.values,color=cmap(0.04),marker='o')
plt.scatter(df['x'].T.values,df['y2'].T.values,color=cmap(0.18),marker='o')
plt.scatter(df['x'].T.values,df['y3'].T.values,color=cmap(0.32),marker='o')
plt.plot(x, y_fit_1,color=cmap(0.04),label='fit ') 
plt.plot(x, y_fit_2,color=cmap(0.18),label='fit ') 
plt.plot(x, y_fit_3,color=cmap(0.32),label='fit ')

#curve fit the second combined data to the combined function
comboY = pd.concat(objs=[df['f1'],df['f2'],df['f3']]).T.values
fittedParameters, pcov = curve_fit(comboFunc, comboX, comboY, initialParameters)

# values for display of fitted function
ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3 = fittedParameters
print(fittedParameters)
ec50CI=bootstrap(df,1)
print("ec50 CI [ %f , " " %f,]" % (ec50CI[0],ec50CI[1]))

#draw second bunch
y_fit_1 = mod1(x, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3) 
y_fit_2 = mod2(x, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3) 
y_fit_3 = mod3(x, ec50,hill,min_res1,max_res1,min_res2,max_res2,min_res3,max_res3)
plt.scatter(df['x'].T.values,df['f1'].T.values,color=cmap(0.66),marker='o')
plt.scatter(df['x'].T.values,df['f2'].T.values,color=cmap(0.80),marker='o')
plt.scatter(df['x'].T.values,df['f3'].T.values,color=cmap(0.94),marker='o')
plt.plot(x, y_fit_1,color=cmap(0.66),label='fit ') 
plt.plot(x, y_fit_2,color=cmap(0.80),label='fit ') 
plt.plot(x, y_fit_3,color=cmap(0.94),label='fit ')

plt.legend(loc='best')
plt.ylabel('OD655nm')
plt.xlabel('[] (nM)')
plt.show()
#plt.savefig("./dose_response.pdf")