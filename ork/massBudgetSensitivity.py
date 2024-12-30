# massBudgetSensitivity.py

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm  # For progress bars
import logging

import orlab
from orlab import FlightDataType


def setup_logging():
    """Configure logging for the script."""
    logging.basicConfig(
        filename="mass_budget_analysis.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )  # Overwrite log file each run
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def mass_budget_sensitivity_analysis():
    setup_logging()
    logging.info("Starting mass budget sensitivity analysis.")

    # Define the mass variation percentages
    mass_variations = np.arange(-5, 6, 1)  # -5%, -4%, ..., 0%, ..., +5%

    # Convert percentages to multipliers
    mass_multipliers = 1 + (mass_variations / 100.0)

    with orlab.OpenRocketInstance() as instance:
        orl = orlab.Helper(instance)

        # Load the document and get the simulation
        ork_file = os.path.join("ork", "hyperion_II_v2.ork")
        if not os.path.exists(ork_file):
            logging.error(f"The .ork file was not found at path: {ork_file}")
            return

        try:
            doc = orl.load_doc(ork_file)
            sim = doc.getSimulation(0)
            rocket = sim.getRocket()
            logging.info(f"Loaded rocket model from '{ork_file}'.")
        except Exception as e:
            logging.error(f"Failed to load the .ork file: {e}")
            return

        # Retrieve all components
        try:
            all_components = orl.get_all_components(rocket)
            logging.info(
                f"Retrieved {len(all_components)} components from the rocket model."
            )
        except Exception as e:
            logging.error(f"Failed to retrieve components: {e}")
            return

        # Store original masses
        original_masses = {}
        for component in all_components:
            try:
                mass = component.getMass()
                original_masses[component.getID()] = mass
            except AttributeError:
                # Component does not have a mass attribute
                continue

        if not original_masses:
            logging.warning("No components with mass found in the rocket model.")
            return

        # Prepare a list to store results
        results_list = []

        # Loop over components
        for component in tqdm(all_components, desc="Analyzing Components"):
            component_id = component.getID()
            # Convert Java string to Python string
            component_name = str(component.getName())
            component_type = component.getClass().getSimpleName()

            # Check if component has mass
            if component_id not in original_masses:
                continue  # Skip components without mass

            original_mass = original_masses[component_id]

            # Loop over mass multipliers
            for multiplier in mass_multipliers:
                mass_variation_percent = (multiplier - 1) * 100
                new_mass = original_mass * multiplier

                # Apply mass override
                component.setMassOverridden(True)
                component.setOverrideMass(new_mass)
                logging.info(
                    f"Component '{component_name}' mass set to {new_mass:.2f} kg ({mass_variation_percent:+.0f}%)."
                )

                # Run the simulation
                try:
                    orl.run_simulation(sim)
                    logging.info(
                        f"Simulation run successful for component '{component_name}' with mass variation {mass_variation_percent:+.0f}%."
                    )
                except Exception as e:
                    logging.error(
                        f"Simulation failed for component '{component_name}' with mass variation {mass_variation_percent:+.0f}%: {e}"
                    )
                    # Record NaN for all metrics if simulation fails
                    results_list.append(
                        {
                            "Component ID": component_id,
                            "Component Name": component_name,
                            "Component Type": component_type,
                            "Mass Variation (%)": mass_variation_percent,
                            "Apogee (m)": np.nan,
                            "Max Velocity (m/s)": np.nan,
                            "Max Acceleration (m/s^2)": np.nan,
                            "Max Mach Number": np.nan,
                            "Stability Margin (calibers)": np.nan,
                        }
                    )
                    # Reset mass override and continue
                    component.setMassOverridden(False)
                    continue

                # Collect performance metrics
                try:
                    data = orl.get_timeseries(
                        sim,
                        [
                            FlightDataType.TYPE_TIME,
                            FlightDataType.TYPE_ALTITUDE,
                            FlightDataType.TYPE_VELOCITY_TOTAL,
                            FlightDataType.TYPE_ACCELERATION_TOTAL,
                            FlightDataType.TYPE_MACH_NUMBER,
                            FlightDataType.TYPE_STABILITY,
                        ],
                    )

                    # Extract metrics
                    apogee = np.max(data[FlightDataType.TYPE_ALTITUDE])
                    max_velocity = np.max(data[FlightDataType.TYPE_VELOCITY_TOTAL])
                    max_acceleration = np.max(
                        data[FlightDataType.TYPE_ACCELERATION_TOTAL]
                    )
                    max_mach = np.max(data[FlightDataType.TYPE_MACH_NUMBER])
                    min_stability = np.min(
                        data[FlightDataType.TYPE_STABILITY]
                    )  # Assuming lower is better

                    logging.info(
                        f"Metrics for '{component_name}' at {mass_variation_percent:+.0f}% mass variation: Apogee={apogee:.2f} m, Max Velocity={max_velocity:.2f} m/s, Max Acceleration={max_acceleration:.2f} m/s², Max Mach={max_mach:.2f}, Stability Margin={min_stability:.2f} calibers."
                    )

                except Exception as e:
                    logging.error(
                        f"Error extracting data for component '{component_name}' with mass variation {mass_variation_percent:+.0f}%: {e}"
                    )
                    apogee = np.nan
                    max_velocity = np.nan
                    max_acceleration = np.nan
                    max_mach = np.nan
                    min_stability = np.nan

                # Append results to the list
                results_list.append(
                    {
                        "Component ID": component_id,
                        "Component Name": component_name,
                        "Component Type": component_type,
                        "Mass Variation (%)": mass_variation_percent,
                        "Apogee (m)": apogee,
                        "Max Velocity (m/s)": max_velocity,
                        "Max Acceleration (m/s^2)": max_acceleration,
                        "Max Mach Number": max_mach,
                        "Stability Margin (calibers)": min_stability,
                    }
                )

                # Reset mass override for the component
                component.setMassOverridden(False)

        # Create DataFrame from results list
        results = pd.DataFrame(results_list)

        # Verify if 'Component Name' exists
        if "Component Name" not in results.columns:
            logging.error(
                "'Component Name' column is missing from the results. Exiting script."
            )
            return

        # Reset masses of all components
        for component in all_components:
            if component.getID() in original_masses:
                component.setMassOverridden(False)

        # Save results to CSV (optional, since you requested to remove other outputs)
        # Uncomment the next two lines if you still want to save the CSV
        # results.to_csv("mass_budget_sensitivity_results.csv", index=False)
        # logging.info("Simulation results saved to 'mass_budget_sensitivity_results.csv'.")

        # Create 'plots' directory if it doesn't exist
        plots_dir = os.path.join("ork", "outputs")
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)
            logging.info(f"Created directory '{plots_dir}' for storing plots.")

        # Data Analysis and Visualization
        # Group results by component
        grouped = results.groupby("Component Name")

        # Sensitivity Analysis Summary for Apogee Only
        sensitivity = []

        metric = "Apogee (m)"
        for name, group in grouped:
            # Remove NaN values
            valid_indices = ~group[metric].isnull()
            x = group.loc[valid_indices, "Mass Variation (%)"].values
            y = group.loc[valid_indices, metric].values
            if len(x) > 1:
                coef = np.polyfit(x, y, 1)[0]  # Slope (m per % mass change)
                sensitivity.append(
                    {"Component Name": name, "Sensitivity (m per % mass change)": coef}
                )
                logging.info(
                    f"Calculated sensitivity for '{name}' - {metric}: {coef:.4f} m/%"
                )
            else:
                logging.warning(
                    f"Insufficient data to calculate sensitivity for '{name}' - {metric}."
                )

        # Create DataFrame for sensitivities
        sensitivity_df = pd.DataFrame(sensitivity)
        if sensitivity_df.empty:
            logging.error(
                "Sensitivity DataFrame is empty. No valid data to plot. Exiting script."
            )
            return

        # Save sensitivity DataFrame to CSV (optional)
        # Uncomment the next two lines if you still want to save the CSV
        # sensitivity_df.to_csv("mass_sensitivity_summary.csv", index=False)
        # logging.info("Sensitivity summary saved to 'mass_sensitivity_summary.csv'.")

        # Plot the sensitivity as a bar chart for Apogee Only
        plt.figure(figsize=(12, 8))
        # Sort components by sensitivity for this metric
        sensitivity_metric_df = (
            sensitivity_df[["Component Name", "Sensitivity (m per % mass change)"]]
            .dropna()
            .sort_values(by="Sensitivity (m per % mass change)", ascending=False)
        )
        plt.barh(
            sensitivity_metric_df["Component Name"],
            sensitivity_metric_df["Sensitivity (m per % mass change)"],
            color="skyblue",
        )
        plt.xlabel("Sensitivity (m per % mass change)")
        plt.title("Apogee Sensitivity to Mass Variation by Component")
        plt.gca().invert_yaxis()  # Highest sensitivity on top
        plt.grid(axis="x")
        plt.tight_layout()
        # Save plot
        filename = "apogee_sensitivity_bar_chart.png"
        plt.savefig(os.path.join(plots_dir, filename))
        plt.close()
        logging.info(f"Saved plot: {filename}")

        logging.info(f"All plots saved in the '{plots_dir}' directory.")
        logging.info("Mass budget sensitivity analysis completed successfully.")


if __name__ == "__main__":
    mass_budget_sensitivity_analysis()
