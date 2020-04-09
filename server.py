import http.server
import socketserver
import time
from process import *
import json
import urllib.parse
import io
from PIL import Image
import base64
import io
import cgi
import matplotlib.pyplot as plt
# run me
# adb -s FA7911A00779 logcat -s Unity ActivityManager PackageManager dalvikvm DEBUG

#counter = 0
collected = ['0','0']
img = None
hull = None



# def onclick(event):
#     global img,hull
#     print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
#           ('double' if event.dblclick else 'single', event.button,
#            event.x, event.y, event.xdata, event.ydata))
#     if (event.dblclick): # any double click will attempt to remove
#         p1 = np.expand_dims(np.array([[event.x,event.y ]]),axis=0)
#         dist = np.linalg.norm(p1-hull,axis=2)
#         idx = np.argmin(dist)
#         if dist[idx]< 5:
#             hull = np.delete(hull,idx,axis=0)
#             print('deleting...')
#     elif (event.button == 3): # right-click
#         print('adding')
#         p1 = np.expand_dims(np.array([[event.x,event.y ]]),axis=0)
#         corners = np.concatenate((hull,p1),axis=0)
#         hull = cv2.convexHull(corners)
#     print(hull)
#     cpy_img = np.copy(img)
#     for i in range(hull.shape[0]):
#         radius = 5
#         x = hull[i,0,0]
#         y = hull[i,0,1]

#         cv2.circle(cpy_img,(x,y), radius, (0,255,0), -1)
#     plt.clf()
#     plt.imshow(cv2.cvtColor(cpy_img, cv2.COLOR_BGR2RGB))

def get_faces():
    front = cv2.imread('./Front.png')
    side = cv2.imread('./Side.png')
    sideHull = calculate_hull(side)
    sideHull[:,:,1] = side.shape[1] - sideHull[:,:,1] 
    frontHull = calculate_hull(front)
    frontHull[:,:,1] = front.shape[1] - frontHull[:,:,1]
    # sideHull = np.load('./Side.npy')
    # frontHull = np.load('./Front.npy')
    faces = create3DFaces(sideHull,frontHull)
    return faces

def crop(img,x,width,y,height):
    crop_img = img[y:y+height, x:x+width]
    return crop_img

def checkIfAcceptable(cropped_img,typeOfImage):
    global hull,img
    hull = calculate_hull(cropped_img)
    img = cropped_img
    cpy_img = np.copy(cropped_img)
    for i in range(hull.shape[0]):
        radius = 5
        x = hull[i,0,0]
        y = hull[i,0,1]
        cv2.circle(cpy_img,(x,y), radius, (0,255,0), -1)
    fig = plt.figure()
    plt.imshow(cv2.cvtColor(cpy_img, cv2.COLOR_BGR2RGB))
    # cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show(block=False)
    isAcceptable = input('Enter Y if acceptablefor the '+typeOfImage+' side?\t\t').lower() == 'y'
    if isAcceptable and typeOfImage == 'Side':
        collected[0] = '1'
    elif isAcceptable and typeOfImage == 'Front':
        collected[1] = '1'
    #hull = cpy_img.shape[1] - hull[:,:,1]
    #np.save('./'+typeOfImage+'.npy',hull)
    #fig.canvas.mpl_disconnect(cid)
    plt.close()
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        #global counter
        if "".join(collected) == '11':
            faces = get_faces()
            #counter = (counter + 1) % 5
            """Respond to a GET request."""
            self.send_response(200)
            self.send_header("Content-type", "text")
            self.end_headers()
            for i in range(len(faces)):
                self.wfile.write("N".encode())
                self.wfile.write(str(len(faces[i])).encode())
                self.wfile.write(",".encode())
                for j in range(len(faces[i])):
                    self.wfile.write(json.dumps(faces[i][j]).encode())
                    if j != len(faces[i])-1:
                        self.wfile.write(",".encode())
        else:
            self.send_response(500)
            self.send_header("Content-type", "text")
            self.end_headers()
            self.wfile.write("Error: Do not have enough pictures to construct 3D object.".encode())
        return
    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
            print (type(form))
            name = form["Type"].value + '.png'
            bbox = {
                'x':int(form["x"].value),
                'y':int(form["y"].value),
                'width':int(form["width"].value),
                'height':int(form["height"].value)
            }
            print(bbox)
            try:
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        open("./%s"%name, "wb").write(record.file.read())
                else:
                    open("./%s"%name, "wb").write(form["file"].file.read())
                img = cv2.imread("./%s"%name)
                cropped_img = crop(img,bbox['x'],bbox['width'],bbox['y'],bbox['height'])
                cv2.imwrite("./%s"%name,cropped_img)
            except IOError:
                    return (False, "Can't create file to write, do you have permission to write?")
        return (True, "Files uploaded",form["Type"].value,cropped_img)
    
    def do_POST(self):        
        r, info,typeOfImage,cropped_img = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        checkIfAcceptable(cropped_img,typeOfImage)
        f = io.BytesIO()
        message = ''
        if r:
            self.send_response(200)
            self.end_headers()
            message = "".join(collected)
        else:
            self.send_response(500)
            self.end_headers()
            message = 'error'
        f.write(message.encode())
        self.wfile.write(f.getvalue())
        f.close() 



if __name__ == '__main__':
    HOST_NAME = "10.0.0.118"
    PORT_NUMBER = 8080
    httpd = socketserver.TCPServer((HOST_NAME, PORT_NUMBER), Handler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.shutdown()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))


    # int next = 0;
    # var list = new List<float>();
    # while (next != -1){
    #   int start = inputTextString.IndexOf('N',next);
    #   int num_delimiter = inputTextString.IndexOf(',',start);
    #   next = inputTextString.IndexOf('N',start+1);
    #   int num_samples = Int16.Parse(inputTextString.Substring(start+1,num_delimiter-start-1));
    #   Console.WriteLine(num_samples);
    #   if (next != -1){
    #     string sub_input = inputTextString.Substring(num_delimiter+1,next-num_delimiter-1);
    #     sub_input = sub_input.Replace("[","");
    #     sub_input = sub_input.Replace("]","");
    #      var myList = sub_input.Split(',').Select(Convert.ToSingle).ToList();
    #      list.add(myList);

    #   }
    # }