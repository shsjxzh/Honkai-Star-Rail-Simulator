import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Speed ranges
min_puller_speed = 99 + 10
max_puller_speed = 195 + 10

min_runner_speed = 169 + 11
max_runner_speed = 265 + 11

# Load data
df = pd.read_csv('round_table_with_full_time_other.csv', index_col=0)
df = df.reset_index(drop=True)
round_table = df.to_numpy()

# Create labels for the heatmap
puller_speeds = np.arange(min_puller_speed, max_puller_speed + 1)
runner_speeds = np.arange(min_runner_speed, max_runner_speed + 1)

# Convert to DataFrame with proper labels
heatmap_df = pd.DataFrame(
    round_table,
    index=puller_speeds,
    columns=runner_speeds
)

# # Create custom blue colormap using part of the spectrum
# blues_cmap = plt.cm.Blues
# # Use only the range from 0.2 to 0.9 of the Blues colormap (avoiding too light/dark extremes)
# colors = blues_cmap(np.linspace(0.2, 0.9, 256))
# custom_blue_cmap = LinearSegmentedColormap.from_list('custom_blues', colors)

# Create the plot
fig, ax = plt.subplots(figsize=(5, 5))

# Create seaborn heatmap
sns.heatmap(
    heatmap_df,
    cmap="viridis",       # Custom blue colormap with partial spectrum
    cbar_kws={'label': 'Turns (t)'},
    ax=ax,
    xticklabels=10,          # Show every 10th x-tick
    yticklabels=10           # Show every 10th y-tick
)

ax.set_xlabel('Firefly\'s speed')
ax.set_ylabel('Bronya\'s speed')
ax.set_title('Turns heatmap across speeds')

# Invert y-axis to match your original (smallest speeds at bottom)
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("plot.png", dpi=300, format="png")
plt.show()