import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class make_angular_plot():
    @staticmethod
    def fit_data(data):

        # Group by 'udgangspunkt', 'direction', 'measurement_number', and 'rising_or_falling'
        grouped_data = data.groupby(['udgangspunkt', 'direction', 'measurement_number', 'rising_or_falling'])

        # Initialize the "visual" dictionary
        visual = {}

        # Loop through the groups and create the nested dictionaries
        for (udgangspunkt, direction, measurement_number, rising_or_falling), group_df in grouped_data:
            if udgangspunkt not in visual:
                visual[udgangspunkt] = {}
            if direction not in visual[udgangspunkt]:
                visual[udgangspunkt][direction] = {}
            if measurement_number not in visual[udgangspunkt][direction]:
                visual[udgangspunkt][direction][measurement_number] = {}

            # Convert the group data into a list of [analytical_value, attempted_value, measured_value]
            values_list = group_df[['analytical_value', 'attempted_value', 'measured_value']].values.tolist()

            # Add the values_list to the 'rising_or_falling' dictionary
            visual[udgangspunkt][direction][measurement_number][rising_or_falling] = values_list

        return visual

    @staticmethod
    def scatter_plot(data, rotation):
        fig, ax = plt.subplots(num=rotation, subplot_kw={'projection': 'polar'})

        for a in set(data['measurement_number']):
            directional_data = data.loc[(data["direction"] == rotation) & (data["rising_or_falling"].str.strip() != 'None') & (data["measurement_number"] == a)]

        # Plot the markers for 'cw' direction
            ax.scatter(np.deg2rad(directional_data['attempted_value'].astype(float)), directional_data['measurement_number'], marker='.', label=f"Measurement Number: {set(directional_data['measurement_number'])}")

        return [fig, ax]

    @staticmethod
    def add_lines(ax, data, direction):
        ax.grid(axis = 'y')
        directional_data = data.loc[(data["direction"] == direction) & (data["rising_or_falling"].str.strip() != 'None')]

        for lines in set(directional_data['analytical_value'].astype(float)):
            ax.plot([np.deg2rad(lines), np.deg2rad(lines)], [0, max(directional_data['measurement_number'])], color='red', linestyle='-', linewidth=0.1)

        for radius in set(directional_data['measurement_number']):
            ax.plot(np.deg2rad(np.linspace(0,360,1000)), [radius for _ in range(1000)], color='grey', linestyle='--', linewidth=0.3)

    @staticmethod
    def add_labels(ax):
        ax.set_yticklabels([])

    @staticmethod
    def add_legend(ax):
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = list(set(labels))
        unique_handles = []
        for label in unique_labels:
            handle = handles[labels.index(label)]
            unique_handles.append(handle)
        ax.legend(unique_handles, unique_labels, bbox_to_anchor=(1.05, 1), loc='upper left')

    @staticmethod
    def set_x_y(data, figure):
        y_values = pd.to_numeric(data['measured_value']) - pd.to_numeric(data['attempted_value'])
        x_values = data['analytical_value']
        #x_values = data[data['direction'] == figure]['analytical_value'].astype(float) # ser analytical som float
        #x_values = data[data['direction'] == figure]['analytical_value'].astype(float).abs() # ser analytical som float og alle værdier er positive

        return [x_values, y_values]
    
    @staticmethod
    def plot_for_measurement_number(ax_non_circular, data, colors):

        for mn in set(data['measurement_number']):

            data_mn = data.loc[(data["measurement_number"] == mn)]

            ax_non_circular.scatter(data_mn['analytical_value'].astype(str), pd.to_numeric(data_mn['measured_value']) - pd.to_numeric(data_mn['attempted_value']), marker='.', color=colors[mn])
        
        return ax_non_circular
    
    @staticmethod
    def set_view(y_values, error_degrees):
        min_y = min(min(y_values),  -error_degrees)
        max_y = max(max(y_values), error_degrees)

        return [max_y, min_y]
    
    @staticmethod
    def error_lines(ax_non_circular, direction, error_degrees):
        ax_non_circular.axhline(y=error_degrees, color='red', linestyle='--')
        ax_non_circular.axhline(y=-error_degrees, color='red', linestyle='--')

        return ax_non_circular

    @staticmethod
    def viewable_rang_and_labels(ax_non_circular, direction, min_y, max_y):
        ax_non_circular[direction].set_ylim(min_y, max_y)

        # Set x-axis label
        ax_non_circular[direction].set_xlabel('Nominiel data')

        # Set y-axis label
        ax_non_circular[direction].set_ylabel('DUT - REF')

        return ax_non_circular