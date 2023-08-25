import matplotlib.pyplot as plt

from matplotlib import rcParams
from cycler import cycler
import matplotlib.style as style
colors = {
    "sky blue":       "#56B4E9",
    "orange":         "#E69F00",
    "bluish green":   "#009E73",
    "reddish purple": "#CC79A7",
    "blue":           "#0072B2",
    "vermillion":     "#D55E00",
    "yellow":         "#F0E442"
}
markers={
    "square":         "s",
    "triangle_down":  "v",
    "circle":         "o",
    "diamond":        "D",
    "hexagon1":       "h",
    "pentagon":       "p",
    "plus":           "P"
}

rcParams['axes.prop_cycle'] = cycler('color', colors.values()) + cycler('marker', markers.values())

# Define the ratios for width and height of subplots
width_ratios = [1, 1, 1, 1]  # Adjust as needed
height_ratios = [0.7, 0.7]      # Adjust as needed

# Create a 3x4 grid of subplots with adjusted sizes
fig, axes = plt.subplots(2, 4, figsize=(12, 9),
                         gridspec_kw={'width_ratios': width_ratios, 'height_ratios': height_ratios})

title_list = [r"Type comparison V$_{sub}$ = -1.2 V",
              r"Irradiation level V$_{sub}$ = -1.2 V",
              r"Irradiation = $10^{15}$",
              "Pitch = 15 \u03BCm"]

data_list = [
    [
        [[10,15,20,25],[98,99,99,100],"P-type"],
        [[15,20,25],[95,96,95],"B-type"],
        [[15],[96],"Standard"]
    ],
    [
        [[10,15,20,25],[99,97,96,95],"Pitch = 15 \u03BCm"],
        [[10,15,20,25],[99,97,97,87],"Pitch = 20 \u03BCm"],
        [[10,15,20,25],[99,98,97,84],"Pitch = 25 \u03BCm"]
    ],
    [
        [[0,1.2,4.8],[86,89,97],"Pitch = 10 \u03BCm"],
        [[0,1.2,4.8],[83,86,95],"Pitch = 15 \u03BCm"],
        [[0,1.2,4.8],[68,78,85],"Pitch = 20 \u03BCm"],
        [[0,1.2,4.8],[56,76,83],"Pitch = 25 \u03BCm"]
    ],
    [
        [[0,1.2,2.4,3.6,4.8],[96,99,99.5,100,99],"P-type"],
        [[0,1.2,2.4,3.6,4.8],[96,98,98,99,99],"B-type"],
        [[0,1.2,2.4,3.6,4.8],[96,97,98,98,99],"Standard"]
    ]
]
# Now you can plot on each subplot
for i in range(2):
    for j in range(4):
        ax = axes[i, j]  # Get the current axis
        for data in data_list[j]:
            ax.plot(data[0],data[1], label = data[2])
        ax.grid()
        if j == 0:
            if i == 0:
                ax.set_ylabel('Detection efficiency (%) \nthr = '+r'3RMS$_{noise}$')  # Set the y-axis label
            else:
                ax.set_ylabel('Detection efficiency (%) \nthr '+r'eff$_{15P 1.2V}$ = 99%')  # Set the y-axis label
        if i == 0:
            ax.set_title(title_list[j])

        if i==1:
            #ax.legend(loc='lower right', bbox_to_anchor=(1,-2), prop={"size": 14})
            if j == 0:
                ax.set_xlabel('Pitch (\u03BCm)')  # Set the y-axis label
            if j == 1:
                ax.set_xlabel(r'NIEL (1 MeV $n_{eq} cm^{-2})$')  # Set the y-axis label
            if j == 2:
                ax.set_xlabel(r'V$_{sub}$ (V)')  # Set the y-axis label
                
            if j == 3:
                ax.set_xlabel(r'V$_{sub}$ (V)')  # Set the y-axis label
        if j > 1:
            ax.set_xlim(-0.1, 4.9)

