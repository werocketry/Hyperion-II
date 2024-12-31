import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re


def parse_test_file(file_path):
    """
    Parses the compressive test data file and returns a list of runs.
    Each run is a dictionary containing metadata and a DataFrame of data points.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()

    print(f"File read successfully: {file_path}")

    runs = []
    data_started = False
    data_lines = []
    header = []

    header_keywords = ["Point", "Time", "Axial Pos.", "DC1", "DC2", "DC3", "DC4"]

    for line_number, line in enumerate(lines, start=1):
        original_line = line
        line = line.strip()
        line_no_quotes = line.replace('"', "").replace("�", " ")

        if all(
            keyword.lower() in line_no_quotes.lower() for keyword in header_keywords
        ):
            print(f"Header detected at line {line_number}: {line}")
            if data_started and data_lines:
                df = pd.DataFrame(data_lines, columns=header)
                runs.append({"data": df})
                print(f"Run added. Data points: {len(data_lines)}")
                data_lines = []
                header = []

            data_started = True
            continue

        if data_started and not header:
            header = [
                "Point No.",
                "Time (s)",
                "Axial Pos. (mm)",
                "DC1 (N)",
                "DC2 (LB)",
                "DC3",
                "DC4",
            ]
            print(f"Header columns set: {header}")
            continue

        if data_started:
            if line == "":
                continue

            parts = re.split(r"\s+", line_no_quotes)
            if len(parts) >= 7:
                try:
                    point_no = int(parts[0])
                    time_s = float(parts[1])
                    axial_pos_mm = float(parts[2])
                    dc1_n = float(parts[3])
                    dc2_lb = float(parts[4])
                    dc3 = parts[5]
                    dc4 = parts[6]
                    data_lines.append(
                        [point_no, time_s, axial_pos_mm, dc1_n, dc2_lb, dc3, dc4]
                    )
                except ValueError:
                    print(f"Skipping line {line_number}: {original_line}")
            else:
                print(f"Incomplete data line at line {line_number}: {original_line}")

    if data_started and data_lines:
        df = pd.DataFrame(data_lines, columns=header)
        runs.append({"data": df})
        print(f"Final run added. Data points: {len(data_lines)}")

    print(f"Total runs detected in {file_path}: {len(runs)}")
    return runs


def visualize_and_save_metrics(runs, file_id, output_dir, metrics_output_path):
    """
    Visualizes data for each run and appends metrics to a combined output file.
    """
    with open(metrics_output_path, "a") as metrics_file:
        for idx, run in enumerate(runs, start=1):
            df = run["data"]
            df["DC1 (N)"] = pd.to_numeric(df["DC1 (N)"], errors="coerce").abs()
            df["Axial Displacement (mm)"] = df["Axial Pos. (mm)"].abs()

            plt.figure(figsize=(10, 6))
            sns.lineplot(
                x="Axial Displacement (mm)", y="DC1 (N)", data=df, label="DC1 (N)"
            )
            plt.title(f"{file_id} - Run {idx} - Load vs. Axial Displacement")
            plt.xlabel("Axial Displacement (mm)")
            plt.ylabel("Load (N)")
            plt.legend()
            plt.grid(True)

            plot_file = os.path.join(output_dir, f"{file_id}_run_{idx}_plot.png")
            plt.savefig(plot_file)
            plt.close()

            if not df.empty:
                max_load_dc1 = df["DC1 (N)"].max()
                deformation_at_max_dc1 = df.loc[
                    df["DC1 (N)"].idxmax(), "Axial Displacement (mm)"
                ]
                metrics = (
                    f"{file_id} - Run {idx} Metrics:\n"
                    f"  Max Load (DC1) = {max_load_dc1:.3f} N\n"
                    f"  Axial Displacement at Max Load = {deformation_at_max_dc1:.3f} mm\n\n"
                )
            else:
                metrics = f"{file_id} - Run {idx} Metrics:\nNo data available.\n\n"

            metrics_file.write(metrics)
            print(f"Run {idx} processed: Metrics and plot saved.")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_files = ["NOV2224_first.txt", "NOV2224_second.txt"]
    output_dir = os.path.join(script_dir, "outputs")
    metrics_output_path = os.path.join(output_dir, "combined_metrics.txt")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Clear previous metrics output
    if os.path.exists(metrics_output_path):
        os.remove(metrics_output_path)

    for input_file in input_files:
        input_path = os.path.join(script_dir, input_file)
        if not os.path.isfile(input_path):
            print(f"Error: Input file '{input_file}' not found.")
            continue

        runs = parse_test_file(input_path)
        if runs:
            file_id = os.path.splitext(input_file)[0]
            visualize_and_save_metrics(runs, file_id, output_dir, metrics_output_path)
        else:
            print(f"No runs detected in {input_file}. Skipping.")

    print(f"Processing complete. Outputs saved to '{output_dir}'.")


if __name__ == "__main__":
    main()
