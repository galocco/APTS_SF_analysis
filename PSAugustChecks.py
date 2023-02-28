#macro to check if one ALPIDE is not working well
import ROOT
alpide_list = [0,1,2,4,5,6]
color_list = [ROOT.kRed,ROOT.kBlack,ROOT.kBlue,,ROOT.kGreen,ROOT.kGreen,ROOT.kOrange]

cv_list_x = []
for i in range(0,7):
    cv = ROOT.TCanvas("ResALPIDE_"+str(i)+"_x","ResALPIDE_"+str(i)+"_x")
    cv_list_x.append(cv)

cv_list_y = []
for i in range(0,7):
    cv = ROOT.TCanvas("ResALPIDE_"+str(i)+"_y","ResALPIDE_"+str(i)+"_y")
    cv_list_y.append(cv)

for ALPIDE in alpide_list:
    path = "/home/giacomo/its-corryvreckan-tools/output/PSAugust/B2/AF20P_W22B6_NOALPIDE_"+str(ALPIDE)+"/AF20P_W22B6/analysis_345211441220826211447_DUT_thr80.root"
    file = ROOT.TFile(path,"read")
    res_alpide_list = alpide_list
    res_alpide_list.pop(ALPIDE)
    for res_alpide in res_alpide_list:
        hist_x = file.Get("Tracking4D/ALPIDE_"+str(res_alpide)+"/global_residuals/GlobaResidualsX")
        hist_y = file.Get("Tracking4D/ALPIDE_"+str(res_alpide)+"/global_residuals/GlobaResidualsY")
        hist_x.SetName("resALPIDE"+str(res_alpide)+"_NO_ALPIDE_"+str(ALPIDE))
        hist_y.SetName("resALPIDE"+str(res_alpide)+"_NO_ALPIDE_"+str(ALPIDE))
        hist_x.SetLineColor(color_list[res_alpide])
        hist_y.SetLineColor(color_list[res_alpide])
        cv_list_x[res_alpide].cd()
        hist_x.Draw("same")
        cv_list_y[res_alpide].cd()
        hist_y.Draw("same")

for cv in cv_list_y:
    cv.SaveAs(cv.GetName()+".png")
for cv in cv_list_x:
    cv.SaveAs(cv.GetName()+".png")

