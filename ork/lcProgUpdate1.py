# lcProgUpdate1.py

import os
import numpy as np
import matplotlib.pyplot as plt

import orlab
from orlab import FlightDataType, FlightEvent


def setup_directories():
    """
    Create and return the directories for storing plots and text outputs.
    Returns:
        plots_dir (str): Path to main output directory.
        key_info_file_path (str): Path to the .txt file for key info.
        individual_plots_dir (str): Path to store individual plot images.
    """

    # 0. Set the path to the .ork file
    version = input("Enter the version number (e.g., 2 for v2): ")
    ork_file = os.path.join("ork", f"hyperion_II_v{version}.ork")
    print(f".ork file path set to: {ork_file}")

    # 1. Set up directories
    plots_dir = os.path.join("ork", f"outputs-v{version}")
    os.makedirs(plots_dir, exist_ok=True)
    print(f"[INFO] Plots directory set to: {plots_dir}")

    key_info_file_path = os.path.join(plots_dir, f"lcProgUpdate1_v{version}.txt")

    individual_plots_dir = os.path.join(plots_dir, "plots-lcProgUpdate1")
    os.makedirs(individual_plots_dir, exist_ok=True)
    print(f"[INFO] Individual plots directory set to: {individual_plots_dir}")

    return ork_file, plots_dir, key_info_file_path, individual_plots_dir


def load_and_run_simulation(helper, ork_file):
    """
    Load the .ork file, retrieve the first simulation, run it, and return the simulation object.
    Args:
        helper (Helper): orlab.Helper instance.
        ork_file (str): Path to the .ork file.
    Returns:
        sim (Simulation or None): OpenRocket simulation object if successful, else None.
    """
    if not os.path.exists(ork_file):
        print(f"[ERROR] The .ork file was not found at path: {ork_file}")
        return None

    print(f"[INFO] Found .ork file at path: {ork_file}")
    try:
        doc = helper.load_doc(ork_file)
        sim = doc.getSimulation(0)
        print(f"[INFO] Loaded rocket model from '{ork_file}'.\n")
    except Exception as e:
        print(f"[ERROR] Failed to load the .ork file: {e}")
        return None

    # Run the simulation
    try:
        helper.run_simulation(sim)
        print("[INFO] Simulation run successful.\n")
    except Exception as e:
        print(f"[ERROR] Simulation failed: {e}")
        return None

    return sim


