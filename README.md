# Tools
General purpose tools

# m8_to_fasta_aln.py
Script that converts m8 alignment file from Foldseek (https://search.foldseek.com/search) and converts it into an aligned .fasta. Takes a few minutes to run on a few hundred sequences. Rough around the edges but works.

# fit_Hill_curves_global_bootstrap.py
Script to globally fit Hill equation (dose response curve) to a triplicate and do bootstrap analysis to report CI interval on the determined EC50 value. Rough around the edges but works.

# cryosparc_rebalance_3D.py
Script to rebalance your particle stack after 3D reconstruction. Runs in the cryosparcm icli python interpreter. Of course this requires the low abundance particles to be actual particles otherwise it will do more harm than good. Requires pyem.

<img src="https://user-images.githubusercontent.com/106915051/236044282-c9a51190-6e0f-45ac-8299-32ef726ba4aa.png" width="800">
