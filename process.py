import cv2
import os
import numpy as np
from matplotlib import pyplot as plt


def normalize(hulls):
    #hulls = np.concatenate((hull1,hull2),axis=0)
    MIN = np.min(hulls,axis=0)
    MAX = np.max(hulls,axis=0)
    return np.divide(hulls-MIN,MAX-MIN)

def calculate_hull(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    corners = cv2.goodFeaturesToTrack(gray, 100, 0.2, 10)
    corners = np.int0(corners)
    hull = cv2.convexHull(corners)
    return hull

def calculate_width_hull(hull):
    p1,p2 = hull[0:2]
    p1 = p1[0]
    p2 = p2[0]
    return p1[0]-p2[0]

def calculate_height_hull(hull):
    p1,p2 = hull[0:2]
    p1 = p1[0]
    p2 = p2[0]
    return p1[0]-p2[0]

def addZAxis(hull):
    hull = np.squeeze(hull)
    zeros = np.zeros((hull.shape[0],1))
    hull_with_zeros = np.concatenate((hull,zeros),axis=1)
    tmp = np.copy(hull_with_zeros)
    hull_with_zeros[:,1] = tmp[:,2]
    hull_with_zeros[:,2] = tmp[:,1]
    return hull_with_zeros

def rotate_by_90(hull):
    rotation = np.array([
        [1,0,0],
        [0,0,-1],
        [0,1,0]
    ])
    return np.dot(hull,rotation)

def match_front_face(hull_top,hull_side):
    # find lowest face on front
    idx_top = np.sort(np.argsort(hull_top[:,1])[0:2])
    # find part of side that connects to front face (closest z)
    idx_side_front = np.sort(np.argsort(hull_side[:,2])[0:2])
    # connect the side to the front face by connecting their x and y
    hull_side_original = np.copy(hull_side)
    hull_side[idx_side_front,0:2] = hull_top[idx_top,0:2]
    hull_back = np.copy(hull_top)
    idx_side_back = np.where(hull_side[:,2] > 0.9)[0]
    if (len(idx_side_back) > 1):
        idx_side_back = np.array([idx_side_back[0],idx_side_back[-1]])
        scale_x =  np.abs(hull_side_original[idx_side_back[0],0]-hull_side_original[idx_side_back[1],0]) / np.abs(hull_side_original[idx_side_front[0],0]-hull_side_original[idx_side_front[1],0])
        #idx_side_back2 = np.sort(np.argsort(hull_side[:,2])[0:2]
        hull_back *= scale_x
        hull_back[idx_top,2] = hull_side[idx_side_back[::-1],2]
        idx_other = np.delete(np.arange(hull_top.shape[0]),idx_top,axis=0)
        hull_back[idx_other,2] = np.max(hull_side[:,2]) # translate remaining points

    else:
        hull_back[:,2] = hull_side[idx_side_back[0],2]
        hull_back[:,0:2] = np.mean(hull_top[:,0:2],axis=0)

    return hull_top,hull_side,hull_back

def reverse(mlist):
    return mlist[::-1]

def construct_faces(hull_top,hull_back):
    faces = [hull_top.tolist(),hull_back.tolist()]
    center_of_mass = np.mean(hull_top,axis=0)
    num_points = hull_top.shape[0]
    for i in range(hull_top.shape[0]):
        p1 = hull_top[i]
        p2 = hull_top[(i+1)%num_points]
        p3 = hull_back[i]
        p4 = hull_back[(i+1)%num_points]
        if np.all(p3 == p4):
            points = np.array([p1,p3,p2])
        else:
            points = np.array([p1,p3,p4,p2])
        points_cm = np.mean(points,axis=0)

        # check y center of gravity
        if (points_cm[1] < center_of_mass[1]):
            print('Less than')
            faces.append(reverse(points.tolist()))
        else:
            faces.append(points.tolist())
    return faces



def scale_down_faces(faces):
    for i in range(len(faces)):
        for j in range(len(faces[i])):
            face_arr = np.array(faces[i][j])
            face_arr *= 0.05
            faces[i][j] = face_arr.tolist()
    return faces


def create3DFaces(sideHull,frontHull):
    sideHull = normalize(sideHull)
    frontHull = normalize(frontHull)
    sideHull = addZAxis(sideHull)
    frontHull = addZAxis(frontHull)
    frontHull = rotate_by_90(frontHull)
    frontHull,sideHull,hull_back = match_front_face(frontHull,sideHull)
    faces = construct_faces(frontHull,hull_back)
    faces = scale_down_faces(faces)
    return faces

# def get_faces(top_type=0):
#     if (top_type == 3):
#         hull_top = calculate_hull('top.jpg')
#         hull_side = calculate_hull('side.jpg')
#     elif (top_type == 1):
#         hull_top = calculate_hull('top2.jpg')
#         hull_side = calculate_hull('side.jpg')
#     elif (top_type == 2):
#         hull_top = calculate_hull('top.jpg')
#         hull_side = calculate_hull('side2.jpg')
#     elif (top_type == 0):
#         hull_top = calculate_hull('side.jpg')
#         hull_side = calculate_hull('top.jpg')
#     else:
#         hull_top = calculate_hull('top3.jpg')
#         hull_side = calculate_hull('side.jpg')

#     hull_side = normalize(hull_side)
#     hull_top = normalize(hull_top)
#     hull_side = addZAxis(hull_side)
#     hull_top = addZAxis(hull_top)
#     hull_top = rotate_by_90(hull_top)
#     hull_top,hull_side,hull_back = match_front_face(hull_top,hull_side)
#     faces = construct_faces(hull_top,hull_back)
#     faces = scale_down_faces(faces)
#     return faces

# rotate side by 90
# 



# # create hull array for convex hull points
# hull = []
 
# # calculate points for each contour
# for i in range(len(corners)):
#     # creating convex hull object for each contour
#     hull.append(cv2.convexHull(corners[i], False))

# img_cpy = np.copy(img)
# # create an empty black image
# drawing = np.zeros((img_cpy.shape[0], img_cpy.shape[1], 3), np.uint8)
 
# # draw contours and hull points
# for i in range(len(corners)):
#     color_contours = (0, 255, 0) # green - color for contours
#     color = (255, 0, 0) # blue - color for convex hull
#     # draw ith contour
#     # draw ith convex hull object
#     cv2.drawContours(drawing, hull, i, color, 1, 8)

# plt.imshow(drawing)
# plt.show()

# thresh = np.copy(edges)
# lines =  cv2.HoughLinesP(thresh,1,np.pi/180,23,20,5)
# img_cpy = np.copy(img)
# for pt in lines:
#     x1 = pt[0][0]
#     y1 = pt[0][1]
#     x2 = pt[0][2]
#     y2 = pt[0][3]
#     cv2.line(img_cpy,(x1,y1),(x2,y2),(0,0,255),1)

# plt.imshow(img_cpy,cmap='gray')
# plt.show()

# black = np.copy(gray)
# black[black>110] = 255
# dst = cv2.cornerHarris(black,5,10,0.04)
# ret, dst = cv2.threshold(dst,0.1*dst.max(),255,0)
# dst = np.uint8(dst)
# ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
# corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
# print(corners)

# img_cpy = np.copy(img)
# img_cpy[dst>0.1*dst.max()]=[0,0,255]
# plt.imshow(img_cpy)
# plt.show()