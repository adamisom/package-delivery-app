# Package Delivery App
<img src="project_logo.png" alt="app logo" width="480">

This repo simulates package-delivery by truck. 

It expects csv files containing distance data and package data. It instantiates truck and package objects and then constructs a route which handles multiple package constraints, uses nearest-neighbors, and shortens the route as much as possible while still delivering all package on time. It then "loads" trucks and "delivers" packages.

## Installation
No dependencies. Works on Mac & Windows. Vanilla Python (3.6.8). Just

`pip install package-delivery-app`

## Usage
The program's entry point is run_program() in \_\_main\_\_.py. The requirements for the distance and package csv files are documented in the load.py docstrings.

You can execute as a package or as a module. 
1. As a package:
   - "import package_delivery_app as pda"
   - "pda.run_program(_your_distance_csv_, _your_package_csv_)"
2. As a module: 
   - "python -m package_delivery_app _your_distance_csv_ _your_package_csv_"

Reminder: wrap filepaths in quotes if they have any spaces.

Tips: 
 - inspecting which functions are imported from a module into \_\_main\_\_ reveals what the 'public API' of that module is intended to be 
    - for example, build_route is the only Route_Builder.py method meant to be called elsewhere
  - there are several "display_" methods you could avail yourself of to pretty-print various things
  - if you're not familiar with Python's dir and \_\_doc\_\_ functions, they're helpful for learning more about what a package offers. 
    - Example: dir(package_delivery_app.load)
    - Example: print(package_delivery_app.Hash.\_\_doc\_\_)

## More Information
#### Purposes
 - Satisfy requirements for a Western Governors University course.
 - Go beyond those requirements and explore building what I hope is a small but professional-grade Python application.

#### Notable requirements & features:
- Route takes into account several kinds of constraints, such as: deadlines, packages needing to have their destination corrected (having the wrong destination initially), sets of packages needing to go together, and so on.
- Users can request snapshots of the delivery status of each package
- Custom Hash and time classes are used. The Hash class was designed to (nearly) replicate Python dictionaries and was a course requirement.

#### Notably unrealistic assumptions:
- trucks maintain a constant speed of 18 miles per hour at all times
- trucks have a capacity of just 16 packages

#### What is definitely out-of-scope
It would be pretty cool for this to allow real-time updates, to track when trucks actually arrive at various places. It would be pretty cool for this to integrate with a package-scanner. It would be pretty cool for this to have a pretty web and/or mobile front-end, or even a GUI allowing users to add or update package information after initial load. It would be pretty cool for this to use a database (SQLAlchemy is fun to use). It does not do any of those things and almost surely never will.

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

I aimed for clarity in organization at the package, module, and method/function level; in docstrings and other comments; and in naming of variables, methods/functions and classes. I aimed to keep each methods/function brief, for it to do one type of thing, and for all its logic to be on the "same level". If you read all the code and say 'WTF' more than a few times, I guess I've failed to achieve that clarity.

## Logo
Logo is a composite of 'noncommercial use with modification' images, except the Python logo which I don't think has the 'with modification' qualifier.

## License
MIT @ Adam Reed Isom 2019 (see LICENSE.txt)