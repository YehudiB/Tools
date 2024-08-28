#Yehudi Bloch 2024

import base64 
import os
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc

#the bli data is stored as a base64 encoded array of float32 values
#the df columns AssayYData_i_decoded hold the decoded values to play around with


# Main function to create the pandas DataFrame
def create_dataframe(folder_path):
    frd_files = find_frd_files(folder_path)
    data,concentrations = parse_frd_files(frd_files)
    df = pd.DataFrame(data)
    return df,concentrations

# Function to find all .frd files in a given folder
def find_frd_files(folder_path):
    frd_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.frd'):
            frd_files.append(os.path.join(folder_path, file))
    return frd_files

# Function to parse .frd files and extract data
def parse_frd_files(frd_files):
    data = {}
    concentrations = []
    max_length = 0
    
    for i, file in enumerate(frd_files):
        tree = ET.parse(file)
        root = tree.getroot()
        
        # get steps and data
        assay_x_data = [elem.text for elem in root.findall('.//AssayXData')]
        assay_y_data = [elem.text for elem in root.findall('.//AssayYData')]
        step_names = [elem.text for elem in root.findall('.//StepName')]

        # get list of concentrations
        molar_concentrations = [elem.text for elem in root.findall('.//MolarConcentration')]
        molar_conc_units = [elem.text for elem in root.findall('.//MolarConcUnits')]
        pairs = zip(molar_concentrations, molar_conc_units)
        filtered_pairs = [f"{conc} {unit}" for conc, unit in pairs if conc != '-1']
        concentrations.extend(filtered_pairs)
                
        max_length = max(max_length, len(assay_x_data), len(assay_y_data), len(step_names))
        
        data[f'StepName_{i}'] = step_names
        data[f'AssayXData_{i}'] = assay_x_data
        data[f'AssayYData_{i}'] = assay_y_data
        data[f'AssayXData_{i}_decoded'] = [decode(x) for x in assay_x_data]
        data[f'AssayYData_{i}_decoded'] = [decode(y) for y in assay_y_data]
    
    # Ensure all lists are of the same length by padding with None
    for key in data:
        data[key] += [None] * (max_length - len(data[key]))
    
    return data,concentrations

def decode(encoded):
    data = base64.b64decode(encoded)
    decoded_data = np.frombuffer(data, dtype=np.float32) #numpy is required for the bg operations, doesn't work if it's a tuple
    return decoded_data

# Deals with most common types of background subtraction
def create_bg_subtracted_df(df, bg):
    n = len(df.columns) // 5
    df_bg_subtracted = pd.DataFrame()
    if bg == "none":
        for i in range(n):
            df_bg_subtracted[f'StepName_{i}'] = df[f'StepName_{i}']
            df_bg_subtracted[f'AssayXData_{i}_decoded'] = df[f'AssayXData_{i}_decoded']-df[f'AssayXData_{i}_decoded'].iloc[0][-1:]
            df_bg_subtracted[f'AssayYData_{i}_decoded'] = df[f'AssayYData_{i}_decoded']
            bg_offset=np.mean(df_bg_subtracted[f'AssayYData_{i}_decoded'].iloc[0][-10:])
            df_bg_subtracted[f'AssayYData_{i}_decoded'] = df_bg_subtracted[f'AssayYData_{i}_decoded']  - bg_offset
    
    elif bg == "single":
        for i in range(n - 1):
            df_bg_subtracted[f'StepName_{i}'] = df[f'StepName_{i}']
            df_bg_subtracted[f'AssayXData_{i}_decoded'] = df[f'AssayXData_{i}_decoded']-df[f'AssayXData_{i}_decoded'].iloc[0][-1:]
            df_bg_subtracted[f'AssayYData_{i}_decoded'] = df[f'AssayYData_{i}_decoded'] - df[f'AssayYData_{n-1}_decoded']
            bg_offset=np.mean(df[f'AssayYData_{i}_decoded'].iloc[0][-10:])
            df_bg_subtracted[f'AssayYData_{i}_decoded'] = df_bg_subtracted[f'AssayYData_{i}_decoded']- bg_offset
    
    elif bg == "double":
        for i in range(n // 2 - 1):
            df_bg_subtracted[f'StepName_{i}'] = df[f'StepName_{i}']
            df_bg_subtracted[f'AssayXData_{i}_decoded'] = df[f'AssayXData_{i}_decoded']-df[f'AssayXData_{i}_decoded'].iloc[0][-1:]
            df_bg_subtracted[f'AssayYData_{i}_decoded'] = (df[f'AssayYData_{i}_decoded']-df[f'AssayYData_{n//2-1}_decoded']) - (df[f'AssayYData_{i + n // 2}_decoded'] - df[f'AssayYData_{n-1}_decoded']) 
            bg_offset=np.mean(df_bg_subtracted[f'AssayYData_{i}_decoded'].iloc[0][-10:])
            df_bg_subtracted[f'AssayYData_{i}_decoded'] = df_bg_subtracted[f'AssayYData_{i}_decoded']- bg_offset
    
    return df_bg_subtracted

#in case of drift and you didn't include a proper control
def drift_correction(df_bg_subtracted, drift, time):
    correction_factor = -drift / time 
    n = len(df_bg_subtracted.columns) // 3
    df_temp = pd.DataFrame()
    for i in range(n):
        df_temp = df_bg_subtracted[f'AssayXData_{i}_decoded']*correction_factor
        df_bg_subtracted[f'AssayYData_{i}_decoded'] = df_bg_subtracted[f'AssayYData_{i}_decoded']+df_temp
    return df_bg_subtracted

# Function to plot the decoded data
def plot_decoded_data(df,coln,concentrations):
    fig = go.Figure()
    colorscale = px.colors.sequential.Viridis
    colors = pc.sample_colorscale(colorscale, np.linspace(0, 1, coln))
        
    for i in range(coln):
        x_col = f'AssayXData_{i}_decoded'
        y_col = f'AssayYData_{i}_decoded'
        
        if x_col in df.columns and y_col in df.columns:
            # Concatenate all rows for the current column
            concatenated_x_data = np.concatenate(df[x_col].dropna().values)
            concatenated_y_data = np.concatenate(df[y_col].dropna().values)
            
            # Add scatter plot trace
            fig.add_trace(go.Scatter(
                x=concatenated_x_data,
                y=concatenated_y_data,
                mode='lines',
                name=concentrations[i],
                line=dict(color=colors[i],)
            ))
    
    fig.update_layout(
        title='Curve goes brrrrr',
        xaxis_title='Time (s)',
        yaxis_title='Δλ (nm)',
        colorway=colors
    )
    
    fig.show()

## Example usage
folder_path = r'C:\path\to\bli\result\folder'
df,concentrations = create_dataframe(folder_path)

bg = "double"  # Change this to "none", "single", or "double" as needed, it will always set the last part of the first baseline to zero
df_bg_subtracted = create_bg_subtracted_df(df, bg)

drift=False # Change to true and change the values passed onto the function to correct for linear drift. Should have set up proper reference!
if drift:
    df_bg_subtracted = drift_correction(df_bg_subtracted, -0.08, 1800)

# Plot the data
coln=len(df.columns) // 5
plot_decoded_data(df,coln,concentrations)
coln=len(df_bg_subtracted.columns) // 3
plot_decoded_data(df_bg_subtracted,coln,concentrations)

