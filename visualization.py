import matplotlib.pyplot as plt
import pandas as pd

from usikkerhedsbudget import usikkerhedsbudget
from SQL_functions import Read_SQL
from plot_vinkeldrej import make_angular_plot

error_degrees = 2
resolution = 0.001

try:
    data = Read_SQL.get_SQL("*", "w_vinkeldrej_test", "task_number = ''")
except:
    file_path = r"C:\Users\AY\Desktop\recovery_hjemme.txt"
    data = pd.read_csv(file_path)


#visual = make_angular_plot.fit_data(data)

##################### circular ##################### 

fig = {direction: None for direction in set(data['direction'])}
ax = {direction: None for direction in set(data['direction'])}
for direction in set(data['direction']):
    fig[direction], ax[direction] = make_angular_plot.scatter_plot(data, direction)

    make_angular_plot.add_lines(ax[direction], data, direction)

    # Set theta ticks to show degree values
    make_angular_plot.add_labels(ax[direction])

    # Add a legend for 'cw' direction grouped by "mn" outside the graph
    make_angular_plot.add_legend(ax[direction])

##################### non_circular ##################### 

fig_non_circular = {direction: None for direction in set(data['direction'])}
ax_non_circular = {direction: None for direction in set(data['direction'])}
for direction in set(data['direction']):

    directional_data = data.loc[(data["direction"] == direction) & (data["rising_or_falling"].str.strip() != 'None')]

    colors = {direction: {mn: plt.cm.tab20(mn) for mn in set(directional_data['measurement_number'])}} # Generate colors for each "mn" value

    fig_non_circular[direction], ax_non_circular[direction] = plt.subplots(num=f"{direction}_non_circular")

    ax_non_circular[direction] = make_angular_plot.plot_for_measurement_number(ax_non_circular[direction], directional_data, colors[direction])

    # Calculate the viewable range
    max_y, min_y = make_angular_plot.set_view(pd.to_numeric(directional_data['measured_value']) - pd.to_numeric(directional_data['attempted_value']), error_degrees)

    # Plot the error lines
    ax_non_circular[direction] = make_angular_plot.error_lines(ax_non_circular[direction], direction, error_degrees)

    # Set the viewable range and labels
    ax_non_circular[direction] = make_angular_plot.viewable_rang_and_labels(ax_non_circular, direction, min_y*1.1, max_y*1.1)

##################### usikkerhedsbudget ##################### 

# Calculate the standard deviation for each analytical value
std_dev_dict = usikkerhedsbudget.standart_afvigelse(data) #stabdard afvigelse per analytisk punkt
max_deviation = max(std_dev_dict.values())

N_value = {}
N = {}
L_value = {}
L = {}
J_value = {}
J = {}
M_value = {}
M = {}

for direction in set(data['direction']):
    (N[direction],
    L[direction],
    J[direction], 
    M[direction], 
    N_value[direction], 
    L_value[direction], 
    J_value[direction], 
    M_value[direction]) = usikkerhedsbudget.get_N_L_M_J(data, direction) #J skal retted så den ikke går tilbage til udgangspunkt

    usikkerhed = usikkerhedsbudget.usikkerheder(L_value[direction], M[direction], M_value[direction], N_value[direction], J_value[direction], direction, data)

#average_for_direction, average_for_each_series, average_udgangspunkt = usikkerhedsbudget.get_average(visual, L, M, J)

resolution_uncertainty = usikkerhedsbudget.get_res_uncertainty(resolution)

plt.show()