def retrieve_data_and_events(helper, sim):
    """
    Retrieve timeseries data and flight events from the simulation.
    Args:
        helper (Helper): orlab.Helper instance.
        sim (Simulation): OpenRocket simulation object.
    Returns:
        data (dict): Dictionary of flight data arrays.
        events (dict): Dictionary of flight events to times.
    """
    # Retrieve multiple flight data types
    try:
        data = helper.get_timeseries(
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
        print("[INFO] Flight data retrieved successfully.\n")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve flight data: {e}")
        return None, None

    # Retrieve flight events
    try:
        events = helper.get_events(sim)
        print("[INFO] Flight events retrieved successfully.\n")
        if events:
            print("[DEBUG] All Flight Events:")
            for evt, times in events.items():
                print(f"       {evt.name}: {times}")
        else:
            print("[DEBUG] No flight events were found in the simulation.")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve flight events: {e}")
        return None, None

    return data, events


def validate_data(data, file_handle):
    """
    Check if all required data arrays are present and return a boolean indicating validity.
    Args:
        data (dict): Dictionary of flight data arrays.
        file_handle: File handle to which we write any errors or messages.
    Returns:
        bool: True if data is valid, False otherwise.
    """
    # 9. Extract relevant data
    required_data = {
        "time": FlightDataType.TYPE_TIME,
        "altitude": FlightDataType.TYPE_ALTITUDE,
        "velocity_total": FlightDataType.TYPE_VELOCITY_TOTAL,
        "acceleration_total": FlightDataType.TYPE_ACCELERATION_TOTAL,
        "thrust_force": FlightDataType.TYPE_THRUST_FORCE,
        "drag_force": FlightDataType.TYPE_DRAG_FORCE,
        "mass": FlightDataType.TYPE_MASS,
        "mach_number": FlightDataType.TYPE_MACH_NUMBER,
        "aoa": FlightDataType.TYPE_AOA,
        "cg_location": FlightDataType.TYPE_CG_LOCATION,
        "cp_location": FlightDataType.TYPE_CP_LOCATION,
    }

    missing_data = []
    for name, ftype in required_data.items():
        if data.get(ftype) is None:
            missing_data.append(name)

    if missing_data:
        msg = "[ERROR] Some flight data types are missing: " + ", ".join(missing_data)
        print(msg)
        file_handle.write(msg + "\n\n")
        return False
    else:
        all_data_msg = "[INFO] All required flight data types are present."
        print(all_data_msg)
        file_handle.write(all_data_msg + "\n\n")
        return True


def compute_and_write_key_info(data, events, file_handle):
    """
    Compute and write the key information (average engine thrust, rail exit velocity,
    descent velocity, ground hit velocity, and average velocity between drogue and main deployment) to file.
    Args:
        data (dict): Dictionary of flight data arrays.
        events (dict): Dictionary of flight events.
        file_handle: File handle for writing key results.
    """
    time = data[FlightDataType.TYPE_TIME]
    altitude = data[FlightDataType.TYPE_ALTITUDE]
    velocity_total = data[FlightDataType.TYPE_VELOCITY_TOTAL]
    thrust_force = data[FlightDataType.TYPE_THRUST_FORCE]

    # Convert thrust to lbf (imperial)
    thrust_force_lbf = thrust_force * 0.224809

    # Convert velocity to ft/s (imperial)
    velocity_ft_s = velocity_total * 3.28084

    # 1. Average Engine Thrust while on the Rail (N and lbf)
    file_handle.write(
        "1. Estimated Average Engine Thrust while on the Rail or Launch Tower:\n"
    )
    liftoff_times = events.get(FlightEvent.LIFTOFF, [])
    if liftoff_times:
        liftoff_time = min(liftoff_times)
        file_handle.write(f"   Liftoff Time: {liftoff_time:.2f} s\n")
        on_rail_mask = time <= liftoff_time
        on_rail_thrust = thrust_force[on_rail_mask]
        if len(on_rail_thrust) > 0:
            avg_thrust_N = np.mean(on_rail_thrust)
            avg_thrust_lbf = avg_thrust_N * 0.224809

            file_handle.write(
                f"   - Average Thrust: {avg_thrust_N:.2f} N ({avg_thrust_lbf:.2f} lbf)\n"
            )
            file_handle.write("   - Calculation Details:\n")
            file_handle.write(
                f"     - Total Thrust during on-rail phase: {np.sum(on_rail_thrust):.2f} N\n"
            )
            file_handle.write(
                f"     - Duration of on-rail phase: {liftoff_time:.2f} s\n"
            )
            file_handle.write(
                f"     - Number of thrust data points: {len(on_rail_thrust)}\n\n"
            )
        else:
            file_handle.write("   - No thrust data available during on-rail phase.\n\n")
    else:
        file_handle.write("   - LIFTOFF event not found in simulation.\n\n")

    # 2. Rail Exit Velocity [ft/s]
    file_handle.write("2. Rail Exit Velocity [ft/s]:\n")
    launchrod_times = events.get(FlightEvent.LAUNCHROD, [])
    if launchrod_times:
        rail_exit_time = min(launchrod_times)
        file_handle.write(f"   Rail Exit Time: {rail_exit_time:.2f} s\n")
        idx_rail_exit = np.argmin(np.abs(time - rail_exit_time))
        if 0 <= idx_rail_exit < len(velocity_total):
            rail_exit_velocity_m_s = velocity_total[idx_rail_exit]
            rail_exit_velocity_ft_s = rail_exit_velocity_m_s * 3.28084
            file_handle.write(
                f"   - Rail Exit Velocity: {rail_exit_velocity_ft_s:.2f} ft/s\n\n"
            )
        else:
            file_handle.write("   - Could not find velocity data for rail exit.\n\n")
    else:
        file_handle.write("   - LAUNCHROD event not found in simulation.\n\n")

    # 3. Descent from Apogee Velocity [ft/s]
    file_handle.write("3. Descent from Apogee Velocity [ft/s]:\n")
    apogee_times = events.get(FlightEvent.APOGEE, [])
    if apogee_times:
        apogee_time = max(apogee_times)
        file_handle.write(f"   Apogee Time: {apogee_time:.2f} s\n")
        recovery_deployment_times = events.get(
            FlightEvent.RECOVERY_DEVICE_DEPLOYMENT, []
        )
        if recovery_deployment_times:
            recovery_time = min(recovery_deployment_times)
            file_handle.write(
                f"   Recovery Device Deployment Time: {recovery_time:.2f} s\n"
            )
            descent_mask = (time >= apogee_time) & (time <= recovery_time)
        else:
            file_handle.write(
                "   Recovery device deployment event not found. Using end of simulation time.\n"
            )
            recovery_time = time[-1]
            descent_mask = time >= apogee_time

        descent_velocity_data = velocity_total[descent_mask]
        if len(descent_velocity_data) > 0:
            avg_descent_velocity = np.mean(descent_velocity_data) * 3.28084
            file_handle.write(
                f"   - Average Descent Velocity: {avg_descent_velocity:.2f} ft/s\n"
            )
            file_handle.write("   - Calculation Details:\n")
            file_handle.write(
                f"     - Duration of descent phase: {recovery_time - apogee_time:.2f} s\n"
            )
            file_handle.write(
                f"     - Number of velocity data points: {len(descent_velocity_data)}\n\n"
            )
        else:
            file_handle.write(
                "   - No descent velocity data available between apogee and recovery.\n\n"
            )
    else:
        file_handle.write("   - APOGEE event not found in simulation.\n\n")

    # 4. Average Velocity Between Drogue and Main Deployment
    file_handle.write(
        "3. Average Velocity Between Drogue and Main Deployment [ft/s]:\n"
    )
    recovery_deployment_times = events.get(FlightEvent.RECOVERY_DEVICE_DEPLOYMENT, [])
    if len(recovery_deployment_times) >= 2:
        drogue_time = recovery_deployment_times[0]  # First event for drogue
        main_time = recovery_deployment_times[-1]  # Last event for main
        file_handle.write(f"   Drogue Deployment Time: {drogue_time:.2f} s\n")
        file_handle.write(f"   Main Deployment Time: {main_time:.2f} s\n")
        if drogue_time < main_time:
            mask = (time >= drogue_time) & (time <= main_time)
            avg_velocity = np.mean(velocity_total[mask]) * 3.28084
            file_handle.write(
                f"   - Average Velocity Between Deployments: {avg_velocity:.2f} ft/s\n"
            )
            file_handle.write("   - Calculation Details:\n")
            file_handle.write(f"     - Duration: {main_time - drogue_time:.2f} s\n")
            file_handle.write(f"     - Data Points: {np.sum(mask)}\n\n")
        else:
            file_handle.write("   - Main deployed before drogue. Invalid sequence.\n\n")
    else:
        file_handle.write(
            "   - Not enough recovery deployment events to determine drogue and main.\n\n"
        )

    # 5. Ground Hit Velocity [ft/s]
    file_handle.write("4. Ground Hit Velocity [ft/s]:\n")
    ground_hit_times = events.get(FlightEvent.GROUND_HIT, [])
    if ground_hit_times:
        ground_hit_time = min(ground_hit_times)
        idx_ground_hit = np.argmin(np.abs(time - ground_hit_time))
        if 0 <= idx_ground_hit < len(velocity_total):
            ground_hit_velocity_m_s = velocity_total[idx_ground_hit]
            ground_hit_velocity_ft_s = ground_hit_velocity_m_s * 3.28084
            file_handle.write(
                f"   - Ground Hit Velocity: {ground_hit_velocity_ft_s:.2f} ft/s\n"
            )
            file_handle.write("   - Calculation Details:\n")
            file_handle.write(f"     - Ground Hit Time: {ground_hit_time:.2f} s\n")
            file_handle.write(
                f"     - Velocity at Ground Hit: {ground_hit_velocity_m_s:.2f} m/s\n\n"
            )
        else:
            file_handle.write(
                "   - Could not find valid velocity data for ground hit.\n\n"
            )
    else:
        file_handle.write("   - GROUND_HIT event not found in simulation.\n\n")


def plot_flight_events(ax, events, event_labels, event_colors, time):
    """
    Plot flight events as vertical lines with labels on the given axis.
    Args:
        ax (matplotlib.axes.Axes): The axis to plot on.
        events (dict): Dictionary of flight events.
        event_labels (dict): Mapping from FlightEvent to label strings.
        event_colors (dict): Mapping from FlightEvent to color strings.
        time (np.array): Time array for reference.
    """
    # Collect all events with their times and labels
    all_events = []
    for evt, times in events.items():
        label = event_labels.get(evt, evt.name)
        color = event_colors.get(evt, "grey")
        for t in times:
            if 0 <= t <= time[-1]:
                all_events.append({"time": t, "label": label, "color": color})

    # Sort events by time
    all_events.sort(key=lambda x: x["time"])

    # To prevent label overlapping, keep track of y-offsets
    y_offsets = {}

    for event in all_events:
        t = event["time"]
        label = event["label"]
        color = event["color"]

        # Plot vertical line
        ax.axvline(x=t, color=color, linestyle="--", linewidth=1)

        # Determine y position for label
        if label in y_offsets:
            y_offsets[label] += 0.02
        else:
            y_offsets[label] = 0.02

        # Get y-limit to place the label
        y_min, y_max = ax.get_ylim()

        # Annotate the event
        ax.annotate(
            label,
            xy=(t, y_max),
            xytext=(0, -10),  # Offset below the top
            textcoords="offset points",
            rotation=90,
            verticalalignment="top",
            horizontalalignment="center",
            color=color,
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.5),
        )


