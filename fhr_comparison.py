import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

hundredElectronToADCu = {
               "AF15_W13_1.2V" : 113.5602885,
               "AF15_W22_1.2V" : 112.6764784,
               "AF15B_W22_1.2V":  79.90360556,
               "AF15P_W22_1.2V":  79.82152217,
               "AF10P_W22_1.2V":  80.31095738,
               "AF20P_W22_1.2V":  80.09704306,
               "AF25P_W22_1.2V":  79.86636469,
               "AF15P_W22_0V"  :  44.7844201,
               "AF15P_W22_2.4V": 103.97717,
               "AF15P_W22_3.6V": 116.4895804,
               "AF15P_W22_4.8V": 122.3611669
            }

list_of_files = [
                    "alignment_415000658221014000702_DUT_FHR.root",
                    "alignment_415000658221014000702_DUT_FHR_2.root",
                    "alignment_414153944221013153949_DUT_FHR.root"
                ]

list_of_labels = [
                    "pixel pitch 10um",
                    "pixel pitch 10um 2",
                    "irradiated"
                 ]
list_of_frames = [
                    1,
                    1,
                    1
                 ]

n_pixels = 16

fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

err_bar_list = []
list_of_thr = [0,10,20,30,40,50,60,70,80,90,100,110,120,130]#,140,150,200,300,400]
for file,label,n_frames in zip(list_of_files, list_of_labels,list_of_frames):

    tfile = ROOT.TFile(file,"read")
    hist = tfile.Get("EventLoaderEUDAQ2/APTS_3/hPixelRawValues")#To be changed for June data

    thrs_list = []
    bins_list = []
    for thr in list_of_thr:
        for k in range(1, hist.GetNbinsX()):
            if hist.GetBinLowEdge(k) > thr:
                bins_list.append(k)
                thrs_list.append(hist.GetBinLowEdge(k))
                break

    n_events = (hist.GetEntries()-hist.GetBinContent(0))/n_pixels
    fake_hit_rate_list = []

    for bin_min in bins_list:
        clusters = hist.Integral(bin_min, hist.GetNbinsX()+1)
        fake_hit_rate_list.append(clusters/n_pixels/n_events/n_frames)

    ax1.errorbar(list_of_thr, fake_hit_rate_list, label=label, marker="s", linestyle='')

ax1.set_ylabel('Fake hit rate')
ax1.set_xlabel('threshold (ADCu)')
ax1.set_title('Vmin in the frames [41,90], baseline = mean of frames in range [0,40]')
#ax1.legend()

ax1.grid(axis='both')
ax1.set_yscale("log")
ax1.set_ylim(10**(-7),1)

ax1.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})

x = 0.8
y = 0.99

ax1.text(
    x,y,
    '$\\bf{ITS3}$ beam test $\\it{preliminary}$',
    fontsize=12,
    ha='center', va='top',
    transform=ax1.transAxes
)

ax1.text(
    x,y-0.06,
    '@PS June 2022, 10 GeV/c protons',
    fontsize=9,
    ha='center', va='top',
    transform=ax1.transAxes
)

ax1.text(1.1,1.0,
    '\n'.join([
        'type: %s'%'modified with gap',
        'split:  %s'%'4',
        '$V_{sub}=V_{pwell}$ = -1.2 V',
        '$I_{reset}=%s\,\\mathrm{pA}$' %100,
        '$I_{biasn}=%s\,\\mathrm{\mu A}$' %5,
        '$I_{biasp}=%s\,\\mathrm{\mu A}$' %0.5,
        '$I_{bias4}=%s\,\\mathrm{\mu A}$' %150,
        '$I_{bias3}=%s\,\\mathrm{\mu A}$' %200,
        '$V_{reset}=%s\,\\mathrm{mV}$' %500
    ]),
    fontsize=9,
    ha='left', va='top',
    transform=ax1.transAxes
)

plt.show()
fig.savefig('FakeHitRateVsThreshold.png', dpi=800)