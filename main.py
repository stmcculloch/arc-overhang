from http.client import PROCESSING
import shapely
from shapely.geometry import Point, Polygon, LineString, GeometryCollection
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


def proces():
    global LINE_WIDTH,LAYER_HEIGHT,ARC_E_MULTIPLIER,FEEDRATE,BRIM_WIDTH,OVERHANG_HEIGHT,FILAMENT_DIAMETER,BASE_HEIGHT,R_MAX,N,avg_radius,irregularity,spikiness,num_vertices,x_axis,y_axis 
   
    LINE_WIDTH=float(Entry.get(E1))
    LAYER_HEIGHT = float(Entry.get(E2))
    ARC_E_MULTIPLIER = float(Entry.get(E3))
    FEEDRATE = float(Entry.get(E4))
    BRIM_WIDTH = float(Entry.get(E5))
    OVERHANG_HEIGHT = float(Entry.get(E6))
    FILAMENT_DIAMETER = float(Entry.get(E7))
    BASE_HEIGHT = float(Entry.get(E8))
    R_MAX = float(Entry.get(E9))
    N = float(Entry.get(E10))
    avg_radius = float(Entry.get(E11))
    irregularity = float(Entry.get(E12))
    spikiness = float(Entry.get(E13))
    num_vertices = float(Entry.get(E14))
    x_axis = float(Entry.get(E15))
    y_axis = float(Entry.get(E16))
    top.destroy()


top = tkinter.Tk()
top.title("Arc GEN")
L200 = Label(top, text="Arc Generator",).grid(row=0,column=0)
L1 = Label(top, text="Line Width",).grid(row=1,column=0)
L2 = Label(top, text="Layer Height",).grid(row=2,column=0)
L3 = Label(top, text="ARC multiplier",).grid(row=3,column=0)
L4 = Label(top, text="Feedrate",).grid(row=4,column=0)
L5 = Label(top, text="BrimWidth",).grid(row=5,column=0)
L6 = Label(top, text="Overhang Height",).grid(row=6,column=0)
L7 = Label(top, text="Filament DIA",).grid(row=7,column=0)
L8 = Label(top, text="Base Height",).grid(row=8,column=0)
L9 = Label(top, text="Radius of Circle",).grid(row=9,column=0)
L10 = Label(top, text="Number Of Points",).grid(row=10,column=0)
L11 = Label(top, text="Average Rad",).grid(row=11,column=0)
L12 = Label(top, text="irregularity",).grid(row=12,column=0)
L13 = Label(top, text='spikiness',).grid(row=13,column=0)
L14 = Label(top, text='num vertices',).grid(row=14,column=0)
L15 = Label(top,text="X Axis Size",).grid(row=15,column=0)
L16 = Label(top,text="X Axis Size",).grid(row=16,column=0)



E1 = Entry(top, bd =5)
E1.grid(row=1,column=1)
E2 = Entry(top, bd =5)
E2.grid(row=2,column=1)
E3 = Entry(top, bd =5)
E3.grid(row=3,column=1)
E4 = Entry(top, bd =5)
E4.grid(row=4,column=1)
E5 = Entry(top, bd=5)
E5.grid(row=5,column=1)
E6 = Entry(top, bd =5)
E6.grid(row=6,column=1)
E7 = Entry(top, bd =5)
E7.grid(row=7,column=1)
E8 = Entry(top, bd =5)
E8.grid(row=8,column=1)
E9 = Entry(top, bd =5)
E9.grid(row=9,column=1)
E10 = Entry(top, bd=5)
E10.grid(row=10,column=1)
E11 = Entry(top, bd=5)
E11.grid(row=11, column=1)
E12 = Entry(top, bd=5)
E12.grid(row=12, column=1)
E13 = Entry(top, bd=5)
E13.grid(row=13, column=1)
E14 = Entry(top, bd=5)
E14.grid(row=14, column=1)
E15 = Entry(top, bd=5)
E15.grid(row=15, column=1)
E16 = Entry(top, bd=5)
E16.grid(row=16, column=1)

E1.insert(1,'.4')
E2.insert(1,'.4')
E3.insert(3,'1.3')
E4.insert(4,'2')
E5.insert(5,'5')
E6.insert(6,'20')
E7.insert(7,'1.75')
E8.insert(8,'2')
E9.insert(9,'30')
E10.insert(10,'40')
E11.insert(11,'10')
E12.insert(12,'.2')
E13.insert(13,'.2')
E14.insert(14,'15')
E15.insert(15,'225')
E16.insert(16,'210')

B=Button(top, text ="Generate",command= proces).grid(row=18,column=1)


top.mainloop()


print_settings = {
    "layer_height": LAYER_HEIGHT,
    "line_width": LINE_WIDTH,
    "e_multiplier": ARC_E_MULTIPLIER,
    "feedrate": FEEDRATE,
    "filament_diam": FILAMENT_DIAMETER,
    "brim_width": BRIM_WIDTH
}

# Shape generation parameters
#OVERHANG_HEIGHT = int(Entry.get(E9))
  # How high the test print is above the build plate
#BASE_HEIGHT = int(Entry.get(E10))
 # thickness of circular base

# Hard-coded recursion information
THRESHOLD = LINE_WIDTH / 2  # How much of a 'buffer' the arcs leave around the base polygon. Don't set it negative or bad things happen.
OUTPUT_FILE_NAME = "output/output.gcode"
#R_MAX 
  # maximum radius for a circle
#N = () #int(Entry.get(E2))
     # number of points per circle

# Create a figure that we can plot stuff onto
fig, ax = plt.subplots(1, 2)
ax[0].set_aspect('equal')
ax[1].set_aspect('equal')
ax[0].title.set_text('Gcode Preview')
ax[1].title.set_text('Rainbow Visualization')