def generate_plots(
    time,
    altitude,
    velocity_total,
    thrust_force,
    events,
    file_handle,
    individual_plots_dir,
):
    """
    Generate and save the relevant plots:
      1) Thrust vs Time (with on-rail phase highlighted)
      2) Velocity vs Time (with all flight events labeled)
      3) Altitude vs Time (with all flight events labeled)
      4) Descent Velocity from Apogee until Recovery
    Args:
        time (np.array): Time array in seconds
        altitude (np.array): Altitude array in meters
        velocity_total (np.array): Velocity array in m/s
        thrust_force (np.array): Thrust array in N
        events (dict): Dictionary of flight events
        file_handle: File handle for writing plot save info
        individual_plots_dir (str): Directory path for saving plots
    """
    # Convert thrust to lbf for plotting
    thrust_force_lbf = thrust_force * 0.224809
    # Convert velocity to ft/s
    velocity_ft_s = velocity_total * 3.28084

    # Define event labels and colors
    event_labels = {
        FlightEvent.LAUNCH: "Launch",
        FlightEvent.IGNITION: "Motor Ignition",
        FlightEvent.LIFTOFF: "Lift-off",
        FlightEvent.LAUNCHROD: "Launch Rod Clearance",
        FlightEvent.BURNOUT: "Motor Burnout",
        FlightEvent.EJECTION_CHARGE: "Ejection Charge",
        FlightEvent.APOGEE: "Apogee",
        FlightEvent.RECOVERY_DEVICE_DEPLOYMENT: "Recovery Device Deployment",
        FlightEvent.GROUND_HIT: "Ground Hit",
        FlightEvent.SIMULATION_END: "Simulation End",
    }

    event_colors = {
        FlightEvent.LAUNCH: "blue",
        FlightEvent.IGNITION: "orange",
        FlightEvent.LIFTOFF: "green",
        FlightEvent.LAUNCHROD: "purple",
        FlightEvent.BURNOUT: "brown",
        FlightEvent.EJECTION_CHARGE: "pink",
        FlightEvent.APOGEE: "red",
        FlightEvent.RECOVERY_DEVICE_DEPLOYMENT: "cyan",
        FlightEvent.GROUND_HIT: "black",
        FlightEvent.SIMULATION_END: "magenta",
    }

    # 1. Thrust vs Time with on-rail phase
    try:
        plt.figure(figsize=(12, 6))
        plt.plot(time, thrust_force_lbf, "b-", label="Thrust Force (lbf)")

        liftoff_times = events.get(FlightEvent.LIFTOFF, [])
        if liftoff_times:
            liftoff_time = min(liftoff_times)
            plt.axvline(x=liftoff_time, color="g", linestyle="--", label="Liftoff")
            mask = time <= liftoff_time
            plt.fill_between(
                time,
                thrust_force_lbf,
                where=mask,
                color="orange",
                alpha=0.3,
                label="On Rail",
            )

        plt.xlabel("Time (s)")
        plt.ylabel("Thrust (lbf)")
        plt.title("Thrust Force vs Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Label all flight events
        ax = plt.gca()
        plot_flight_events(ax, events, event_labels, event_colors, time)

        thrust_plot_path = os.path.join(individual_plots_dir, "thrust_vs_time.png")
        plt.savefig(thrust_plot_path)
        plt.close()
        print(f"[INFO] Saved plot: {thrust_plot_path}")
        file_handle.write(f"Saved plot: {thrust_plot_path}\n\n")
    except Exception as e:
        print(f"[ERROR] Error during thrust plot: {e}")
        file_handle.write(f"Error during thrust plot: {e}\n\n")

    # 2. Velocity vs Time with all flight events labeled
    try:
        plt.figure(figsize=(12, 6))
        plt.plot(time, velocity_ft_s, "r-", label="Velocity (ft/s)")

        plt.xlabel("Time (s)")
        plt.ylabel("Velocity (ft/s)")
        plt.title("Velocity vs Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Label all flight events
        ax = plt.gca()
        plot_flight_events(ax, events, event_labels, event_colors, time)

        velocity_plot_path = os.path.join(individual_plots_dir, "velocity_vs_time.png")
        plt.savefig(velocity_plot_path)
        plt.close()
        print(f"[INFO] Saved plot: {velocity_plot_path}")
        file_handle.write(f"Saved plot: {velocity_plot_path}\n\n")
    except Exception as e:
        print(f"[ERROR] Error during velocity plot: {e}")
        file_handle.write(f"Error during velocity plot: {e}\n\n")

    # 3. Altitude vs Time with all flight events labeled
    try:
        plt.figure(figsize=(12, 6))
        plt.plot(time, altitude, "g-", label="Altitude (m)")

        plt.xlabel("Time (s)")
        plt.ylabel("Altitude (m)")
        plt.title("Altitude vs Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Label all flight events
        ax = plt.gca()
        plot_flight_events(ax, events, event_labels, event_colors, time)

        altitude_plot_path = os.path.join(individual_plots_dir, "altitude_vs_time.png")
        plt.savefig(altitude_plot_path)
        plt.close()
        print(f"[INFO] Saved plot: {altitude_plot_path}")
        file_handle.write(f"Saved plot: {altitude_plot_path}\n\n")
    except Exception as e:
        print(f"[ERROR] Error during altitude plot: {e}")
        file_handle.write(f"Error during altitude plot: {e}\n\n")

    # 4. Descent velocity from apogee until recovery (or end of sim)
    try:
        # Define apogee_times within generate_plots
        apogee_times = events.get(FlightEvent.APOGEE, [])

        if apogee_times:
            apogee_time = max(apogee_times)
            recovery_deployment_times = events.get(
                FlightEvent.RECOVERY_DEVICE_DEPLOYMENT, []
            )
            if recovery_deployment_times:
                recovery_time = min(recovery_deployment_times)
                print(
                    f"[INFO] Using recovery device deployment time: {recovery_time:.2f} s"
                )
                file_handle.write(
                    f"Using recovery device deployment time: {recovery_time:.2f} s\n\n"
                )
            else:
                recovery_time = time[-1]
                print(
                    "[INFO] Recovery device deployment not found. Using end of simulation time."
                )
                file_handle.write(
                    "Recovery device deployment not found. Using end of simulation time.\n\n"
                )

            descent_mask = (time >= apogee_time) & (time <= recovery_time)
            descent_velocity_data = velocity_total[descent_mask]
            descent_time = time[descent_mask]
            descent_velocity_ft_s = descent_velocity_data * 3.28084

            plt.figure(figsize=(12, 6))
            plt.plot(
                descent_time,
                descent_velocity_ft_s,
                "c-",
                label="Descent Velocity (ft/s)",
            )

            if len(descent_velocity_ft_s) > 0:
                plt.xlabel("Time (s)")
                plt.ylabel("Velocity (ft/s)")
                plt.title("Descent Velocity from Apogee to Recovery Deployment")
                plt.legend()
                plt.grid(True)
                plt.tight_layout()

                # Label relevant flight events
                ax = plt.gca()
                # Only label Apogee and Recovery Device Deployment on this plot
                relevant_events = {
                    FlightEvent.APOGEE: events.get(FlightEvent.APOGEE, []),
                    FlightEvent.RECOVERY_DEVICE_DEPLOYMENT: events.get(
                        FlightEvent.RECOVERY_DEVICE_DEPLOYMENT, []
                    ),
                }
                # Flatten the relevant_events dictionary
                flat_relevant_events = {}
                for evt, times in relevant_events.items():
                    label = event_labels.get(evt, evt.name)
                    color = event_colors.get(evt, "grey")
                    for t in times:
                        if apogee_time <= t <= recovery_time:
                            flat_relevant_events[evt] = [t]
                plot_flight_events(
                    ax, flat_relevant_events, event_labels, event_colors, time
                )

                descent_plot_path = os.path.join(
                    individual_plots_dir, "descent_velocity.png"
                )
                plt.savefig(descent_plot_path)
                plt.close()
                print(f"[INFO] Saved plot: {descent_plot_path}")
                file_handle.write(f"Saved plot: {descent_plot_path}\n\n")
    except Exception as e:
        print(f"[ERROR] Error during descent velocity plot: {e}")
        file_handle.write(f"Error during descent velocity plot: {e}\n\n")


def lcProgUpdate1():
    """
    Main function to run the entire logic of building directories, loading & simulating the rocket,
    retrieving data and events, computing key info, and generating plots.
    """
    # Set up directories
    ork_file, plots_dir, key_info_file_path, individual_plots_dir = setup_directories()

    # Create an OpenRocket instance
    with orlab.OpenRocketInstance() as instance:
        helper = orlab.Helper(instance)

        # Load and run the simulation
        sim = load_and_run_simulation(helper, ork_file)
        if sim is None:
            return  # Early exit if failed to load or run

        # Retrieve data and events
        data, events = retrieve_data_and_events(helper, sim)
        if data is None or events is None:
            return  # Early exit if data or events could not be retrieved

        # Open text file for writing key info
        with open(key_info_file_path, "w") as f:
            f.write(f"[INFO] Loaded rocket model from '{ork_file}'.\n\n")
            f.write("[INFO] Simulation run successful.\n\n")

            # Write flight events for reference
            if events:
                f.write("All Flight Events:\n")
                for evt, times in events.items():
                    f.write(f"  {evt.name}: {times}\n")
                f.write("\n")
            else:
                f.write("No flight events were found in the simulation.\n\n")

            # Validate data presence
            if not validate_data(data, f):
                return  # Early exit if missing data

            # Compute and record key info
            compute_and_write_key_info(data, events, f)

            # Generate and save plots
            time = data[FlightDataType.TYPE_TIME]
            altitude = data[FlightDataType.TYPE_ALTITUDE]
            velocity_total = data[FlightDataType.TYPE_VELOCITY_TOTAL]
            thrust_force = data[FlightDataType.TYPE_THRUST_FORCE]

            generate_plots(
                time,
                altitude,
                velocity_total,
                thrust_force,
                events,
                f,
                individual_plots_dir,
            )


if __name__ == "__main__":
    lcProgUpdate1()
