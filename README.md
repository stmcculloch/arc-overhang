# arc-overhang

A 3D printer slicing algorithm that lets you print 90° overhangs without support material. 

## Brief Description
Essentially you need to know 3 things:  
1. You can print 90° overhangs by wrapping filament around itself in concentric **arcs**. You may have seen the [fullcontrol.xyz overhang challenge](https://fullcontrol.xyz/#/models/b70938). This uses the exact same principle.

![fullcontrol overhang challenge](examples\fullcontrol_overhang_challenge.jpg)

2. You can start an **arc** on an **arc** .

![arc starting on another arc](examples/arc_on_arc.jpg)

3. Recursively print arcs until the space is filled. This can be used to print almost any artibtrary shape:
   
![arc starting on another arc](examples/arbitrary_shape.jpg)

This is what the algorithm looks like: 

![arc-overhang visualization](examples\gcode_vis3.gif)

## Motivation

Earlier this year, I accidentally discovered you can print an overhang that supports itself. I was just messing around with printing into thin air to see what happens. Here's the print that started it all: 

![accidental discovery](examples/accidental_discovery.jpg)

Then I tried to recreate the effect on purpose

![first attempts](examples\early_work_2.png)

And fine tune it: 

![first attempts2](examples\early_work_1.png)

Here's what this effect looks like while printing:  

![printing demo](examples/printing_demo.gif)