from http.client import PROCESSING
import shapely
from shapely.geometry import Point, Polygon, LineString, GeometryCollection
from shapely import affinity
import geopandas as gpd
import matplotlib.pyplot as plt
import moviepy.editor as mp
import numpy as np
import os
import util
import imageio
import os
from tkinter import *
import tk
import tkinter 
from tkinter import messagebox

R_TRUNK = 5
R_LEAF = 20
LEVELS = 20
Z_GAP = 2
ROT_ANGLE = 137.5 # golden angle 

top = tkinter.Tk()
top.title("Arc GEN")
label_list = [
     ["Arc generator",            0]
    ,["Line width",               0.35]
    ,["Layer height",             0.4]
    ,["Arc extrusion multiplier", 1.05]
    ,["Feedrate",                 2]
    ,["BrimWidth",                20]
    ,["Overhang Height",          20]
    ,["Filament DIA",             1.75]
    ,["Base Height",              0.5]
    ,["Max circle radius",        10]
    ,["Min circle radius",        2]
    ,["Points per circle",        40]
    ,["Radius of random polygon", 10]
    ,["Polygon irregularity",     0.5]
    ,["Polygon spikiness",        0.3]
    ,["Polygon num vertices",     15]
    ,["X Axis position",          100]
    ,["Y Axis position",          50]]
L = []
for i, label in enumerate(label_list):
    L.append("nothing")
    L[i] = Label(top, text=label_list[i][0],).grid(row=i,column=0)


E = []
for i in range(len(label_list)-1):
    E.append("nothing")
    E[i] = Entry(top, bd =5)
    E[i].grid(row = i+1,column=1)
    E[i].insert(i, str(label_list[i+1][1]))

def proces():
    global LINE_WIDTH
    i = 0
    LINE_WIDTH=float(Entry.get(E[i]))
    i += 1
    global LAYER_HEIGHT
    LAYER_HEIGHT = float(Entry.get(E[i]))
    i += 1
    global ARC_E_MULTIPLIER
    ARC_E_MULTIPLIER = float(Entry.get(E[i]))
    i += 1
    global FEEDRATE
    FEEDRATE = float(Entry.get(E[i]))
    i += 1
    global BRIM_WIDTH
    BRIM_WIDTH = float(Entry.get(E[i]))
    i += 1
    global OVERHANG_HEIGHT
    OVERHANG_HEIGHT = float(Entry.get(E[i]))
    i += 1
    global FILAMENT_DIAMETER
    FILAMENT_DIAMETER = float(Entry.get(E[i]))
    i += 1
    global BASE_HEIGHT
    BASE_HEIGHT = float(Entry.get(E[i]))
    i += 1
    global R_MAX
    R_MAX = float(Entry.get(E[i]))
    i += 1
    global R_MIN
    R_MIN = float(Entry.get(E[i]))
    i += 1
    global N
    N = float(Entry.get(E[i]))
    i += 1
    global  avg_radius
    avg_radius = float(Entry.get(E[i]))
    i += 1
    global irregularity
    irregularity = float(Entry.get(E[i]))
    i += 1
    global spikiness
    spikiness = float(Entry.get(E[i]))
    i += 1
    global num_vertices
    num_vertices = float(Entry.get(E[i]))
    i += 1
    global x_axis
    x_axis = float(Entry.get(E[i]))
    i += 1
    global y_axis
    y_axis = float(Entry.get(E[i]))
    top.destroy()

B=Button(top, text ="Generate",command= proces).grid(row=19,column=1)
top.mainloop()

# Hard-coded recursion information
THRESHOLD = R_MIN  #5 # How much of a 'buffer' the arcs leave around the base polygon. Don't set it negative or bad things happen.
MIN_ARCS = np.floor(R_MIN/LINE_WIDTH)
OUTPUT_FILE_NAME = "output/output.gcode"

# Create a figure that we can plot stuff onto
fig, ax = plt.subplots(1, 2)
ax[0].set_aspect('equal')
ax[1].set_aspect('equal')
ax[0].title.set_text('Gcode Preview')
ax[1].title.set_text('Rainbow Visualization')

# Create a list of image names
image_name_list = []

# Delete all previous images
current_directory = "./"
files_in_directory = os.listdir(current_directory)
for item in files_in_directory:
    if item.endswith(".png"):
        os.remove(os.path.join(current_directory, item))

# Create a new gcode file
os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)
with open(OUTPUT_FILE_NAME, 'w') as gcode_file:
    gcode_file.write(""";gcode for ArcOverhang. Created by Steven McCulloch\n""")

# Add start gcode
with open('input/start.gcode','r') as start_gcode, open(OUTPUT_FILE_NAME,'a') as gcode_file:
    for line in start_gcode:
        gcode_file.write(line)

