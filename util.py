import math
import time
import random
import os
from typing import List, Tuple
import shapely
from shapely.geometry import Point, Polygon, LineString, GeometryCollection
from shapely import affinity
from shapely.ops import split, nearest_points
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

def longest_edge(poly):
    """
    Finds the longest edge in a polygon
    
    Parameters
    ----------
    poly: Polygon
        The polygon that we want to find the longest edge of
        
    Returns
    -------
    start: Point
        First point of the longest edge
    
    end: Point
        Other point of the longest edge    
    """
    poly_coords = list(poly.exterior.coords)
    max_length = 0
    prev_p = Point(poly_coords[-1])
    for p in poly_coords:
        curr_p = Point(p)
        length = curr_p.distance(prev_p)
        if length > max_length:
            max_length = length
            start = prev_p
            end = curr_p

        prev_p = curr_p

    return start, end

def get_farthest_point(arc, base_poly, remaining_empty_space):
    """
    Find the point on a given arc that is farthest away from the base polygon.
    In other words, the point on which the largest circle can be drawn without going outside the base polygon.
    
    Parameters
    ----------
    arc: Polygon
        The arc in question
    
    base_poly: Polygon
        The base polygon
        
    remaining_empty_space: Polygon
        The polygon representing the space left to be filled in the base polygon
            
    ax: matplotlib Axes
        Used for plotting

    fig: matplotlib Figure
        Used for plotting
        
    Returns
    -------
    farthest_point: Point
        The point on the arc that is farthest away from the base polygon
        
    longest_distance: float
        How far away the polygon is from the farthest point
        
    point_on_poly: Point
        The point on the base polygon that is closest to the arc
    """
    longest_distance = 0
    farthest_point = Point([0, 0])

    # Handle input for polygons and LineString
    # The first arc begins on a LineString rather than a Polygon
    if arc.geom_type == 'Polygon':
        arc_coords = arc.exterior.coords
    elif arc.geom_type == 'LineString':
        arc_coords = np.linspace(list(arc.coords)[0], list(arc.coords)[1])
    else:
        print('get_farthest_distance: Wrong shape type given')
        
    # For every point in the arc, find out which point is farthest away from the base polygon
    for p in list(arc_coords):
        distance = Point(p).distance(base_poly)
        if (distance > longest_distance) and ((remaining_empty_space.buffer(1e-9).contains(Point(p)))):
            longest_distance = distance
            farthest_point = Point(p)

    point_on_poly = nearest_points(base_poly, farthest_point)[0]
    return farthest_point, longest_distance, point_on_poly

def move_toward_point(start_point, target_point, distance):
    """Moves a point a set distance toward another point"""

    # Calculate the direction in which to move
    dx = target_point.x - start_point.x
    dy = target_point.y - start_point.y

    # Normalize the direction
    magnitude = (dx**2 + dy**2)**0.5
    dx /= magnitude
    dy /= magnitude

    # Move the point in the direction of the target by the set distance
    return Point(start_point.x + dx*distance, start_point.y + dy*distance)

def get_boundary_line(poly, p1):
    """
    Find the geometry that the arcs will build out to approach.
    In this implementation, it is simply the base_poly without the starting line 
    Arcs cannot start from, or terminate on this line.
    """
    poly_coords = poly.exterior.coords
    for i, p in enumerate(poly_coords):
        # find the starting point in the polygon
        if p == list(p1.coords)[0]:
            # arrange the boundary line so first coordinate is at one end, and the final coordinate is at the end
            base_poly_1 = poly_coords[:i+1]
            base_poly_2 = poly_coords[i+1:]
            base_poly_2 += base_poly_1
            return base_poly_2

def create_circle(x, y, radius, n):
    """
    Create a circle
    - with center at point (x,y)
    - with specified radius
    - using n segments
    """
    return Polygon([[radius*np.sin(theta)+x, radius*np.cos(theta)+y] for theta in np.linspace(0, 2*np.pi - 2*np.pi/n, int(n))])

