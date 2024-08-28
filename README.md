# Tools
General purpose tools

# read_bli.py
Script that converts the .frd file format into usable data. Biolayer Interferometry (BLI) data is saved by the machine (Fortebio/Sartorius "Octet") in individual folders per experiment with a single .frd file(xml formatted) per sensor. The script extracts all .frd files from a given folder and converts the encoded time and response values into plain float32 values for all to enjoy. 
Can also do simple reference correction.
-  none: aligns to end of baseline
-  single: none and assumes last tip is reference
-  double: single and assumes second half of measurements are reference

<img src="https://github.com/user-attachments/assets/efd96094-5272-49da-970e-3cc1cefc8ee0" width="800">
  
# m8_to_fasta_aln.py
Script that converts m8 alignment file from Foldseek (https://search.foldseek.com/search) and converts it into an aligned .fasta. Takes a few minutes to run on a few hundred sequences. Rough around the edges but works.

# fit_Hill_curves_global_bootstrap.py
Script to globally fit Hill equation (dose response curve) to a triplicate and do bootstrap analysis to report CI interval on the determined EC50 value. Rough around the edges but works.

# cryosparc_rebalance_3D.py
Script to rebalance your particle stack after 3D reconstruction. Runs in the cryosparcm icli python interpreter. Of course this requires the low abundance particles to be actual particles otherwise it will do more harm than good. Requires pyem.

<img src="https://user-images.githubusercontent.com/106915051/236044282-c9a51190-6e0f-45ac-8299-32ef726ba4aa.png" width="800">

This is now implemented in Cryosparc.

# extract_tls.py
Script to extract TLS group definitions from PDB header as written out by Phenix.refine into REFMAC format. Requires CCP4. This fixes the inability of ccp4 to read the TLS atom selection. Also writes out a gelly style TLS group definition for Buster.
> extract_tls.py ./location/of/input/pdb.pdb
