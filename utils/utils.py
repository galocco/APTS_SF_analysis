#Name convention
# AF{pitch}{type}_W{split}_{Vbb}V
# if irradiation level != none
#AF{pitch}{type}_W{split}_{Vbb}V_{irradiationlevel}   irradiation level in the format x.xxE+yy
# if Ireset != 1 
# AF{pitch}{type}_W{split}_{Vbb}V_{irradiationlevel}_IR{ireset}
# dictionary with the conversion from 100e+- to ADCu
hundredElectronToADCu = {
    "AF15_W13_1.2V" : 113.5602885,
    "AF15_W22_1.2V" : 112.6764784,
    "AF15_W22_0.0V" : 99.96019279,
    "AF15_W22_2.4V" : 118.6366722,
    "AF15_W22_3.6V" : 122.4966069,
    "AF15_W22_4.8V" : 124.5837159,
    "AF15B_W22_1.2V" : 79.90360556,
    "AF15B_W22_0.0V" : 44.38443415,
    "AF15B_W22_2.4V" : 104.1295414,
    "AF15B_W22_4.8V" : 108.5,
    "AF25B_W22_1.2V" : 79.19905893,
1
#Name convention
2
# AF{pitch}{type}_W{split}_{Vbb}V
3
# if irradiation level != none
4
#AF{pitch}{type}_W{split}_{Vbb}V_{irradiationlevel}   irradiation level in the format x.xxE+yy
5
# if Ireset != 1 
6
# AF{pitch}{type}_W{split}_{Vbb}V_{irradiationlevel}_IR{ireset}
7
# dictionary with the conversion from 100e+- to ADCu
8
hundredElectronToADCu = {
9
    "AF15_W13_1.2V" : 113.5602885,
10
    "AF15_W22_1.2V" : 112.6764784,
11
    "AF15_W22_0.0V" : 99.96019279,
12
    "AF15_W22_2.4V" : 118.6366722,
13
    "AF15_W22_3.6V" : 122.4966069,
14
    "AF15_W22_4.8V" : 124.5837159,
15
    "AF15B_W22_1.2V" : 79.90360556,
16
    "AF15B_W22_0.0V" : 44.38443415,
17
    "AF15B_W22_2.4V" : 104.1295414,
18
    "AF15B_W22_4.8V" : 108.5,
19
    "AF25B_W22_1.2V" : 79.19905893,
20
    "AF25B_W22_0.0V" : 43.49487644,
21
    "AF25B_W22_2.4V" : 104.9121782,
22
    "AF25B_W22_3.6V" : 118.5515334,
23
    "AF25B_W22_4.8V" : 125.7991292,
24
    "AF10B_W22_1.2V" : 78.24761423,
25
    "AF10B_W22_0.0V" : 42.92999417,
26
    "AF10B_W22_2.4V" : 103.0991327,
27
    "AF10B_W22_3.6V" : 115.96225,
28
    "AF10B_W22_4.8V" : 122.5137794,
29
    "AF15P_W22_1.2V" : 79.84663062,
30
    "AF10P_W22_1.2V" : 80.31095738,
31
    "AF10P_W22_0.0V" : 45.23827032,
32
    "AF10P_W22_2.4V" : 104.6569318,
33
    "AF10P_W22_3.6V" : 117.084588 ,
34
    "AF10P_W22_4.8V" : 122.9757817,
35
    "AF20P_W22_1.2V" : 80.54125157,
36
    "AF20P_W22_0.0V" : 44.40487805,
37
    "AF25P_W22_1.2V" : 79.86636469,
38
    "AF25P_W22_0.0V" : 44.287061  ,
39
    "AF25P_W22_2.4V" : 105.157962 ,
40
    "AF25P_W22_3.6V" : 118.0621447,
41
    "AF25P_W22_4.8V" : 124.3887409,
42
    "AF15P_W22_0.0V" : 44.287061  ,
43
    "AF15P_W22_2.4V" : 105.157962 ,
44
    "AF15P_W22_3.6V" : 118.0621447,
45
    "AF15P_W22_4.8V" : 124.3887409,
46
    "AF20P_W22_4.8V" : 124.3887409,
47
    "AF15P_W13_4.8V" : 49.27785294,
48
    "AF15P_W13_4.8V" : 76.62601626,
49
    "AF15P_W22_1.2V_1.00E+13_IR2.5" : 77.25182031,
50
    "AF15P_W22_1.2V_1.00E+14_IR2.5" : 78.96702965,
51
    "AF15P_W22_1.2V_1.00E+15_IR2.5" : 82.37392738,
52
    "AF15P_W22_0.0V_1.00E+15_IR2.5" : 48.41384382,
53
    "AF15P_W22_2.4V_1.00E+15_IR2.5" : 100.5483839,
54
    "AF15P_W22_3.6V_1.00E+15_IR2.5" : 109.6334685,
55
    "AF15P_W22_4.8V_1.00E+15_IR2.5" : 113.3373915,
56
    "AF15P_W22_0.0V_2.00E+15_IR2.5" : 52.14 ,
57
    "AF15P_W22_1.2V_2.00E+15_IR2.5" : 88.93 ,
58
    "AF15P_W22_2.4V_2.00E+15_IR2.5" : 105.5 ,
59
    "AF15P_W22_3.6V_2.00E+15_IR2.5" : 113.4 ,
60
    "AF15P_W22_4.8V_2.00E+15_IR2.5" : 115.28,
61
    "AF15P_W22_0.0V_5.00E+15_IR2.5" : 54.9  ,
62
    "AF15P_W22_1.2V_5.00E+15_IR2.5" : 92    ,
63
    "AF15P_W22_2.4V_5.00E+15_IR2.5" : 107   ,
64
    "AF15P_W22_3.6V_5.00E+15_IR2.5" : 114   ,
65
    "AF15P_W22_4.8V_5.00E+15_IR2.5" : 118   ,
66
    "AF15P_W22_0.0V_1.00E+13" : 45.12558914,
67
    "AF15P_W22_1.2V_1.00E+13" : 79.60384366,
68
    "AF15P_W22_0.0V_1.00E+14" : 45.39719039,
69
    "AF15P_W22_1.2V_1.00E+14" : 80.45921242,
70
    "AF15P_W22_1.2V_1.00E+15" : 86.93042427,
71
    "AF15P_W22_0.0V_1.00E+15" : 49.47844094,
72
    "AF15P_W22_2.4V_1.00E+15" : 106.4280085,
73
    "AF15P_W22_3.6V_1.00E+15" : 116.6179973,
74
    "AF15P_W22_4.8V_1.00E+15" : 120.8595215,
75
    "AF20P_W22_0.0V_1.00E+13" : 44.21169175,
76
    "AF20P_W22_1.2V_1.00E+13" : 79.55532966,
77
    "AF20P_W22_4.8V_1.00E+13" : 123.341547 ,
78
    "AF20P_W22_0.0V_1.00E+14" : 44.82900886,
79
    "AF20P_W22_1.2V_1.00E+14" : 81.12716741,
80
    "AF20P_W22_4.8V_1.00E+14" : 122.9273761,
81
    "AF10P_W22_0.0V_1.00E+15" : 57.35467596,
82
    "AF10P_W22_1.2V_1.00E+15" : 90.96906659,
83
    "AF10P_W22_4.8V_1.00E+15" : 122.2604183,
84
    "AF10P_W22_0.0V_2.00E+15" : 56.64004329,
85
    "AF10P_W22_1.2V_2.00E+15" : 93.99412366,

    "AF25B_W22_0.0V" : 43.49487644,
    "AF25B_W22_2.4V" : 104.9121782,
    "AF25B_W22_3.6V" : 118.5515334,
    "AF25B_W22_4.8V" : 125.7991292,
    "AF10B_W22_1.2V" : 78.24761423,
    "AF10B_W22_0.0V" : 42.92999417,
    "AF10B_W22_2.4V" : 103.0991327,
    "AF10B_W22_3.6V" : 115.96225,
    "AF10B_W22_4.8V" : 122.5137794,
    "AF15P_W22_1.2V" : 79.84663062,
    "AF10P_W22_1.2V" : 80.31095738,
    "AF10P_W22_0.0V" : 45.23827032,
    "AF10P_W22_2.4V" : 104.6569318,
    "AF10P_W22_3.6V" : 117.084588 ,
    "AF10P_W22_4.8V" : 122.9757817,
    "AF20P_W22_1.2V" : 80.54125157,
    "AF20P_W22_0.0V" : 44.40487805,
    "AF25P_W22_1.2V" : 79.86636469,
    "AF25P_W22_0.0V" : 44.287061  ,
    "AF25P_W22_2.4V" : 105.157962 ,
    "AF25P_W22_3.6V" : 118.0621447,
    "AF25P_W22_4.8V" : 124.3887409,
    "AF15P_W22_0.0V" : 44.287061  ,
    "AF15P_W22_2.4V" : 105.157962 ,
    "AF15P_W22_3.6V" : 118.0621447,
    "AF15P_W22_4.8V" : 124.3887409,
    "AF20P_W22_4.8V" : 124.3887409,
    "AF15P_W13_4.8V" : 49.27785294,
    "AF15P_W13_4.8V" : 76.62601626,
    "AF15P_W22_1.2V_1.00E+13_IR2.5" : 77.25182031,
    "AF15P_W22_1.2V_1.00E+14_IR2.5" : 78.96702965,
    "AF15P_W22_1.2V_1.00E+15_IR2.5" : 82.37392738,
    "AF15P_W22_0.0V_1.00E+15_IR2.5" : 48.41384382,
    "AF15P_W22_2.4V_1.00E+15_IR2.5" : 100.5483839,
    "AF15P_W22_3.6V_1.00E+15_IR2.5" : 109.6334685,
    "AF15P_W22_4.8V_1.00E+15_IR2.5" : 113.3373915,
    "AF15P_W22_0.0V_2.00E+15_IR2.5" : 52.14 ,
    "AF15P_W22_1.2V_2.00E+15_IR2.5" : 88.93 ,
    "AF15P_W22_2.4V_2.00E+15_IR2.5" : 105.5 ,
    "AF15P_W22_3.6V_2.00E+15_IR2.5" : 113.4 ,
    "AF15P_W22_4.8V_2.00E+15_IR2.5" : 115.28,
    "AF15P_W22_0.0V_5.00E+15_IR2.5" : 54.9  ,
    "AF15P_W22_1.2V_5.00E+15_IR2.5" : 92    ,
    "AF15P_W22_2.4V_5.00E+15_IR2.5" : 107   ,
    "AF15P_W22_3.6V_5.00E+15_IR2.5" : 114   ,
    "AF15P_W22_4.8V_5.00E+15_IR2.5" : 118   ,
    "AF15P_W22_0.0V_1.00E+13" : 45.12558914,
    "AF15P_W22_1.2V_1.00E+13" : 79.60384366,
    "AF15P_W22_0.0V_1.00E+14" : 45.39719039,
    "AF15P_W22_1.2V_1.00E+14" : 80.45921242,
    "AF15P_W22_1.2V_1.00E+15" : 86.93042427,
    "AF15P_W22_0.0V_1.00E+15" : 49.47844094,
    "AF15P_W22_2.4V_1.00E+15" : 106.4280085,
    "AF15P_W22_3.6V_1.00E+15" : 116.6179973,
    "AF15P_W22_4.8V_1.00E+15" : 120.8595215,
    "AF20P_W22_0.0V_1.00E+13" : 44.21169175,
    "AF20P_W22_1.2V_1.00E+13" : 79.55532966,
    "AF20P_W22_4.8V_1.00E+13" : 123.341547 ,
    "AF20P_W22_0.0V_1.00E+14" : 44.82900886,
    "AF20P_W22_1.2V_1.00E+14" : 81.12716741,
    "AF20P_W22_4.8V_1.00E+14" : 122.9273761,
    "AF10P_W22_0.0V_1.00E+15" : 57.35467596,
    "AF10P_W22_1.2V_1.00E+15" : 90.96906659,
    "AF10P_W22_4.8V_1.00E+15" : 122.2604183,
    "AF10P_W22_0.0V_2.00E+15" : 56.64004329,
    "AF10P_W22_1.2V_2.00E+15" : 93.99412366,
    "AF10P_W22_4.8V_2.00E+15" : 124.3138632,
    "AF25P_W22_0.0V_1.00E+13" : 45.67136046,
    "AF25P_W22_1.2V_1.00E+13" : 81.46896162,
    "AF25P_W22_0.0V_1.00E+14" : 44.84449066,
    "AF25P_W22_1.2V_1.00E+14" : 80.98899878,
    "AF25P_W22_4.8V_1.00E+14" : 120.4337289,
    "AF25P_W22_0.0V_1.00E+15" : 53.15451571,
    "AF25P_W22_1.2V_1.00E+15" : 90.69691215,
    "AF25P_W22_4.8V_1.00E+15" : 127.613118,
    "AF20P_W22_0.0V_1.00E+15" : 54.41834333, 
    "AF20P_W22_1.2V_1.00E+15" : 92.05930616, 
    "AF20P_W22_4.8V_1.00E+15" : 126.3394924,
    "AF10P_W22_0.0V_5.00E+15" : 100,
    "AF10P_W22_1.2V_5.00E+15" : 100,
    "AF10P_W22_4.8V_5.00E+15" : 100
 
}

from ROOT import TMath




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
