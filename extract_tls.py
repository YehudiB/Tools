import re
import os
import argparse
import subprocess

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process a pdb file.')
parser.add_argument('pdb_file', type=str, help='The path to the pdb file to process.')
args = parser.parse_args()

# Run the tlsextract program
subprocess.run(['tlsextract', 'XYZIN', args.pdb_file, 'TLSOUT', 'output.tls'])

def parse_pdb(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    output = []
    for i in range(len(lines)):
        if lines[i].startswith("REMARK   3   TLS GROUP :"):
            if i+1 < len(lines) and lines[i+1].startswith("REMARK   3    SELECTION:"):
                match = re.search(r"chain '(\w)' and \(resid (\d+) through (\d+) \)", lines[i+1])
                if match:
                    chain = match.group(1)
                    resid_start = match.group(2)
                    resid_end = match.group(3)
                    output.append(f"RANGE  '{chain}   {resid_start}' '{chain}  {resid_end}.' ALL")
            elif i+2 < len(lines) and lines[i+2].startswith("REMARK   3    ORIGIN FOR THE GROUP (A):"):
                match = re.search(r"REMARK   3    ORIGIN FOR THE GROUP \(A\): ([\-\d\.]+) ([\-\d\.]+) ([\-\d\.]+)", lines[i+2])
                if match:
                    x = match.group(1)
                    y = match.group(2)
                    z = match.group(3)
                    output.append(f"ORIGIN  {x} {y}  {z}")

    return output

# Parse the pdb file
parsed_output = parse_pdb(args.pdb_file)

# Read the output.tls file
with open('output.tls', 'r') as file:
    tls_lines = file.readlines()

# Replace the lines in output.tls
j=0
for i in range(len(tls_lines)):
    if tls_lines[i] == "RANGE  ''' ALL\n":
            if j < len(parsed_output):
                tls_lines[i] = parsed_output[j] + '\n'
                j += 1

# Write the updated lines to output_2.tls
with open('output_2.tls', 'w') as file:
    file.writelines(tls_lines)