def create_rect(x, y, length, width, from_center):
    """
    Create a rectangle either from the center or from the bottom-left corner
    """    

    if from_center: 
        return Polygon([(x - width/2, y - length/2),
                        (x - width/2, y + length/2),
                        (x + width/2, y + length/2),
                        (x + width/2, y - length/2)])
    else: 
        return Polygon([(x, y),
                        (x, y + length),
                        (x + width, y + length),
                        (x + width, y)]) 

def image_number(list_of_files):
    if list_of_files:
        return str(int(list_of_files[-1][:-4])+1)
    else:
        return "1"

def get_exterior(poly):

    #extract just the first polygon if there's ever a multipolygon or geometry collection
    for geom in getattr(poly, 'geoms', [poly]):
        if geom.geom_type == 'Polygon':
            poly = geom
            break

    return [
        coord
        for geom in getattr(poly, 'geoms', [poly])
        for coord in geom.exterior.coords
    ]

def create_arc(circle, remaining_empty_space, ax, depth):
    """
    Turns a circle into an arc
    
    Parameters
    ----------
    circle: Polygon
        The circle to convert into an arc
    
    remaining_empty_space: Polygon
        The polygon representing the space left to be filled in the base polygon
        
    ax: matplotlib Axes
        Used for plotting
        
    depth: int
        How deep are we into recursion? Used for rainbow coloring based on depth.
        
    Returns
    -------
    Polygon
        A properly oriented arc shape. (looks like a "D") This will be the path the nozzle takes.
    """
    
    # Turn "moon" shaped arcs into D shapes
    crescent = circle.intersection(remaining_empty_space)
    
    # Remove all the points in the concave section of the crescent shape, turning it into a "D" shape instead
    crescent_exterior = get_exterior(crescent)

    # Plot the arcs. Comment the following 2 lines to make the code run faster
    crescent_geoseries = gpd.GeoSeries(Polygon(crescent_exterior))
    crescent_geoseries.plot(ax=ax[0], color='none', edgecolor='black', linewidth=1) # set color='none' for black and white plotting
    crescent_geoseries.plot(ax=ax[1], color=num_to_rgb(depth), edgecolor='black', linewidth=1) # set color='none' for black and white plotting
    
    empty_exterior = get_exterior(remaining_empty_space)

    arc = []
    for coord in crescent_exterior:
        if (not coord in empty_exterior) and (not coord in arc):
            arc.append(coord)

    if len(arc) == 0:
        print("CIRCLE COMPLETELY ENGULFED")
        return None

    elif len(arc) <= 2:
        arc = Polygon(crescent_exterior).intersection(remaining_empty_space)

    else: 
        arc = Polygon(arc)

    # Make sure first point is on one corner "D", and last point is on the other. 
    # This makes sure the arcs start from one end, and go all the away around to the other

    start, _ = longest_edge(arc)
    fixed_arc = get_boundary_line(arc, start)
                
    return Polygon(fixed_arc) 

