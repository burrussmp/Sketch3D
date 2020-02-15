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

4. Examples of changing up the side and the front.


## Demo Video
A demo video can be found [here](https://drive.google.com/drive/folders/1Ye07AEKM2lWnVQWmO6ogAaoMGznK2UzF?usp=sharing)

## Results
## Example 1
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex1.png)
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex1_3d.png)
## Example 2
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex2.png)
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex2_3d.png)
## Example 3
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex3.png)
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex3_3d.png)
## Example 4
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex4.png)
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex4_3d.png)
## Example 5
![alt text](https://github.com/burrussmp/Augmented-Reality-Sketch-Authoring/blob/master/ex5.png)

Created using the triangle as the side and the square as the front face.

## Discussion

### System
Upon detecting the target image, the client (AR) application requests for information to construct a 3D object. The server processes static images of the front and side faces and produces a description of the faces to construct. This information is sent to the AR application which constructs the 3D object and displays the object. The user can interact with the 3D construction using buttons that allow the user to rotate, scale, and translate the object for better viewing. Once the target image leaves the view of the camera, the 3D object is destroyed. Upon seeing the target again, the server rotates the content being served to the client and displays the next 3D object. Currently, there are four 3D objects created from sketches of the front and side faces shown above.

### Face construction
The most crucial part of the application is the face reconstruction which is performed by the server using openCV image processing. The client constructs the 3D object using a series of co-routines that first communicate to the server to get the information of the object, construct the meshes, and then register the 3D object in the augmented environment.

To construct the faces, the following procedure is followed:

1. Read in image of side and face and gray scale.
2. Use OpenCV good features to track algorithm used to detect corners in an image
3. Use OpenCV convexHull() which performs Sklansky’s algorithm to find the convex hull given a set of points
4. Normalize the dimensions of the side and front convex hull.
5. Add a z axis to the side and front convex hull and then rotate the top by 90 degrees along the x axis.
6. Match the bottom of the front hull which is defined by the two lowest vertices to the closest two vertices of the side.
7. Create the back side which is essentially a copy of the front side, scaled by whatever change occurs in the side, and translated according to the length of the side.
8. Construct the faces so that each face is defined by a set of points in a counter-clock wise direction based on how a viewer would look at the faces where the points are defined by the front and back face of the object.
9. Scale the object down so that it is realistically rendered in unity.


### Limitations

Example 4 above is an example of the limitation. If the feature detector does not sufficiently cover the front face, then it is possible that the 3D model is incorrectly rendered. The above example shows how a lack of detecting points resulted in the 3D reconstruction of an incomplete cylinder.

The system also only supports simple 3D objects and requires that the sketches be provided statically. A server processes the static images and sends the images to the user. The server rotates between displaying a new 3D object each time the target image is detected One major limitation is the type of sides that can be constructed. 

Only sides with four and three points are currently supported (for example a rectangle and a triangle).

## Possible Future Additions
1. Support multiple authored objects
2. Ability to edit the authored models
3. Possibly add textures and colors
4. Add the ability to make things hollow using marks like 'H' on the object
5. Add properties to objects like friction
6. Dynamically process images and not just serve static content.
7. Use a segmentation neural network to detect corners.

# Citations
[1] Banu, Simona Maria. "Augmented Reality system based on sketches for geometry education." 2012 International Conference on E-Learning and E-Technologies in Education (ICEEE). IEEE, 2012.

[2] Bergig, Oriel, et al. "In-place 3D sketching for authoring and augmenting mechanical systems." 2009 8th IEEE International Symposium on Mixed and Augmented Reality. IEEE, 2009.
