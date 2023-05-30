To run the analysis:
1) download the .raw files and put it the chosen directory
2) rename the files removing the _
3) move the configs file in the chosen directory
4) create a directory for the output
5) put analysis_launcher.py, merge_all.py and utils.py (previous directory) in its-corryvreckan-tools
6) set everything inside analysis_launcher.py
7) compile the custom version of EventLoaderEudaq2 (for the noise)
8) run analysis_launcher.py: python analysis_launcher.py -al -e -an -r
   it will run the alingment, eta correction, analysis and once you have an aligned geometry file that can be reaused it will do it
9) run merge_all.py to merge all the output. It will create new .root files and .txt with the path that you can copy paste in the configs file for eff_res_plotter.py