def arc_overhang(arc, boundary, starting_line_angle, n, prev_poly, prev_circle, threshold, ax, fig, depth, 
                 filename_list, r_max, min_arcs, line_width, gcode_file, layer_height, filament_diameter, e_multiplier, feedrate):
    """ 
    Main recursive function (I'm deeply sorry for the number of arguments here.)
    
    TODO collapse all the hardcoded parameters into a single parameter
    
    Parameters
    ----------
    circle: Polygon
        The circle to convert into an arc
    
    remaining_empty_space: Polygon
        The polygon representing the space left to be filled in the base polygon
        
    ax: matplotlib Axes
        Used for plotting
        
    depth: int
        How deep are we into recursion? Used for rainbow coloring based on depth.
    """
    # Find the next center point of arc, the radius of the new arc, and the closest point on the boundary to the center point.
    next_point, r_final, _ = get_farthest_point(arc, boundary, prev_poly)
    # Limit maximum circle size
    r_final = min(r_final - threshold, r_max)

    small_arc_radius = 0.5  #1

    # Overlap arc with the previous one. 
    circle_moved = False
    if r_final > small_arc_radius:
        next_point = move_toward_point(next_point, prev_circle.centroid, 0) # change 0 to any distance in mm to move the arcs 
        circle_moved = True
    
    # Update the current boundary polygon to include the previous circle
    remaining_empty_space = prev_poly.difference(prev_circle)    
    
    # Create multiple layers  
    r = line_width
    if r > r_final:
        print("WARNING: r", r, "should not be bigger than r_final", r_final)
        
    while r < r_final:
        # Create a circle based on point location, radius, n
        next_circle = create_circle(next_point.x, next_point.y, r, n)
        next_circle = affinity.rotate(next_circle, starting_line_angle, origin = 'centroid', use_radians=True)
      
        # Plot arc
        next_arc = create_arc(next_circle, remaining_empty_space, ax, depth)
        if not next_arc:
            r += line_width
            continue
        curr_arc = Polygon(next_arc)
        longest_distance = r
        
        #Slow down and reduce flow for all small arcs
        if circle_moved and r < small_arc_radius:
            speed_modifier = 0.25
            e_modifier = 0.25
        elif r <= line_width:
            speed_modifier = 0.25
            e_modifier = 0.1
        else: 
            speed_modifier = 1
            e_modifier = 1

        # Write gcode
        if r_final > 0:    
            write_gcode(gcode_file, next_arc, line_width, layer_height, filament_diameter, e_multiplier*e_modifier, feedrate*speed_modifier, False)
        
        r += line_width
        # Create image
        #filename = image_number(filename_list)   
        #plt.savefig(filename, dpi=200)
        #filename_list.append(filename + ".png")
        
    remaining_empty_space = remaining_empty_space.difference(next_circle)
    
    next_point, longest_distance, _ = get_farthest_point(curr_arc, boundary, remaining_empty_space)
    branch = 0    
    # Create new arcs on the same base arc until no more points on the base arc are farther than the threshold distance.
    while (longest_distance > threshold + min_arcs*line_width): 
        branch += 1

        #Create a new arc on curr_arc
        next_arc, remaining_empty_space, filename_list = arc_overhang(
            curr_arc, boundary, starting_line_angle, n, remaining_empty_space, next_circle, threshold, ax, fig, depth + 1, 
            filename_list, r_max, min_arcs, line_width, gcode_file, layer_height, filament_diameter, e_multiplier, feedrate)

        # Get the farthest distance between curr_arc and the boundary
        next_point, longest_distance, closest_point_on_poly = get_farthest_point(
            curr_arc, boundary, remaining_empty_space)
        
        # Optional: Draw lines showing distance to outer polygon
        #if list(next_point.coords)[0] != (0,0):
        #    nextPointGeoSeries = gpd.GeoSeries(LineString([next_point, closest_point_on_poly]))
        #    nextPointGeoSeries.plot(ax=ax[0], color='green', linewidth=1)

    print("Depth = ", depth, "Arcs this layer", branch)
    return next_arc, remaining_empty_space, filename_list

def write_gcode(file_name, arc, line_width, layer_height, filament_diameter, e_multiplier, feedrate, close_loop):
    ## TODO try using circles instead of D shapes for better surface quality
    ## TODO use a dict or something to reduce # parameters
    #line_width = print_settings["line_width"]
    #layer_height = print_settings["layer_height"]
    #e_multiplier = print_settings["e_multiplier"]
    #filament_diameter = print_settings["filament_diameter"]
    #feedrate = print_settings["feedrate"]    
    feedrate_travel = feedrate * 20
    feedrate_printing = feedrate

    #extract just the first polygon if there's ever a multipolygon or geometry collection
    for geom in getattr(arc, 'geoms', [arc]):
        if geom.geom_type == 'Polygon':
            arc = geom
            break

    with open(file_name, 'a') as gcode_file:
        
        for geom in getattr(arc, 'geoms', [arc]):
            if geom.geom_type == 'LineString':
                coord_list = arc.coords

            elif geom.geom_type == 'Polygon':
                if close_loop == False:
                    coord_list = arc.exterior.coords[:-1]
                else:
                    coord_list = arc.exterior.coords

        first_coord = True    
        prev_coordinate = coord_list[0]
        for coordinate in coord_list:
            if not first_coord and coordinate == prev_coordinate:
                continue
            else: 
                first_coord = False
            # Calculate extrusion amount
            # Extrusion number = height of cylinder with equal volume to amount of filament required
            distance = Point(coordinate).distance(Point(prev_coordinate))
            volume = line_width * layer_height * distance
            e_distance = e_multiplier * volume / (3.1415 * (filament_diameter / 2)**2)

            if e_distance <= 0.0001:
                feedrate = feedrate_travel
                gcode_file.write("G1 E-1 F1500\n") # retract
            else:
                feedrate = feedrate_printing

            gcode_file.write(f"G0 "
                            f"X{'{0:.3f}'.format(coordinate[0])} "
                            f"Y{'{0:.3f}'.format(coordinate[1])} "
                            f"E{'{0:.8f}'.format(e_distance)} "
                            f"F{feedrate*60}\n")

            if e_distance <= 0.000001:
                feedrate = feedrate_travel
                gcode_file.write("G1 E1 F1500\n") # deretract

            prev_coordinate = coordinate
    return

