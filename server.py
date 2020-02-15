import http.server
import socketserver
import time
from process import *
import json

counter = 0
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global counter
        faces = get_faces(counter)
        counter = (counter + 1) % 5
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
        #self.wfile.write(triangles.encode())
        return


if __name__ == '__main__':
    HOST_NAME = "10.66.129.3"
    PORT_NUMBER = 8080
    httpd = socketserver.TCPServer((HOST_NAME, PORT_NUMBER), Handler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
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