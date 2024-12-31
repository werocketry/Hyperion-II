# multiPlot.py

import os
import numpy as np
import matplotlib.pyplot as plt

import orlab
from orlab import FlightDataType, FlightEvent


def log_extrema(file_handle, data_x, data_y, title):
    """Write the extrema (max and min) for a given dataset to a file."""
    max_value = np.max(data_y)
    min_value = np.min(data_y)
    max_time = data_x[np.argmax(data_y)]
    min_time = data_x[np.argmin(data_y)]
    file_handle.write(f"{title}:\n")
    file_handle.write(f"  Max Value: {max_value:.2f} at Time: {max_time:.2f} s\n")
    file_handle.write(f"  Min Value: {min_value:.2f} at Time: {min_time:.2f} s\n\n")


def multi_plot_analysis():

    # 0. Set the path to the.ork file
    version = input("Enter the version number (e.g., 2 for v2): ")
    ork_file = os.path.join("ork", f"hyperion_II_v{version}.ork")
    print(f".ork file path set to: {ork_file}")

    # 1. Set up directories
    plots_dir = os.path.join("ork", f"outputs-v{version}")
    os.makedirs(plots_dir, exist_ok=True)
    print(f"[INFO] Plots directory set to: {plots_dir}")

    # Define the key info file path
    key_info_file_path = os.path.join(plots_dir, "multi_plot_analysis.txt")

    # Define the subfolder for individual plots
    individual_plots_dir = os.path.join(plots_dir, "multi_plots")
    os.makedirs(individual_plots_dir, exist_ok=True)

    with orlab.OpenRocketInstance() as instance:
        orl = orlab.Helper(instance)

        if not os.path.exists(ork_file):
            print(f"The.ork file was not found at path: {ork_file}")
            return

        try:
            doc = orl.load_doc(ork_file)
            sim = doc.getSimulation(0)
            print(f"Loaded rocket model from '{ork_file}'.\n")
        except Exception as e:
            print(f"Failed to load the.ork file: {e}")
            return

        # Run the simulation
        try:
            orl.run_simulation(sim)
            print("Simulation run successful.\n")
        except Exception as e:
            print(f"Simulation failed: {e}")
            return

        # Retrieve multiple flight data types
        try:
            data = orl.get_timeseries(
                sim,
                [
                    FlightDataType.TYPE_TIME,
                    FlightDataType.TYPE_ALTITUDE,
                    FlightDataType.TYPE_VELOCITY_TOTAL,
                    FlightDataType.TYPE_ACCELERATION_TOTAL,
                    FlightDataType.TYPE_THRUST_FORCE,
                    FlightDataType.TYPE_DRAG_FORCE,
                    FlightDataType.TYPE_MASS,
                    FlightDataType.TYPE_MACH_NUMBER,
                    FlightDataType.TYPE_AOA,  # Angle of Attack
                    FlightDataType.TYPE_CG_LOCATION,
                    FlightDataType.TYPE_CP_LOCATION,
                ],
            )
            events = orl.get_events(sim)
            print("Flight data and events retrieved successfully.\n")
        except Exception as e:
            print(f"Failed to retrieve flight data and events: {e}")
            return

        # Open the key info file for writing
        with open(key_info_file_path, "w") as f:
            # Write some initial info
            f.write(f"Loaded rocket model from '{ork_file}'.\n\n")
            f.write("Simulation run successful.\n\n")
            # Define plot configurations
            plot_configs = [
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_ALTITUDE],
                    "xlabel": "Time (s)",
                    "ylabel": "Altitude (m)",
                    "title": "Altitude vs Time",
                    "color": "b-",
                    "filename": "altitude_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_VELOCITY_TOTAL],
                    "xlabel": "Time (s)",
                    "ylabel": "Velocity (m/s)",
                    "title": "Total Velocity vs Time",
                    "color": "r-",
                    "filename": "velocity_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_ACCELERATION_TOTAL],
                    "xlabel": "Time (s)",
                    "ylabel": "Acceleration (m/s²)",
                    "title": "Total Acceleration vs Time",
                    "color": "g-",
                    "filename": "acceleration_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_THRUST_FORCE],
                    "xlabel": "Time (s)",
                    "ylabel": "Thrust Force (N)",
                    "title": "Thrust Force vs Time",
                    "color": "m-",
                    "filename": "thrust_force_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_DRAG_FORCE],
                    "xlabel": "Time (s)",
                    "ylabel": "Drag Force (N)",
                    "title": "Drag Force vs Time",
                    "color": "c-",
                    "filename": "drag_force_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_MASS],
                    "xlabel": "Time (s)",
                    "ylabel": "Mass (kg)",
                    "title": "Mass vs Time",
                    "color": "k-",
                    "filename": "mass_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_MACH_NUMBER],
                    "xlabel": "Time (s)",
                    "ylabel": "Mach Number",
                    "title": "Mach Number vs Time",
                    "color": "b-",
                    "filename": "mach_number_vs_time.png",
                },
                {
                    "data_x": data[FlightDataType.TYPE_TIME],
                    "data_y": data[FlightDataType.TYPE_AOA],
                    "xlabel": "Time (s)",
                    "ylabel": "Angle of Attack (deg)",
                    "title": "Angle of Attack vs Time",
                    "color": "r-",
                    "filename": "angle_of_attack_vs_time.png",
                },
            ]

            # Plot and save each configuration separately
            for config in plot_configs:
                try:
                    plt.figure(figsize=(10, 6))
                    plt.plot(
                        config["data_x"],
                        config["data_y"],
                        config["color"],
                        label=config.get("label", ""),
                    )
                    plt.xlabel(config["xlabel"])
                    plt.ylabel(config["ylabel"])
                    plt.title(config["title"])
                    plt.grid(True)
                    if "label" in config and config["label"]:
                        plt.legend()

                    # Annotate events
                    index_at = lambda t: (
                        np.abs(data[FlightDataType.TYPE_TIME] - t)
                    ).argmin()
                    for event, times in events.items():
                        event_name = event.name.replace("_", " ").title()
                        for time in times:
                            if event_name == "Apogee" or event_name == "Launchrod":
                                plt.annotate(
                                    event_name,
                                    xy=(
                                        time,
                                        data[FlightDataType.TYPE_ALTITUDE][
                                            index_at(time)
                                        ],
                                    ),
                                    xycoords="data",
                                    xytext=(20, 10),
                                    textcoords="offset points",
                                    arrowprops=dict(
                                        arrowstyle="->", connectionstyle="arc3"
                                    ),
                                )
                            else:
                                plt.annotate(
                                    event_name,
                                    xy=(time, config["data_y"][index_at(time)]),
                                    xycoords="data",
                                    xytext=(20, 10),
                                    textcoords="offset points",
                                    arrowprops=dict(
                                        arrowstyle="->", connectionstyle="arc3"
                                    ),
                                )

                    plt.tight_layout()
                    plot_path = os.path.join(individual_plots_dir, config["filename"])
                    plt.savefig(plot_path)
                    plt.close()
                    print(f"Saved plot: {plot_path}")
                    f.write(f"Saved plot: {plot_path}\n")
                    # Log extrema
                    log_extrema(f, config["data_x"], config["data_y"], config["title"])
                except Exception as e:
                    print(f"Failed to plot {config['title']}: {e}")
                    f.write(f"Failed to plot {config['title']}: {e}\n")


if __name__ == "__main__":
    multi_plot_analysis()
