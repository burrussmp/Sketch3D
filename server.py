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
from AnnotationSegmentation import *
# run me
# adb -s FA7911A00779 logcat -s Unity ActivityManager PackageManager dalvikvm DEBUG

class Processor():
    def __init__(self):
        self.model = generate_model(pathToModel='./weights2.pt')
        self.material = {
            "colorside":'0',
            "colorfront":'0',
            "textureside":'0',
            "texturefront":'0',
            "special":'0'
        }
        self.side = None
        self.front = None
        self.sideMask = None
        self.frontMask = None
        self.sensitivityFront = None
        self.sensitivitySide = None

    def ready_to_send(self):
        return self.side is not None and self.front is not None
    def message(self):
        message = ''
        if self.side is not None:
            message += '1'
        else:
            message += '0'
        if self.front is not None:
            message += '1'
        else:
            message += '0'
        return message

    def set_image(self,type,img):
        if type == 'Side':
            self.side = img
        elif type == 'Front':
            self.front = img
        else:
            raise ValueError('Type {} is undefined'.format(type))

    def set_mask(self,type,mask):
        if type == 'Side':
            self.sideMask = mask
        elif type == 'Front':
            self.frontMask = mask
        else:
            raise ValueError('Type {} is undefined'.format(type))

    def set_sensitivity(self,type,sensitivity):
        if type == 'Side':
            self.sensitivitySide = sensitivity
        elif type == 'Front':
            self.sensitivityFront = sensitivity
        else:
            raise ValueError('Type {} is undefined'.format(type))

    def check_around(self,mask,idx):
        dist = 10
        maxY = mask.shape[0]
        maxX = mask.shape[1]
        x,y = idx[1],idx[0]
        small_x = max(0,x-dist)
        big_x = min(x+dist,maxX)
        small_y = max(0,y-dist)
        big_y = min(y+dist,maxY)
        return np.any(mask[small_x:big_x,small_y:big_y]==1)

    def draw_on_image(self,img,hull):
        cpy_img = np.copy(img)
        for i in range(hull.shape[0]):
            radius = 10
            x = hull[i,0,0]
            y = hull[i,0,1]
            cv2.circle(cpy_img,(x,y), radius, (0,0,255), -1)
        plt.imshow(cpy_img,cmap='gray')
        plt.show(block=False)

    def applyMaskToHull(self,mask,hull,img):
        if mask is not None:
            remove = []
            for i in range(hull.shape[0]):
                idx = hull[i,0,:]
                for j in range(mask.shape[0]):
                    cur_mask = cv2.resize(mask[j].astype('float32'),(img.shape[0],img.shape[1]))
                    if (self.check_around(cur_mask,idx)):
                        remove.append(i)
            hull = np.delete(hull,remove,axis=0)
        return hull

    def get_faces(self):
        side = self.side
        sideMask = self.sideMask
        sideHull = calculate_hull(side,self.sensitivitySide)
        sideHull = self.applyMaskToHull(sideMask,sideHull,side)
        sideHull[:,:,1] = side.shape[1] - sideHull[:,:,1]
        sideHull = cv2.convexHull(sideHull)

        front = self.front
        frontMask = self.frontMask
        frontHull = calculate_hull(front,self.sensitivityFront)
        frontHull = self.applyMaskToHull(frontMask,frontHull,front)
        frontHull[:,:,1] = front.shape[1] - frontHull[:,:,1]
        faces = create3DFaces(sideHull,frontHull)
        return faces

    def updateMaterial(self,typeOfImage,predictions):
        for i in range(predictions.shape[0]):
            prediction = predictions[i]
            if prediction in ['R','G','B']:
                self.material['{}{}'.format('color',typeOfImage.lower())] = prediction
            elif prediction in ['U','S']:
                self.material['{}{}'.format('texture',typeOfImage.lower())] = prediction
            elif prediction in ['H']:
                self.material['special'] = prediction

    def clearMaterial(self,typeOfImage):
        self.set_image(typeOfImage,None)
        self.set_mask(typeOfImage,None)
        self.set_sensitivity(typeOfImage,0.25)
        self.material['{}{}'.format('color',typeOfImage.lower())] = '0'
        self.material['{}{}'.format('texture',typeOfImage.lower())] = '0'

    def clearAll(self):
        self.clearMaterial('Front')
        self.clearMaterial('Side')
        self.material['special'] = '0'

    def crop(self,img,x,width,y,height):
        crop_img = img[y:y+height, x:x+width]
        return crop_img

    def processImage(self,typeOfImage):
        if typeOfImage == 'Side':
            cropped_img = self.side
        elif typeOfImage == 'Front':
            cropped_img = self.front
        else:
            raise ValueError('Type {} not supported'.format(typeOfImage))
        assert cropped_img is not None,\
            print('The side {} has not been defined...ERROR'.format(typeOfImage))
        
        seg_img = cv2.resize(cropped_img,(128,128),interpolation=cv2.INTER_AREA)
        mask,prediction = predict_segmentation(self.model,seg_img,typeOfImage)
        if 'C' in prediction:
            print('Clearing everything...')
            self.clearAll()
        else:
            sensitivities = [ 0.25,0.1,0.3,0.05,0.4]
            selected_sensitivity = None
            for sensitivity in sensitivities:
                hull = calculate_hull(cropped_img,sensitivity)
                remove = []
                hull = self.applyMaskToHull(mask,hull,cropped_img)
                self.draw_on_image(cropped_img,hull)
                isAcceptable = input('Enter Y if acceptable for the '+typeOfImage+'?\t\t').lower() == 'y'
                plt.close()
                if isAcceptable:
                    selected_sensitivity = sensitivity
                    break
            if isAcceptable:
                self.set_sensitivity(typeOfImage,selected_sensitivity)
                if (mask.shape[0] != 0):
                    self.set_mask(typeOfImage,mask)
                    self.updateMaterial(typeOfImage,prediction)
                else:
                    self.clearMaterial(typeOfImage)
            else:
                self.clearMaterial(typeOfImage)
            

