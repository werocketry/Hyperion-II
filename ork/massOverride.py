# massOverride.py

import os
import numpy as np
import matplotlib.pyplot as plt
import logging

import orlab
from orlab import FlightDataType


def setup_logging():
    """Configure logging to output to both console and a specified log file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


def mass_override_analysis():
    # Define the plots directory
    plots_dir = os.path.join("ork", "outputs")
    os.makedirs(plots_dir, exist_ok=True)

    setup_logging()

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
            logging.info(f"Loaded rocket model from '{ork_file}'.\n")
        except Exception as e:
            logging.error(f"Failed to load the .ork file: {e}")
            return

        # Get the payload component
        payload = None
        for component in orl.get_all_components(rocket):
            if component.getName() == "Payload":
                payload = component
                break

        if payload is None:
            logging.error("No component named 'Payload' found.")
            return

        base_mass = payload.getMass()
        logging.info(f"Base mass of 'Payload': {base_mass} kg.\n")

        # Define a range of mass multipliers
        mass_multipliers = np.linspace(0.5, 1.5, 11)  # From 50% to 150% of base mass

        apogees = []
        max_velocities = []
        payload_masses = mass_multipliers * base_mass

        for multiplier, mass in zip(mass_multipliers, payload_masses):
            mass_variation_percent = (multiplier - 1) * 100
            logging.info(
                f"Setting Payload mass to {mass:.2f} kg ({mass_variation_percent:+.0f}%)."
            )
            payload.setMassOverridden(True)
            payload.setOverrideMass(mass)

            # Run the simulation
            try:
                orl.run_simulation(sim)
                logging.info("Simulation run successful.")
                data = orl.get_timeseries(
                    sim,
                    [
                        FlightDataType.TYPE_ALTITUDE,
                        FlightDataType.TYPE_VELOCITY_TOTAL,
                    ],
                )
                apogee = np.max(data[FlightDataType.TYPE_ALTITUDE])
                max_velocity = np.max(data[FlightDataType.TYPE_VELOCITY_TOTAL])
                logging.info(
                    f"Apogee: {apogee:.2f} m, Max Velocity: {max_velocity:.2f} m/s.\n"
                )
            except Exception as e:
                logging.error(f"Simulation failed: {e}")
                apogee = np.nan
                max_velocity = np.nan

            apogees.append(apogee)
            max_velocities.append(max_velocity)

        # Reset the mass override
        payload.setMassOverridden(False)
        logging.info("Reset Payload mass override.\n")

        # Plot the results
        fig, axs = plt.subplots(2, 1, figsize=(10, 10))

        # Apogee vs Payload Mass
        axs[0].plot(payload_masses, apogees, "o-b")
        axs[0].set_xlabel("Payload Mass (kg)")
        axs[0].set_ylabel("Apogee Altitude (m)")
        axs[0].set_title("Effect of Payload Mass on Apogee Altitude")
        axs[0].grid(True)

        # Max Velocity vs Payload Mass
        axs[1].plot(payload_masses, max_velocities, "o-r")
        axs[1].set_xlabel("Payload Mass (kg)")
        axs[1].set_ylabel("Maximum Velocity (m/s)")
        axs[1].set_title("Effect of Payload Mass on Maximum Velocity")
        axs[1].grid(True)

        plt.tight_layout()
        plot_path = os.path.join(plots_dir, "payload_mass_effects.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Saved plot: {plot_path}")


if __name__ == "__main__":
    mass_override_analysis()