def num_to_rgb(val, max_val=10):
    i = (val * 255 / max_val)
    r = round(math.sin(0.024 * i + 0) * 127 + 128)
    g = round(math.sin(0.024 * i + 2) * 127 + 128)
    b = round(math.sin(0.024 * i + 4) * 127 + 128)
    r /= 256
    g /= 256
    b /= 256
    return (r, g, b)

def generate_polygon(center: Tuple[float, float], avg_radius: float,
                     irregularity: float, spikiness: float,
                     num_vertices: int) -> List[Tuple[float, float]]:
    """
    Start with the center of the polygon at center, then creates the
    polygon by sampling points on a circle around the center.
    Random noise is added by varying the angular spacing between
    sequential points, and by varying the radial distance of each
    point from the centre.

    Args:
        center (Tuple[float, float]):
            a pair representing the center of the circumference used
            to generate the polygon.
        avg_radius (float):
            the average radius (distance of each generated vertex to
            the center of the circumference) used to generate points
            with a normal distribution.
        irregularity (float):
            variance of the spacing of the angles between consecutive
            vertices.
        spikiness (float):
            variance of the distance of each vertex to the center of
            the circumference.
        num_vertices (int):
            the number of vertices of the polygon.
    Returns:
        List[Tuple[float, float]]: list of vertices, in CCW order.
    """
    # Parameter check
    if irregularity < 0 or irregularity > 1:
        raise ValueError("Irregularity must be between 0 and 1.")
    if spikiness < 0 or spikiness > 1:
        raise ValueError("Spikiness must be between 0 and 1.")

    irregularity *= 2 * math.pi / num_vertices
    spikiness *= avg_radius
    angle_steps = random_angle_steps(num_vertices, irregularity)

    # now generate the points
    points = []
    angle = random.uniform(0, 2 * math.pi)
    for i in range(int(num_vertices)):
        radius = clip(random.gauss(avg_radius, spikiness), 0, 2 * avg_radius)
        point = (center[0] + radius * math.cos(angle),
                 center[1] + radius * math.sin(angle))
        points.append(point)
        angle += angle_steps[i]

    return points

def random_angle_steps(steps: int, irregularity: float) -> List[float]:
    """Generates the division of a circumference in random angles.

    Args:
        steps (int):
            the number of angles to generate.
        irregularity (float):
            variance of the spacing of the angles between consecutive vertices.
    Returns:
        List[float]: the list of the random angles.
    """
    # generate n angle steps
    angles = []
    lower = (2 * math.pi / steps) - irregularity
    upper = (2 * math.pi / steps) + irregularity
    cumsum = 0
    for i in range(int(steps)):
        angle = random.uniform(lower, upper)
        angles.append(angle)
        cumsum += angle

    # normalize the steps so that point 0 and point n+1 are the same
    cumsum /= (2 * math.pi)
    for i in range(int(steps)):
        angles[i] /= cumsum
    return angles

def clip(value, lower, upper):
    """
    Given an interval, values outside the interval are clipped to the interval
    edges.
    """
    return min(upper, max(value, lower))