class Handler(http.server.BaseHTTPRequestHandler): 
    def get_mesh(self):
        if processor.ready_to_send():
            faces = processor.get_faces()
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

    def get_annotation_data(self):
        self.send_response(200)
        self.send_header("Content-type", "text")
        self.end_headers()
        message = 'colorside={};colorfront={};textureside={};texturefront={};special={};'.format(processor.material['colorside']
            ,processor.material['colorfront']
            ,processor.material['textureside']
            ,processor.material['texturefront']
            ,processor.material['special'])
        print(message)
        self.wfile.write(message.encode())
    
    def do_GET(self):
        if self.path == '/data':
            self.get_mesh()
        elif self.path == '/annotation':
            self.get_annotation_data()
    
    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
            # typeOfImage = form["Type"].value + '.png'
            bbox = {
                'x':int(form["x"].value),
                'y':int(form["y"].value),
                'width':int(form["width"].value),
                'height':int(form["height"].value)
            }
            try:
                byteThings = b""
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        #open("./%s"%name, "wb").write(record.file.read())
                        byteThings += record.file.read()
                else:
                    #open("./%s"%name, "wb").write(form["file"].file.read())
                    byteThings += form["file"].file.read()
                nparr = np.fromstring(byteThings, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cropped_img = processor.crop(img,bbox['x'],bbox['width'],bbox['y'],bbox['height'])
                processor.set_image(form["Type"].value,cropped_img)
                
            except IOError:
                    return (False, "Can't create file to write, do you have permission to write?")
        return (True, "Files uploaded",form["Type"].value)
    
    def do_POST(self):        
        r, info,typeOfImage = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        processor.processImage(typeOfImage)
        f = io.BytesIO()
        message = ''
        if r:
            self.send_response(200)
            self.end_headers()
            message = processor.message()
        else:
            self.send_response(500)
            self.end_headers()
            message = 'error'
        f.write(message.encode())
        self.wfile.write(f.getvalue())
        f.close() 


processor = Processor()
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



# import http.server
# import socketserver
# import time
# from process import *
# import json
# import urllib.parse
# import io
# from PIL import Image
# import base64
# import io
# import cgi
# import matplotlib.pyplot as plt
# from AnnotationSegmentation import *
# # run me
# # adb -s FA7911A00779 logcat -s Unity ActivityManager PackageManager dalvikvm DEBUG

# collected = ['1','1']
# model = generate_model(pathToModel='./weights2.pt')
# material = {
#     "colorside":'R',
#     "colorfront":'0',
#     "textureside":'0',
#     "texturefront":'0',
#     "special":'0'
# }


# def check_around(mask,idx):
#     dist = 10
#     maxY = mask.shape[0]
#     maxX = mask.shape[1]
#     x,y = idx[1],idx[0]
#     small_x = max(0,x-dist)
#     big_x = min(x+dist,maxX)
#     small_y = max(0,y-dist)
#     big_y = min(y+dist,maxY)
#     return np.any(mask[small_x:big_x,small_y:big_y]==1)

# def draw_on_image(img,hull):
#     cpy_img = np.copy(img)
#     for i in range(hull.shape[0]):
#         radius = 4
#         x = hull[i,0,0]
#         y = hull[i,0,1]
#         cv2.circle(cpy_img,(x,y), radius, (0,0,255), -1)
#     plt.imshow(cpy_img,cmap='gray')
#     plt.show(block=False)

# def get_faces():
#     side = cv2.imread('./Side.png')
#     sideHull = calculate_hull(side,'Side')
#     if os.path.isfile('./mask_Side.npy'):
#         mask = np.load('./mask_Side.npy')
#         remove = []
#         for i in range(sideHull.shape[0]):
#             idx = sideHull[i,0,:]
#             for j in range(mask.shape[0]):
#                 cur_mask = cv2.resize(mask[j].astype('float32'),(side.shape[0],side.shape[1]))
#                 if (check_around(cur_mask,idx)):
#                     remove.append(i)
#         sideHull = np.delete(sideHull,remove,axis=0)
#     sideHull[:,:,1] = side.shape[1] - sideHull[:,:,1]
#     sideHull = cv2.convexHull(sideHull)
#     front = cv2.imread('./Front.png')
#     frontHull = calculate_hull(front,'Front')
#     if os.path.isfile('./mask_Front.npy'):
#         mask = np.load('./mask_Front.npy')
#         remove = []
#         for i in range(frontHull.shape[0]):
#             idx = frontHull[i,0,:]
#             for j in range(mask.shape[0]):
#                 cur_mask = cv2.resize(mask[j].astype('float32'),(front.shape[0],front.shape[1]))
#                 if (check_around(cur_mask,idx)):
#                     remove.append(i)
#         frontHull = np.delete(frontHull,remove,axis=0)
#     frontHull = cv2.convexHull(frontHull)
#     frontHull[:,:,1] = front.shape[1] - frontHull[:,:,1]
#     faces = create3DFaces(sideHull,frontHull)
#     print(len(faces))
#     return faces

# def updateMaterial(typeOfImage,predictions):
#     print('Updating',predictions,'for',typeOfImage)
#     for i in range(predictions.shape[0]):
#         prediction = predictions[i]
#         lower_type = typeOfImage.lower()
#         if prediction in ['R','G','B']:
#             material['{}{}'.format('color',lower_type)] = prediction
#         elif prediction in ['U','S']:
#             material['{}{}'.format('texture',lower_type)] = prediction
#         elif prediction in ['H']:
#             material['special'] = prediction

# def clearMaterial(typeOfImage):
#     if os.path.isfile('.mask_/{}.npy'.format(typeOfImage)):
#         os.remove('./mask_{}.npy'.format(typeOfImage))
#     lower_type = typeOfImage.lower()
#     material['{}{}'.format('color',lower_type)] = '0'
#     material['{}{}'.format('texture',lower_type)] = '0'

# def clearAll():
#     clearMaterial('Front')
#     clearMaterial('Side')
#     material['special'] = '0'
#     collected = ['0','0']

# def crop(img,x,width,y,height):
#     crop_img = img[y:y+height, x:x+width]
#     return crop_img

# def checkIfAcceptable(typeOfImage):
#     # do segmentation
#     cropped_img = cv2.imread('./{}.png'.format(typeOfImage))
#     seg_img = cv2.resize(cropped_img,(128,128),interpolation=cv2.INTER_AREA)
#     mask,prediction = predict_segmentation(model,seg_img,typeOfImage)
#     if 'C' in prediction:
#         print('Clearing everything...')
#         clearAll()
#     else:
#         hull = calculate_hull(cropped_img,typeOfImage)
#         remove = []
#         for i in range(hull.shape[0]):
#             idx = hull[i,0,:]
#             for j in range(mask.shape[0]):
#                 cur_mask = cv2.resize(mask[j].astype('float32'),(cropped_img.shape[0],cropped_img.shape[1]))
#                 if (check_around(cur_mask,idx)):
#                     remove.append(i)
#         hull = np.delete(hull,remove,axis=0)
#         cpy_img = np.copy(cropped_img)
#         for i in range(hull.shape[0]):
#             radius = 10
#             x = hull[i,0,0]
#             y = hull[i,0,1]
#             cv2.circle(cpy_img,(x,y), radius, (0,0,255), -1)

#         fig = plt.figure()
#         plt.imshow(cv2.cvtColor(cpy_img, cv2.COLOR_BGR2RGB))
#         plt.show(block=False)
#         isAcceptable = input('Enter Y if acceptable for the '+typeOfImage+'?\t\t').lower() == 'y'
#         if isAcceptable:
#             if (mask.shape[0] != 0):
#                 print('Saving mask:',mask.shape)
#                 np.save('./mask_{}.npy'.format(typeOfImage),mask)
#                 updateMaterial(typeOfImage,prediction)
#             else:
#                 clearMaterial(typeOfImage)
#             if typeOfImage == 'Side':
#                 collected[0] = '1'
#             elif typeOfImage == 'Front':
#                 collected[1] = '1'
#         plt.close()
# class Handler(http.server.BaseHTTPRequestHandler):

#     def get_mesh(self):
#         if "".join(collected) == '11':
#             faces = get_faces()
#             #counter = (counter + 1) % 5
#             """Respond to a GET request."""
#             self.send_response(200)
#             self.send_header("Content-type", "text")
#             self.end_headers()
#             for i in range(len(faces)):
#                 self.wfile.write("N".encode())
#                 self.wfile.write(str(len(faces[i])).encode())
#                 self.wfile.write(",".encode())
#                 for j in range(len(faces[i])):
#                     self.wfile.write(json.dumps(faces[i][j]).encode())
#                     if j != len(faces[i])-1:
#                         self.wfile.write(",".encode())
#         else:
#             self.send_response(500)
#             self.send_header("Content-type", "text")
#             self.end_headers()
#             self.wfile.write("Error: Do not have enough pictures to construct 3D object.".encode())
#     def get_annotation_data(self):
#         self.send_response(200)
#         self.send_header("Content-type", "text")
#         self.end_headers()
#         message = 'colorside={};colorfront={};textureside={};texturefront={};special={};'.format(material['colorside']
#             ,material['colorfront']
#             ,material['textureside']
#             ,material['texturefront']
#             ,material['special'])
#         print(message)
#         self.wfile.write(message.encode())
    
#     def do_GET(self):
#         if self.path == '/data':
#             self.get_mesh()
#         elif self.path == '/annotation':
#             self.get_annotation_data()
    
#     def deal_post_data(self):
#         ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
#         pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
#         pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
#         if ctype == 'multipart/form-data':
#             form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
#             print (type(form))
#             name = form["Type"].value + '.png'
#             bbox = {
#                 'x':int(form["x"].value),
#                 'y':int(form["y"].value),
#                 'width':int(form["width"].value),
#                 'height':int(form["height"].value)
#             }
#             try:
#                 byteThings = b""
#                 if isinstance(form["file"], list):
#                     for record in form["file"]:
#                         #open("./%s"%name, "wb").write(record.file.read())
#                         byteThings += record.file.read()
#                 else:
#                     #open("./%s"%name, "wb").write(form["file"].file.read())
#                     byteThings += form["file"].file.read()
#                 nparr = np.fromstring(byteThings, np.uint8)
#                 print(nparr)
#                 data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#                 print('data type:',type(data),'shape:',data.shape)
#                 img = cv2.imread("./%s"%name)
#                 cropped_img = crop(img,bbox['x'],bbox['width'],bbox['y'],bbox['height'])
#                 cv2.imwrite("./%s"%name,cropped_img)
                
#             except IOError:
#                     return (False, "Can't create file to write, do you have permission to write?")
#         return (True, "Files uploaded",form["Type"].value)
    
#     def do_POST(self):        
#         r, info,typeOfImage = self.deal_post_data()
#         print(r, info, "by: ", self.client_address)
#         checkIfAcceptable(typeOfImage)
#         f = io.BytesIO()
#         message = ''
#         if r:
#             self.send_response(200)
#             self.end_headers()
#             message = "".join(collected)
#         else:
#             self.send_response(500)
#             self.end_headers()
#             message = 'error'
#         f.write(message.encode())
#         self.wfile.write(f.getvalue())
#         f.close() 



# if __name__ == '__main__':
#     HOST_NAME = "10.0.0.118"
#     PORT_NUMBER = 8080
#     httpd = socketserver.TCPServer((HOST_NAME, PORT_NUMBER), Handler)
#     print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     httpd.shutdown()
#     print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))


#     # int next = 0;
#     # var list = new List<float>();
#     # while (next != -1){
#     #   int start = inputTextString.IndexOf('N',next);
#     #   int num_delimiter = inputTextString.IndexOf(',',start);
#     #   next = inputTextString.IndexOf('N',start+1);
#     #   int num_samples = Int16.Parse(inputTextString.Substring(start+1,num_delimiter-start-1));
#     #   Console.WriteLine(num_samples);
#     #   if (next != -1){
#     #     string sub_input = inputTextString.Substring(num_delimiter+1,next-num_delimiter-1);
#     #     sub_input = sub_input.Replace("[","");
#     #     sub_input = sub_input.Replace("]","");
#     #      var myList = sub_input.Split(',').Select(Convert.ToSingle).ToList();
#     #      list.add(myList);

#     #   }
#     # }