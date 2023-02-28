import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import math

z_position_list = [71,71.2,70.8,70.7,71.3,70.7,70.6,70.5,70.4,70.3,70.2,75]
chip = ''
# quantities to be studied as a function of z:
# 1) efficiency
# 2) resolution
# 3) number of tracks

fig_eff, ax_eff = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

fig_ntrk, ax_ntrk = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

fig_resx, ax_resx = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

fig_resy, ax_resy = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

fig_res_mean, ax_res_mean = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

#ax.errorbar([],[],([],[]),label="x-position resolution ",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
#ax.errorbar([],[],([],[]),label="cluster size",marker='o',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

eff_list = []
resx_list = []
resy_list = []
res_mean_list = []
ntrk_list = []

err_eff_up_list = []
err_eff_low_list = []
err_resx_list = []
err_resy_list = []
err_res_mean_list = []
err_ntrk_list = []

for z_pos in z_position_list:
    input_file = ROOT.TFile('/home/giacomo/its-corryvreckan-tools/output/PSAugust/B2/AF20P_W22B6_APTS_Z_'+str(z_pos)+'/analysis_345211441220826211447_DUT_thr80.root')
    input_file_2 = ROOT.TFile('/home/giacomo/its-corryvreckan-tools/output/PSAugust/B2/AF20P_W22B6_APTS_Z_'+str(z_pos)+'/analysis_345171002220826171008_DUT_thr80.root')
    print(z_pos)
    if chip == "AF25P_W22_1.2V" or chip == "AF20P_W22_1.2V":
        apts = "4"
    else:
        apts = "3"
    residualsX= input_file.Get("AnalysisDUT/APTS_"+apts+"/local_residuals/residualsX")
    residualsY= input_file.Get("AnalysisDUT/APTS_"+apts+"/local_residuals/residualsY")
    associated= input_file.Get("AnalysisDUT/APTS_"+apts+"/hAssociatedTracksLocalPosition")
    unassociated= input_file.Get("AnalysisDUT/APTS_"+apts+"/hUnassociatedTracksLocalPosition")

    residualsX.Add(input_file_2.Get("AnalysisDUT/APTS_"+apts+"/local_residuals/residualsX"))
    residualsY.Add(input_file_2.Get("AnalysisDUT/APTS_"+apts+"/local_residuals/residualsY"))
    associated.Add(input_file_2.Get("AnalysisDUT/APTS_"+apts+"/hAssociatedTracksLocalPosition"))
    unassociated.Add(input_file_2.Get("AnalysisDUT/APTS_"+apts+"/hUnassociatedTracksLocalPosition"))

    efficiency = input_file.Get("AnalysisEfficiency/APTS_"+apts+"/eTotalEfficiency")

    trk_ass = associated.GetEntries() 
    trk_unass = unassociated.GetEntries()
    ntrk_list.append(trk_ass+trk_unass)
    err_ntrk_list.append(math.sqrt(trk_ass+trk_unass))

    resx_list.append(residualsX.GetStdDev())
    resy_list.append(residualsY.GetStdDev())
    err_resx_list.append(residualsX.GetStdDevError())
    err_resy_list.append(residualsY.GetStdDevError())

    res_mean_list.append((residualsX.GetStdDev()+residualsY.GetStdDev())/2.)
    err_res_mean_list.append((residualsX.GetStdDevError()+residualsY.GetStdDevError())/2.)

    eff_list.append(100*efficiency.GetEfficiency(1))
    err_eff_up_list.append(100*efficiency.GetEfficiencyErrorUp(1))
    err_eff_low_list.append(100*efficiency.GetEfficiencyErrorLow(1))


ax_eff.errorbar(z_position_list, eff_list, yerr=[err_eff_low_list,err_eff_up_list], marker="s", linestyle='')
ax_resx.errorbar(z_position_list, resx_list, yerr=[err_resx_list,err_resx_list], marker="s", linestyle='')
ax_resy.errorbar(z_position_list, resy_list, yerr=[err_resy_list,err_resy_list], marker="s", linestyle='')
ax_res_mean.errorbar(z_position_list, res_mean_list, yerr=[err_res_mean_list,err_res_mean_list], marker="s", linestyle='')
ax_ntrk.errorbar(z_position_list, ntrk_list, yerr=[err_ntrk_list,err_ntrk_list], marker="s", linestyle='')


ax_eff.set_ylabel('Efficiency (%)')
ax_eff.set_xlabel('APTS z position (mm)')
ax_eff.grid()


ax_resx.set_ylabel('x-residuals Std.Dev. (um)')
ax_resx.set_xlabel('APTS z position (mm)')
ax_resx.grid()

ax_resy.set_ylabel('y-residuals Std.Dev. (um)')
ax_resy.set_xlabel('APTS z position (mm)')
ax_resy.grid()

ax_res_mean.set_ylabel('residuals Std.Dev. (um)')
ax_res_mean.set_xlabel('APTS z position (mm)')
ax_res_mean.grid()

ax_ntrk.set_ylabel('number of tracks in the 4 central pixels')
ax_ntrk.set_xlabel('APTS z position (mm)')
ax_ntrk.grid()

fig_eff.savefig('ChecksAPTSZ/efficiencyVsZ.png', dpi=600)
fig_resx.savefig('ChecksAPTSZ/resolutionXVsZ.png', dpi=600)
fig_resy.savefig('ChecksAPTSZ/resolutionYVsZ.png', dpi=600)
fig_res_mean.savefig('ChecksAPTSZ/resolutionMeanVsZ.png', dpi=600)
fig_ntrk.savefig('ChecksAPTSZ/ntracksVsZ.png', dpi=600)
