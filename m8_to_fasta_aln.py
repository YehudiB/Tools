# run as: python m8_to_fasta.py ../location/input_file.m8 ../location/output_file.fasta

import numpy as np
import pandas as pd
import sys
from contextlib import redirect_stdout

m8_location="../Downloads/alis_afdb50.m8"
fasta_output="./testaln.fasta"
filtered_output="./filtered_testaln.fasta"
#m8_location=sys.argv[1]
#fasta_output=sys.argv[2]

def insert_dash(string, index):
    return string[:index] + '-' + string[index:]

def insert_dot(string, index):
    return string[:index] + '.' + string[index:]

#the ca position won't be properly read
m8df=pd.read_table(m8_location,delimiter="\t",dtype=str)
colnames=['job','target','percent_identity','alignment_length','n_mismatch','gapopen','qstart','qend','tstart','tend','evalue','bits','qlength','tlength','tend','qaln','taln','Ca_position','target_seq','taxid','Organism']
m8df.columns = colnames

m8df["percent_identity"] = m8df["percent_identity"].astype(float)
m8df["evalue"] = m8df["evalue"].astype(float)
m8df["qstart"] = m8df["qstart"].astype(int)
m8df["alignment_length"] = m8df["alignment_length"].astype(int)

#cull crap
m8df=m8df[m8df.evalue>0.95]
m8df=m8df.sort_values(by=['evalue'],ascending=False,ignore_index=True)
#if you want cull to a number
max_sequences=len(m8df.index)
#m8df=m8df[m8df.index<5]

#first pad N ter with dots
for i in range (0,max_sequences):
    for j in range (m8df.at[i,"qstart"]-1):
        m8df.at[i,"qaln"]=insert_dot(m8df.at[i,"qaln"],0)
        m8df.at[i,"taln"]=insert_dot(m8df.at[i,"taln"],0)

#pad C ter with dots
length_longest_taln=m8df.taln.str.len().max()
for i in range (0,max_sequences):
    pad=0
    diff=length_longest_taln-len(m8df.at[i,"taln"])
    while pad< diff:
        m8df.at[i,"qaln"]=insert_dot(m8df.at[i,"qaln"],len(m8df.at[i,"qaln"]))
        m8df.at[i,"taln"]=insert_dot(m8df.at[i,"taln"],len(m8df.at[i,"taln"]))
        pad=pad+1
        
#insert dashes when dash is found and otherwise ass dot at end

not_beyond=True
string_pos=0
while not_beyond:
    i=0
    dash_notfound=True
    while dash_notfound:
        if (m8df.at[i,"qaln"][string_pos]) =="-":
            dash_notfound=False
            for j in range (0,max_sequences):
                if (m8df.at[j,"qaln"][string_pos]) != "-":
                    m8df.at[j,"qaln"]=insert_dash(m8df.at[j,"qaln"],string_pos)
                    m8df.at[j,"taln"]=insert_dash(m8df.at[j,"taln"],string_pos)
                elif (m8df.at[j,"qaln"][string_pos]) == "-":
                    m8df.at[j,"qaln"]=insert_dot(m8df.at[j,"qaln"],len(m8df.at[j,"qaln"]))
                    m8df.at[j,"taln"]=insert_dot(m8df.at[j,"taln"],len(m8df.at[j,"taln"]))
        i+=1
        if i >= (max_sequences): dash_notfound=False
    string_pos+=1
    if m8df.taln.str.len().max()<=string_pos:not_beyond=False
    #length_longest_taln=m8df.taln.str.len().max()
    #print(length_longest_taln)

#writing output
with open(fasta_output,"w") as f:
    with redirect_stdout(f):
        print(">Query_aligned_to_best_hit")
        print(m8df.at[0,"qaln"].replace(".","-"))
        for i in range (0,max_sequences):
            print(">"+str(m8df.at[i,"target"])+"_"+str(m8df.at[i,"taxid"])+"_"+str(m8df.at[i,"Organism"]))
            print(m8df.at[i,"taln"].replace(".","-"))

#selecting only specific values
with open(filtered_output,"w") as f:
    with redirect_stdout(f):
        print(">Query_aligned_to_best_hit")
        print(m8df.at[0,"qaln"].replace(".","-"))
        for i in range (0,max_sequences):
            if (m8df.at[i,"taln"][344]) =="Y":
                print(">"+str(m8df.at[i,"target"])+"_"+str(m8df.at[i,"taxid"])+"_"+str(m8df.at[i,"Organism"]))
                print(m8df.at[i,"taln"].replace(".","-"))