# Adjust layout spacing
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)  # Adjust the value as needed
# Create a common legend for the bottom row
bottom_axes = axes[1, :]
for ax in bottom_axes:
    bottom_legend = ax.legend(bbox_to_anchor=(0.5, -0.5), loc='lower right')
    ax.add_artist(bottom_legend)

# Show the plot
plt.savefig("eff.png")


# Create a 3x4 grid of subplots with adjusted sizes
fig, axes = plt.subplots(4, 4, figsize=(12, 9))

title_list = [r"Type comparison V$_{sub}$ = -1.2 V",
              r"Irradiation level V$_{sub}$ = -1.2 V",
              r"Irradiation = $10^{15}$",
              "Pitch = 15 \u03BCm"]

data_list = [
    [
        [[10,15,20,25],[96,97,99,98],"P-type"],
        [[15,20,25],[95,96,95],"B-type"],
        [[15],[96],"Standard"]
    ],
    [
        [[10,15,20,25],[96,97,99,98],"Pitch = 15 \u03BCm"],
        [[10,15,20,25],[96,97,99,98],"Pitch = 20 \u03BCm"],
        [[10,15,20,25],[96,97,99,98],"Pitch = 25 \u03BCm"]
    ],
    [
        [[0,1.2,4.8],[96,97,98],"Pitch = 10 \u03BCm"],
        [[0,1.2,4.8],[96,97,98],"Pitch = 15 \u03BCm"],
        [[0,1.2,4.8],[95,96,99],"Pitch = 20 \u03BCm"],
        [[0,1.2,4.8],[96,97,98],"Pitch = 25 \u03BCm"]
    ],
    [
        [[0,1.2,2.4,3.6,4.8],[96,97,99,99,99],"P-type"],
        [[0,1.2,2.4,3.6,4.8],[96,98,98,99,99],"B-type"],
        [[0,1.2,2.4,3.6,4.8],[96,97,98,98,99],"Standard"]
    ]
]
# Now you can plot on each subplot
for i in range(4):
    for j in range(4):
        ax = axes[i, j]  # Get the current axis
        for data in data_list[j]:
            ax.plot(data[0],data[1], label = data[2])
        ax.grid()
        if j == 0:
            if i == 0:
                ax.set_ylabel('Spatial resolution (\u03BCm) \n thr = '+r'3RMS$_{noise}$')  # Set the y-axis label
            if i == 1:
                ax.set_ylabel('Spatial resolution (\u03BCm) \n thr '+r'eff$_{15P 1.2V}$ = 99%')  # Set the y-axis label
            if i == 2:
                ax.set_ylabel('Average cluster size \n thr '+r'eff$_{15P 1.2V}$ = 99%')  # Set the y-axis label
            if i == 3:
                ax.set_ylabel('Average cluster size \n thr '+r'eff$_{15P 1.2V}$ = 99%')  # Set the y-axis label
        if i == 0:
            ax.set_title(title_list[j])

        if i==3:
            #ax.legend(loc='lower right', bbox_to_anchor=(1,-2), prop={"size": 14})
            if j == 0:
                ax.set_xlabel('Pitch (\u03BCm)')  # Set the y-axis label
            if j == 1:
                ax.set_xlabel(r'NIEL (1 MeV $n_{eq} cm^{-2})$')  # Set the y-axis label
            if j == 2:
                ax.set_xlabel(r'V$_{sub}$ (V)')  # Set the y-axis label
                
            if j == 3:
                ax.set_xlabel(r'V$_{sub}$ (V)')  # Set the y-axis label
        if j > 1:
            ax.set_xlim(-0.1, 4.9)

# Adjust layout spacing
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)  # Adjust the value as needed
# Create a common legend for the bottom row
bottom_axes = axes[3, :]
for ax in bottom_axes:
    bottom_legend = ax.legend(bbox_to_anchor=(0.5, -0.5), loc='lower right')
    ax.add_artist(bottom_legend)

# Show the plot
plt.savefig("res.png")