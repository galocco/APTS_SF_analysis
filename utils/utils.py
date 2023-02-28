from ROOT import TMath

# dictionary with the conversion from 100e- to ADCu
hundredElectronToADCu = {
    "AF15_W13_1.2V":  113.5602885,
    "AF15_W22_1.2V": 112.6764784,
    "AF15_W22_0.0V":	99.96019279,
    "AF15_W22_2.4V":	118.6366722,
    "AF15_W22_3.6V":	122.4966069,
    "AF15_W22_4.8V":	124.5837159,
    "AF15B_W22_1.2V":	79.90360556,
    "AF15B_W22_0.0V":	44.38443415,
    "AF15B_W22_2.4V":	104.1295414,

    "AF15P_W22_0V": 44.7844201,
    "AF15P_W22_2.4V": 103.97717,
    "AF15P_W22_3.6V": 116.4895804,
    "AF15P_W22_4.8V": 122.3611669,

    "AF15P_W22B9_IR2.5_1.2V":	76.7774608,
    "AF15P_W22B12_IR2.5_1.2V": 76.25865981,
    "AF15P_W22B16_IR2.5_1.2V": 81.95167308,
    "AF15P_W22B16_IR2.5_0.0V": 48.42682102,
    "AF15P_W22B16_IR2.5_2.4V": 100.5220934,
    "AF15P_W22B16_IR2.5_3.6V": 110.0892196,
    "AF15P_W22B16_IR2.5_4.8V": 114.0137095,

    "AF25B_W22_1.2V":	    79.19905893,
    "AF25B_W22_0V":			43.49487644,
    "AF25B_W22_2.4V":		104.9121782,
    "AF25B_W22_3.6V":		118.5515334,
    "AF25B_W22_4.8V":		125.7991292,
    "AF10B_W22_1.2V":	    78.24761423,
    "AF10B_W22_0V":			42.92999417,
    "AF10B_W22_2.4V":		103.0991327,
    "AF10B_W22_3.6V":		115.96225,
    "AF10B_W22_4.8V":		122.5137794,
    "AF15P_W22_1.2V":	    79.84663062,
    "AF10P_W22_1.2V":		80.31095738,
    "AF10P_W22_0V":			45.23827032,
    "AF10P_W22_2.4V":		104.6569318,
    "AF10P_W22_3.6V":		117.084588,
    "AF10P_W22_4.8V":		122.9757817,
    "AF20P_W22_1.2V":       80.09704306,
    "AF25P_W22_1.2V":	    79.86636469,
    "AF25P_W22_0V":			44.43762416,
    "AF25P_W22_2.4V":		105.157962,
    "AF25P_W22_3.6V":		118.0621447,
    "AF25P_W22_4.8V":		124.3887409
}


def qGauss(x, par):
    if x[0] <= par[4]:
        fitval = par[0]*TMath.Power(1 - (1 - par[2])*(1./(3 - par[2]))*(
            x[0] - par[4])*(x[0] - par[4])/(par[1]*par[1]), 1./(1 - par[2]))
    else:
        fitval = par[0]*TMath.Power(1 - (1 - par[3])*(1./(3 - par[3]))*(
            x[0] - par[4])*(x[0] - par[4])/(par[1]*par[1]), 1./(1 - par[3]))
    return fitval


def gauss_exp_tails(x, par):
    N = par[0]
    sig = par[1]
    mu = par[4]
    tau0 = par[2]
    tau1 = par[3]
    u = (x[0] - mu) / sig
    if (u < tau0):
        return N*TMath.Exp(-tau0 * (u - 0.5 * tau0))
    elif (u <= tau1):
        return N*TMath.Exp(-u * u * 0.5)
    else:
        return N*TMath.Exp(-tau1 * (u - 0.5 * tau1))

def clean_residuals(residuals, percentage = 90, mean=True):
    if mean:
        center = residuals.GetMean()
        center_bin = residuals.GetXaxis().FindBin(center)
    else:
        center_bin = residuals.GetMaximumBin()

    percentOfCounts = percentage*residuals.GetEntries()/100
    border_bin = residuals.GetNbinsX()-center_bin
    #print("90%:", percentOfCounts," 100%:", residuals.GetEntries())
    #print("center bin: ",center_bin)
    #print("nbins", residuals.GetNbinsX())
    if  center_bin - 1 < border_bin:
        border_bin = center_bin - 1
    #print("border bin:", border_bin)
    sum = residuals.GetBinContent(center_bin)
    bin_cut = 0 
    for bin in range(1, border_bin):
        sum += residuals.GetBinContent(center_bin-bin)
        sum += residuals.GetBinContent(center_bin+bin)
        ##print(sum, bin)
        if sum >= percentOfCounts:
            #print("Sum:", sum)
            bin_cut = bin+1
            break
        
    #print(bin_cut)
    for bin in range(1,center_bin-bin_cut+1):
        residuals.SetBinContent(bin,0)
    for bin in range(center_bin+bin_cut,residuals.GetNbinsX()+1):
        residuals.SetBinContent(bin,0)
