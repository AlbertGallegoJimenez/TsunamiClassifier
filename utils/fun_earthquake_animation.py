import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import geopandas as gpd
from matplotlib.animation import FuncAnimation
import cartopy.feature as cfeature
import utils.matplotlib_config
# Get the palette
palette = plt.rcParams['axes.prop_cycle'].by_key()['color']
purple_PCM = palette[0]
golden_PCM = palette[1]

def create_earthquake_animation(gdf):
    gdf["year"] = gdf["date"].dt.year

    # Sort the data by year
    gdf = gdf.sort_values('year')
    years = gdf['year'].unique()
    # Create custom marker sizes based on the magnitude
    min_size, max_size = 10, 150
    gdf['size'] = np.interp(gdf['Mw'], (gdf['Mw'].min(), gdf['Mw'].max()), (min_size, max_size))

    fig, (ax_map, ax_bar) = plt.subplots(1, 2,
                                         gridspec_kw={'width_ratios': [3, 0.35]},
                                         subplot_kw={'projection': ccrs.PlateCarree() if 'ax_map' else None},
                                         figsize=(12, 5.5),
                                         tight_layout=True)

    ax_map.stock_img()
    ax_map.coastlines(resolution='50m', linewidth=.5, color="white")

    # Create an update function for the animation
    def update(frame):
        ax_map.clear(), ax_bar.clear()
        ax_map.stock_img()
        ax_map.coastlines(resolution='50m', linewidth=.5, color="white")
        #ax.gridlines(draw_labels=True)
        ax_map.set_extent([-180, 180, -90, 90], ccrs.PlateCarree())

        # Filter events up to the current year in the frame
        current_data = gdf[gdf['year'] <= frame]

        # Separate tsunami and non-tsunami data
        no_tsunami = current_data[current_data['tsunami'] == 0]
        tsunami = current_data[current_data['tsunami'] == 1]

        # Plot non-tsunami events
        ax_map.scatter(
            no_tsunami.geometry.x, no_tsunami.geometry.y,
            s=no_tsunami['size'],  # Custom sizes
            color=purple_PCM, alpha=0.5, label="No tsunami",
            transform=ccrs.PlateCarree(), zorder=20
        )

        # Plot tsunami events
        ax_map.scatter(
            tsunami.geometry.x, tsunami.geometry.y,
            s=tsunami['size'],  # Custom sizes
            color=golden_PCM, alpha=0.5, label="Tsunami",
            transform=ccrs.PlateCarree(), zorder=20
        )

        # Title with the current year
        ax_map.set_title(f"Earthquakes up to Year {frame} (N={len(current_data)})", fontsize=18, weight='bold')

        # Plot a stacked bar plot
        df_count = current_data['tsunami'].value_counts(normalize=True).rename(index={0: 'No tsunami', 1: 'Tsunami'}).to_frame()
        ax_bar.bar(0, df_count.loc["No tsunami"], color=purple_PCM, label='No tsunami', width=0.211)
        ax_bar.bar(0, df_count.loc["Tsunami"], bottom=df_count.loc["No tsunami"], color=golden_PCM, label='Tsunami', width=0.211)
        # Add annotations to the bar plot at the middle of each bar
        for i, (index, row) in enumerate(df_count.iterrows()):
            ax_bar.text(0, row[0] / 2 + df_count.iloc[:i].sum()[0], f'{row[0]:.1%}',
                        ha='center', va='center', color='white', weight='bold', fontsize=14)
            # Add the label to the right of the bar plot at the same y position
            ax_bar.text(0.12, row[0] / 2 + df_count.iloc[:i].sum()[0], index,
                        ha='left', va='center', color=purple_PCM if i == 0 else golden_PCM, weight='bold', fontsize=14)
        ax_bar.set_ylim(0, 1)
        ax_bar.axis('off')

    # Create the animation
    ani = FuncAnimation(fig, update, frames=years, repeat=False)

    # Save the animation
    ani.save('images/earthquakes_animation.gif', fps=7, dpi=200)