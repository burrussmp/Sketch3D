# Augmented-Reality-Sketch-Authoring
**Proposal:** Begin replicating approach to authoring 3D objects by sketching basic geometric shapes [1]. To do so, I have developed a simpler version based on [2] where a pre-drawn "front" and "side" face sketch are used to reconstruct a 3D object. The information necessary to construct the 3D object is done offline by a server code written in Python. The server sends the information to construct the 3D object to an phone running the AR application which creates the 3D object. Whenever the target image is detected by the AR application, the 3D object is constructed. The user is also presented with various functionality to scale, rotate, and translate the object for better viewing. These functionalities are controlled by button's on the phone screen.

## Background
Sketch based authoring allows a user to add elements, modify existing elements, and manipulate 3D models using sketches which are automatically rendered as 3D objects.

![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/example.png)

The application has four main components

1. Image understanding: Enhances the input image and converts it into its vector-based representations
2. Structure Reconstruction: 3D reconstruction based on vector-representation
3. Scene Composition: Create the virtual scene
4. Augment: Augment the virtual scene with the physical properties

## Assignment 2 Accomplishments

1. Python server that is able to process 2 drawn images of the front and side face of the geometric object we would like to construct.

2. AR application written in Unity to construct the 3D object and communicate to the python server as the client.

3. Button interface to interact with the 3D constructed image (rotate, scale, and translate).


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
[1] Banu, Simona Maria. "Augmented Reality system based on sketches for geometry education." 2012 International Conference on E-Learning and E-Technologies in Education (ICEEE). IEEE, 2012.

[2] Bergig, Oriel, et al. "In-place 3D sketching for authoring and augmenting mechanical systems." 2009 8th IEEE International Symposium on Mixed and Augmented Reality. IEEE, 2009.
