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

## More Information
#### Purposes
 - Satisfy requirements for a Western Governors University course.
 - Go beyond those requirements; explore building a "real" Python application.

#### Notable requirements & features:
- Route takes into account several kinds of constraints, such as: deadlines, packages needing to have their destination corrected (having the wrong destination initially), sets of packages needing to go together, and so on.
- Users can request snapshots of the delivery status of each package
- Custom Hash and time classes are used. The Hash class was designed to (nearly) replicate Python dictionaries (a Hash class of some kind was a course requirement).

#### Notably unrealistic assumptions:
- Trucks maintain a constant speed of 18 miles per hour at all times.
- Trucks have a capacity of just 16 packages.

#### What is definitely out-of-scope
It would be pretty cool for this to allow real-time updates, to track when trucks actually arrive at various places. It would be pretty cool for this to integrate with a package-scanner. It would be pretty cool for this to have a pretty web and/or mobile front-end, or even a GUI. It would be pretty cool for this to use a database (SQLAlchemy is fun to use). It does not do any of those things and likely never will.

## Possible Future Enhancements
- add and automate tests
- enhance "distances" data structure by applying a shortest-path all-pairs algorithm such as Floyd-Warshall (arguably more appropriate than Dijkstra's for dense graphs like intra-city distances) rather than simply using the direct-path distances from the supplied distances-csv input file
  - the file floyd-warshall-annotated.py at [my repo here](https://github.com/adamisom/python-odds-and-ends) could be used
- try smarter "nearest neighbors" to see how much they help 
  - try the 'altered' and 'repeated' strategies suggested by [Norvig here](https://nbviewer.jupyter.org/url/norvig.com/ipython/TSP.ipynb)
- automatically optimize, for arbitrary input data, the currently-hardcoded parameter for the Route_Builder add_nearby_neighbors method 
- enhance improve_route to not only optimize small segments but to optimize sets of segments as well (note that optimizing the entire route is O(n!), but keeping "n" small at all times avoids long runtimes)
- build out a speed-function using realistic average speeds between destinations including the fact that some roads may be faster/slower plus the time necessary for a truck to stop, deliver packages, and start again
  - a Truck-class speed_function exists and is used by other classes already, as a sort of 'hook' for inserting additional functionality
  - a _super_ enhancement would be to learn this over time for a given city; right now my app is not nearly sophisticated enough to accommodate this
- allow user to add new packages or update current known packages
- enhance package histories to track the location of the truck when on route so that snapshots say precisely _where_ a package was at any given time
- permit routes to revisit a node if that would save time; initial testing shows this could save ~5% of distance/time (for my sample data)
- allow more than one special note on a package

## Code Style
This project adheres to pep8.

Idiomatic or 'Pythonic' ways were preferred, to the extent I've successfully learned them. Possible exception: I often prefer from/import for imports.

## Logo
The logo is a composite of 'noncommercial use with modification' images, except the Python logo which I don't think has the 'with modification' qualifier.

## License
MIT (see LICENSE.txt for details)