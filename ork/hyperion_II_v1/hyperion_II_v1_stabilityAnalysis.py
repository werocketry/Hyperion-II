# stabilityAnalysis.py

import os
import numpy as np
import matplotlib.pyplot as plt

import orlab
from orlab import FlightDataType


def stability_analysis():
    # Define the plots directory
    plots_dir = os.path.join("ork", "hyperion_II_v1", "plots", "stability_analysis")
    os.makedirs(plots_dir, exist_ok=True)

    # Define the key info file path
    key_info_file_path = os.path.join(plots_dir, "stability_analysis.txt")

    with orlab.OpenRocketInstance() as instance:
        orl = orlab.Helper(instance)

        # Load the document and get the simulation
        ork_file = os.path.join("ork", "hyperion_II_v1", "hyperion_II_v1.ork")
        if not os.path.exists(ork_file):
            print(f"The .ork file was not found at path: {ork_file}")
            return

        try:
            doc = orl.load_doc(ork_file)
            sim = doc.getSimulation(0)
            print(f"Loaded rocket model from '{ork_file}'.\n")
        except Exception as e:
            print(f"Failed to load the .ork file: {e}")
            return

        # Run the simulation
        try:
            orl.run_simulation(sim)
            print("Simulation run successful.\n")
        except Exception as e:
            print(f"Simulation failed: {e}")
            return

        # Retrieve flight data
        try:
            data = orl.get_timeseries(
                sim,
                [
                    FlightDataType.TYPE_TIME,
                    FlightDataType.TYPE_STABILITY,
                    FlightDataType.TYPE_CG_LOCATION,
                    FlightDataType.TYPE_CP_LOCATION,
                    FlightDataType.TYPE_MACH_NUMBER,
                ],
            )
            print("Flight data retrieved successfully.\n")
        except Exception as e:
            print(f"Failed to retrieve flight data: {e}")
            return

        # Open the key info file for writing
        with open(key_info_file_path, "w") as f:
            # Write some initial info
            f.write(f"Loaded rocket model from '{ork_file}'.\n\n")
            f.write("Simulation run successful.\n\n")
            # Plot stability over time with dual y-axes
            try:
                time = data[FlightDataType.TYPE_TIME]
                stability_margin = data[FlightDataType.TYPE_STABILITY]
                mach_number = data[FlightDataType.TYPE_MACH_NUMBER]

                fig, ax1 = plt.subplots(figsize=(10, 6))

                ax1.plot(
                    time, stability_margin, "b-", label="Stability Margin (calibers)"
                )
                ax1.set_xlabel("Time (s)")
                ax1.set_ylabel("Stability Margin (calibers)", color="b")
                ax1.tick_params("y", colors="b")
                ax1.grid(True)

                ax2 = ax1.twinx()
                ax2.plot(time, mach_number, "r-", label="Mach Number")
                ax2.set_ylabel("Mach Number", color="r")
                ax2.tick_params("y", colors="r")

                plt.title("Stability Margin and Mach Number over Time")
                fig.legend(loc="upper right", bbox_to_anchor=(0.85, 0.85))
                plt.tight_layout()

                plot_path = os.path.join(plots_dir, "stability_margin_mach_number.png")
                plt.savefig(plot_path)
                plt.close()
                print(f"Saved plot: {plot_path}")
                f.write(f"Saved plot: {plot_path}\n")
            except Exception as e:
                print(f"Error during dual y-axis plotting: {e}")
                f.write(f"Error during dual y-axis plotting: {e}\n")

            # Enhanced Scatter Plot: Stability Margin vs Mach Number with Time Coloring
            try:
                plt.figure(figsize=(10, 6))
                scatter = plt.scatter(
                    mach_number, stability_margin, c=time, cmap="viridis", alpha=0.7
                )
                plt.xlabel("Mach Number")
                plt.ylabel("Stability Margin (calibers)")
                plt.title("Stability Margin vs Mach Number Colored by Time")
                plt.colorbar(scatter, label="Time (s)")
                plt.grid(True)
                plt.tight_layout()

                scatter_plot_path = os.path.join(
                    plots_dir, "stability_margin_vs_mach_number_colored.png"
                )
                plt.savefig(scatter_plot_path)
                plt.close()
                print(f"Saved plot: {scatter_plot_path}")
                f.write(f"Saved plot: {scatter_plot_path}\n")
            except Exception as e:
                print(f"Error during scatter plot with color: {e}")
                f.write(f"Error during scatter plot with color: {e}\n")

            # Additional Useful Information: Average Stability Margin
            try:
                avg_stability = np.nanmean(stability_margin)
                print(f"Average Stability Margin: {avg_stability:.2f} calibers.")
                f.write(f"Average Stability Margin: {avg_stability:.2f} calibers.\n")
            except Exception as e:
                print(f"Error calculating average stability margin: {e}")
                f.write(f"Error calculating average stability margin: {e}\n")

            # Log extrema for Stability Margin and Mach Number
            try:
                f.write("\nExtrema Information:\n\n")
                # Stability Margin
                max_stability = np.nanmax(stability_margin)
                min_stability = np.nanmin(stability_margin)
                time_max_stability = time[np.nanargmax(stability_margin)]
                time_min_stability = time[np.nanargmin(stability_margin)]
                f.write(f"Stability Margin:\n")
                f.write(
                    f"  Max Value: {max_stability:.2f} at Time: {time_max_stability:.2f} s\n"
                )
                f.write(
                    f"  Min Value: {min_stability:.2f} at Time: {time_min_stability:.2f} s\n\n"
                )

                # Mach Number
                max_mach = np.nanmax(mach_number)
                min_mach = np.nanmin(mach_number)
                time_max_mach = time[np.nanargmax(mach_number)]
                time_min_mach = time[np.nanargmin(mach_number)]
                f.write(f"Mach Number:\n")
                f.write(f"  Max Value: {max_mach:.2f} at Time: {time_max_mach:.2f} s\n")
                f.write(
                    f"  Min Value: {min_mach:.2f} at Time: {time_min_mach:.2f} s\n\n"
                )
            except Exception as e:
                print(f"Error calculating extrema: {e}")
                f.write(f"Error calculating extrema: {e}\n")


if __name__ == "__main__":
    stability_analysis()
