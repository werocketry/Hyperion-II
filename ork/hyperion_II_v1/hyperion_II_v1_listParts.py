# listParts.py

import os
from orlab import OpenRocketInstance, Helper


def write_component_attributes_to_file(file_path, all_components):
    """Write the list of components and their attributes to a file."""
    with open(file_path, "w") as file:
        file.write("List of all components with their attributes:\n\n")
        for idx, component in enumerate(all_components, start=1):
            name = str(component.getName())
            component_type = component.getClass().getSimpleName()

            file.write(f"Component {idx}:\n")
            file.write(f"  Name: {name}\n")
            file.write(f"  Type: {component_type}\n")

            # Retrieve and write specific attributes if available
            try:
                mass = component.getMass()
                file.write(f"  Mass: {mass} kg\n")
            except AttributeError:
                file.write("  Mass: Not Available\n")

            try:
                length = component.getLength()
                file.write(f"  Length: {length} m\n")
            except AttributeError:
                file.write("  Length: Not Available\n")

            try:
                diameter = component.getDiameter()
                file.write(f"  Diameter: {diameter} m\n")
            except AttributeError:
                file.write("  Diameter: Not Available\n")

            try:
                area = component.getReferenceArea()
                file.write(f"  Reference Area: {area} m²\n")
            except AttributeError:
                file.write("  Reference Area: Not Available\n")

            file.write("\n" + "-" * 50 + "\n\n")


def list_component_attributes():
    # Define the plots directory
    plots_dir = os.path.join("ork", "hyperion_II_v1", "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Define the output file path
    file_path = os.path.join(plots_dir, "component_attributes.txt")

    # Initialize the OpenRocketInstance context
    with OpenRocketInstance() as instance:
        orl = Helper(instance)

        # Load the OpenRocket document
        ork_path = os.path.join("ork", "hyperion_II_v1", "hyperion_II_v1.ork")
        if not os.path.exists(ork_path):
            print(f"Error: The .ork file was not found at path: {ork_path}")
            return

        try:
            doc = orl.load_doc(ork_path)
            rocket = doc.getRocket()
            print(f"Loaded rocket model from '{ork_path}'.\n")
        except Exception as e:
            print(f"Failed to load the .ork file: {e}")
            return

        # Retrieve all components
        all_components = orl.get_all_components(rocket)
        print(f"Found {len(all_components)} components in the rocket model.\n")

        # Write components and attributes to the file
        write_component_attributes_to_file(file_path, all_components)
        print(f"Component attributes written to: {file_path}")


if __name__ == "__main__":
    list_component_attributes()
