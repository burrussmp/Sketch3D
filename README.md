# Augmented-Reality-Sketch-Authoring
**Proposal:** Begin replicating Bergig et al. 2009 approach to authoring 3D objects by sketching basic geometric shapes.
## Background
Sketch based authoring allows a user to add elements, modify existing elements, and manipulate 3D models using sketches which are automatically rendered as 3D objects.

![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/example.png)

The application has four main components

1. Image understanding: Enhances the input image and converts it into its vector-based representations
2. Structure Reconstruction: 3D reconstruction based on vector-representation
3. Scene Composition: Create the virtual scene
4. Augment: Augment the virtual scene with the physical properties

## Assignment 2 Objectives
My goal is to build the basic components above for a single object.

1. Allow a user to draw a simple object like a ramp or cube
2. Allow the user to scale, rotate, or translate the AR model by interacting in AR
3. Allow simple annotations like color

### Image Understanding
Requires image enhacement, object recognition, annotation recognition, stroke interpretation
### Structure Reconstruction
2D beautification, geoemtric reconstruction, 3D beauitfication
### Scene Composition
Model composition and simulation composition

## Possible Future Additions
1. Support multiple authored objects
2. Ability to edit the authored models
3. Possibly add textures and colors
4. Add the ability to make things hollow using marks like 'H' on the object
5. Add properties to objects like friction




# Citations
Bergig, Oriel, et al. "In-place 3D sketching for authoring and augmenting mechanical systems." 2009 8th IEEE International Symposium on Mixed and Augmented Reality. IEEE, 2009.
