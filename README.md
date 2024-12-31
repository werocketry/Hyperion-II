# Hyperion-II

This repository contains all the resources, designs, and analyses for the Hyperion-II rocket project. It is organized into several folders, each dedicated to a specific aspect of the project. Below is a breakdown of the repository structure and its contents.

## Repository Details

### Structure

```
Hyperion-II
├───cad
│   └───dwg
├───ork
│   └───outputs
├───rasAeroII
├───schematics
└───testing
   └───aero
```

### `cad/`

Contains the computer-aided design (CAD) files for Hyperion-II, including drawings and 3D models. The `dwg/` subfolder is specifically for detailed technical drawings.

### `ork/`

Holds all OpenRocket simulation files (`.ork`) and associated Python scripts that utilize [orlab](https://github.com/CameronBrooks11/orlab) for simulation analysis. The `outputs/` subfolder contains generated plots, text files, and sensitivity analyses derived from these simulations. Once you have Python and a valid Java release installed, install `orlab` using:

```
pip install orlab
```

For detailed installation instructions see [CameronBrooks11/orlab](https://github.com/CameronBrooks11/orlab).

### `rasAeroII/`

Placeholder for files related to RASAero II simulations.

### `schematics/`

Contains electronic schematics and related documentation for onboard systems.

### `testing/`

Documents all physical tests, including aerodynamics, electronics, and structural assessments. Each test has its own subfolder with details and results.

- **Key Subfolders**:
  - `2024-11-24_compression_al_couplers/`: Contains data for aluminum coupler compression testing on the specified date.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. Ensure you adhere to the coding standards and provide detailed documentation for any new scripts or analyses.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