# Create a list of image names
image_name_list = []

recursion_info = {
    "threshold": THRESHOLD,
    "gcode_file": OUTPUT_FILE_NAME,
    "fig": fig,
    "ax": ax,
    "image_name_list": image_name_list,
    "r_max": R_MAX,
    "n": N
}

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

# Create base polygon. The base polygon is the shape that will be filled by arcs
# base_poly = create_rect(RECT_X, RECT_Y, RECT_LENGTH, RECT_WIDTH, True)

# Make the base polygon a randomly generated shape
base_poly = Polygon(util.generate_polygon(center=(x_axis, y_axis),
                                         avg_radius=avg_radius,
                                         irregularity=irregularity,
                                         spikiness=spikiness,
                                         num_vertices=num_vertices,))

# Find starting edge (in this implementation, it just finds the largest edge to start from.
# TODO Allow multiple starting points
# TODO Come up with some way to determine starting edges based on geometry of previous layer
 
p1, p2 = util.longest_edge(base_poly)
starting_line = LineString([p1, p2])

# Copy the base polygon, but exclude the starting (longest) line, turning it from a closed Polygon to an open LineString
boundary_line = LineString(util.get_boundary_line(base_poly, p1))

# Create the first arc
starting_point, r_start, r_farthest = util.get_farthest_point(starting_line, boundary_line, base_poly)
starting_circle = util.create_circle(starting_point.x, starting_point.y, r_start, N)
starting_arc = starting_circle.intersection(base_poly)

# plot base poly
base_poly_geoseries = gpd.GeoSeries(base_poly)
base_poly_geoseries.plot(ax=ax[0], color='white', edgecolor='black', linewidth=1)
base_poly_geoseries.plot(ax=ax[1], color='white', edgecolor='black', linewidth=1)

# plot starting line
starting_line_geoseries = gpd.GeoSeries(starting_line)
starting_line_geoseries.plot(ax=ax[0], color='red', linewidth=2)

# Generate 3d printed starting tower
curr_z = LAYER_HEIGHT  # Height of first layer
with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
    gcode_file.write(f"G1 Z{curr_z} F500\n")
    gcode_file.write(";Generating first layer\n")
    gcode_file.write("G1 E4.25\n")  # Unretract
    
# Fill in circles from outside to inside
while curr_z < BASE_HEIGHT:
    starting_tower_r = r_start + BRIM_WIDTH  
    while starting_tower_r > LINE_WIDTH*2:
        first_layer_circle = util.create_circle(starting_point.x, starting_point.y, starting_tower_r, N)
        util.write_gcode(OUTPUT_FILE_NAME, first_layer_circle, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 2, FEEDRATE*5, close_loop=True)
        starting_tower_r -= LINE_WIDTH*2
    
    curr_z += LAYER_HEIGHT
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")

with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
    gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    gcode_file.write(";Generating tower\n")
    gcode_file.write("M106 S255 ;Turn on fan to max power\n") 
    
while curr_z < OVERHANG_HEIGHT:
    util.write_gcode(OUTPUT_FILE_NAME, starting_line.buffer(LINE_WIDTH), LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 2, FEEDRATE*5, close_loop=True)
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    curr_z += LAYER_HEIGHT

# Create multiple layers
r = LINE_WIDTH
curr_arc = starting_arc
while r < r_start-THRESHOLD:
    # Create a circle based on point location, radius, n
    next_circle = Polygon(util.create_circle(starting_point.x, starting_point.y, r, N))
    # Plot arc
    next_arc = util.create_arc(next_circle, base_poly, ax, depth=0)
    curr_arc = Polygon(next_arc)
    r += LINE_WIDTH
    
    # Write gcode to file
    util.write_gcode(OUTPUT_FILE_NAME, next_arc, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER, FEEDRATE, close_loop=False)
    
    # Create image
    #file_name = util.image_number(image_name_list)   
    #plt.savefig(file_name, dpi=72)
    #image_name_list.append(file_name + ".png")

remaining_empty_space = base_poly.difference(curr_arc)
next_point, longest_distance, _ = util.get_farthest_point(curr_arc, boundary_line, base_poly)

while longest_distance > THRESHOLD + LINE_WIDTH:
    next_arc, remaining_empty_space, image_name_list = util.arc_overhang(curr_arc, boundary_line, N, 
                                                                        remaining_empty_space, next_circle, 
                                                                        THRESHOLD, ax, fig, 1, image_name_list, 
                                                                        R_MAX, LINE_WIDTH, OUTPUT_FILE_NAME,
                                                                        LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER,
                                                                        FEEDRATE)
    next_point, longest_distance, _ = util.get_farthest_point(curr_arc, boundary_line, remaining_empty_space)
"""
# Turn images into gif + MP4
print("Making gif")
with imageio.get_writer('mygif.gif', mode='I', fps=20) as writer:
    for file_name in image_name_list:
        image = imageio.imread(file_name)
        writer.append_data(image)

print("Making movie")
clip = mp.VideoFileClip("output/output_gif.gif")
clip.write_videofile("output/output_video.mp4")
"""
# Build a few layers on top of the overhanging area

for i in range(10):
    util.write_gcode(OUTPUT_FILE_NAME, Polygon(boundary_line).buffer(-THRESHOLD/2), LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER, FEEDRATE*10, close_loop=True)
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z+LAYER_HEIGHT*i)} F500\n")
        
# Write end gcode
with open('input/end.gcode','r') as end_gcode, open(OUTPUT_FILE_NAME,'a') as gcode_file:
    for line in end_gcode:
        gcode_file.write(line)
        
plt.show()
