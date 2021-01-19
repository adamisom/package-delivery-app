# Package Delivery App
<img src="package_delivery_app/project_logo.png" alt="app logo" width="480">

This repo simulates package-delivery by truck. 

It expects csv files containing distance data and package data. It instantiates truck and package objects and then constructs a route which handles multiple package constraints, uses nearest-neighbors, and shortens the route as much as possible while still delivering all package on time. It then "loads" trucks and "delivers" packages.

## Installation
`pip install package-delivery-app`

Dependencies: none.

Prerequisites: Python 3 and either MacOS or a recent Windows.

Tech used: just Python 3.6.8.

## Usage
The program's entry point is run_program() in \_\_main\_\_.py. The requirements for the distance and package csv files are documented in the load.py docstrings.

You can run this code as a package or as a module. 
1. As a package:
   - import package_delivery_app as pda
   - pda.run_program(your_distance_csv, your_package_csv)
2. As a module: 
   - python -m package_delivery_app your_distance_csv your_package_csv

Reminder: wrap filepaths in quotes if they have any spaces.

Tip: use Python's \_\_doc\_\_ function to learn more about a package or class.
  - Example: print(package_delivery_app.Hash.\_\_doc\_\_)

## Further Information
#### Purposes
 - Satisfy requirements for a Western Governors University course.
 - Go beyond those requirements; explore building a "real" Python application.

#### Custom Hash and time classes:
- Custom Hash and time classes are used. The Hash class was designed to (nearly) replicate Python dictionaries.

#### Features:
- Route takes into account several kinds of constraints, such as: deadlines, packages needing to have their destination corrected (having the wrong destination initially), sets of packages needing to go together, and so on.
- Users can request snapshots of the delivery status of each package.

#### Assumptions:
- Trucks maintain a constant speed of 18 miles per hour at all times.
- Trucks have a capacity of just 16 packages.

## Code Style
This project adheres to pep8. Idiomatic or 'Pythonic' ways were preferred, with the exception that I prefer the from/import style of imports.

## Note on the Logo
I designed the logo--a composite of 'noncommercial use with modification' images, except for the Python logo, which I don't think has the 'with modification' qualifier.

## License
MIT (see LICENSE.txt for details)