base_poly = util.create_circle(x_axis, y_axis + R_TRUNK, R_LEAF, N)
trunk_poly = util.create_circle(x_axis, y_axis, R_TRUNK, N)
base_poly = base_poly.difference(trunk_poly)

# Find starting edge (in this implementation, it just finds the largest edge to start from.
# TODO Allow multiple starting points
# TODO Come up with some way to determine starting edges based on geometry of previous layer
 
starting_arc = trunk_poly.intersection(base_poly)

# plot base poly
base_poly_geoseries = gpd.GeoSeries(base_poly)
base_poly_geoseries.plot(ax=ax[0], color='white', edgecolor='black', linewidth=1)
base_poly_geoseries.plot(ax=ax[1], color='white', edgecolor='black', linewidth=1)

# Move nozzle to start position
curr_z = LAYER_HEIGHT  # Height of first layer
with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
    gcode_file.write(f"G0 X{'{0:.3f}'.format(x_axis)} Y{'{0:.3f}'.format(y_axis)} F500\n")
    gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    gcode_file.write(";Generating first layer\n")
    gcode_file.write("G1 E3.8\n")  # Unretract
    
# Print brim + bottom layer(s) 
while curr_z < BASE_HEIGHT:
    starting_tower_r = R_TRUNK + BRIM_WIDTH
    while starting_tower_r > LINE_WIDTH*2:
        first_layer_circle = util.create_circle(x_axis, y_axis, starting_tower_r, N)
        util.write_gcode(OUTPUT_FILE_NAME, first_layer_circle, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 2, FEEDRATE*5, close_loop=True)
        starting_tower_r -= LINE_WIDTH*2
    
    curr_z += LAYER_HEIGHT
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")

# Turn fan on after first few layers
with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
    gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    gcode_file.write(";Generating tower\n")
    gcode_file.write("M106 S255 ;Turn on fan to max power\n") 

for level in range(LEVELS):
    # Print Trunk  
    start_z = curr_z  
    while curr_z < Z_GAP+start_z:
        first_layer_circle = util.create_circle(x_axis, y_axis, R_TRUNK, N)
        util.write_gcode(OUTPUT_FILE_NAME, first_layer_circle, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 2, FEEDRATE*5, close_loop=True)
        curr_z += LAYER_HEIGHT
        with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
            gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")

    curr_z -= LAYER_HEIGHT

    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
            gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
            gcode_file.write(";Printing Arcs\n")

    # Create multiple layers
    r = LINE_WIDTH
    small_arc_radius = 0.5 # Arcs smaller than this get reduced speed and/or flow settings.

    # Create arcs until we reach the edge of the polygon
    while r < R_LEAF:

        # Create a circle based on point location, radius, n
        next_circle = Polygon(util.create_circle(x_axis, y_axis + R_TRUNK, r, N))
        next_circle = affinity.rotate(next_circle, level*ROT_ANGLE, origin = Point(x_axis, y_axis), use_radians=False)
        base_poly = Polygon(util.create_circle(x_axis, y_axis + R_TRUNK, R_LEAF, N))
        base_poly = affinity.rotate(base_poly, level*ROT_ANGLE, origin = Point(x_axis, y_axis), use_radians=False)
        if base_poly.contains(trunk_poly):
            close_loop = True
        else:
            close_loop = False
        base_poly = base_poly.difference(trunk_poly).buffer(1e-9)

        # Plot arc
        next_arc = util.create_arc(next_circle, base_poly, ax, depth=0)
        if not next_arc:
            r += LINE_WIDTH
            continue

        #Slow down and reduce flow for all small arcs
        if r < small_arc_radius:
            speed_modifier = 0.25
            e_modifier = 0.25
        else: 
            speed_modifier = 1
            e_modifier = 1

        # Write gcode to file

        util.write_gcode(OUTPUT_FILE_NAME, next_arc, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER*e_modifier, FEEDRATE*speed_modifier, close_loop)
        
        r += LINE_WIDTH

    R_LEAF -= 2*(R_LEAF/LEVELS)

curr_z += LAYER_HEIGHT*2

with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")  

# Print top layers
starting_tower_r = R_TRUNK
while starting_tower_r > LINE_WIDTH:
        first_layer_circle = util.create_circle(x_axis, y_axis, starting_tower_r, N)
        util.write_gcode(OUTPUT_FILE_NAME, first_layer_circle, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 1.2, FEEDRATE, close_loop=True)
        starting_tower_r -= LINE_WIDTH

# Write end gcode
with open('input/end.gcode','r') as end_gcode, open(OUTPUT_FILE_NAME,'a') as gcode_file:
    for line in end_gcode:
        gcode_file.write(line)

# Create image
plt.savefig("output/output", dpi=600)
plt.show()