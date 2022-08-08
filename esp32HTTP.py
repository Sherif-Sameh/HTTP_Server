# Author's Name: Eng. Sherif Sameh
#
# This script, esp32HTTP, builds on the existing Python http.server library
# by extending the defined class BaseHTTPRequestHandler to redefine the
# methods used by the server to respond to HTTP methods like the GET and
# POST methods to achieve the required behavior for this simple HTTP server.

# Import the http specfic classes, os library for general operating system
# operations and shutil for copying data between files.
from http.server import HTTPServer, BaseHTTPRequestHandler
import os 
import shutil

class HTTPHandler(BaseHTTPRequestHandler):
	
	# Instance variables for keeping track of clients' IPs and data Files 
	clients_list = [] 
	files_list = []
	
	# Method for checking for new clients and registering them in the lists if new,
	# Returns the index of the client, wether new or not, in the lists. 
	def register_client(self):
		address = self.address_string()
		try:
			index = self.clients_list.index(address)
			return index
		except ValueError: # Raised when IP is not found in the list, i.e. New Client.
			self.clients_list.append(address)
			f = open("Client{}.txt".format(len(self.clients_list)),"wb") # Write (Binary mode).
			f.write("Client's IP Address: {}\r\n\n\n".format(address).encode("utf-8"))
			self.files_list.append(f)
			return len(self.clients_list)-1
	
	# Called when the user stops the server to close all open files.	
	def	close_all_files(self):
		for x in self.files_list:
			x.close()
	
	# Gets the list of files in the current directory, cleans it of all the files 
	# starting in "." like .settings and the actual .py file and returns it sorted.
	def list_directory(self):
		path = os.getcwd()
		dir_list = os.listdir(path)
		# lamda defines a function a.lower() to be used as key when sorting to prevent
		# the lower and uppercase lettering from messing up the order of files in the list.
		dir_list.sort(key = lambda a: a.lower())
		#reversed is used to loop in reverse order as to not cause an index out of bounds exception
		for name in reversed(dir_list):
			if(name.startswith(".") or (name == 'esp32HTTP.py')):
				dir_list.remove(name)
		return dir_list
	
	# Called by GET method when the path is not an empty one, indicating a request for
	# a file has been made. When called it will close the chosen file to change its mode to
	# reading(binary mode) to be copied into the writing buffer then reopen it in append mode(binary mode).
	def copy_file(self, index, outputfile):
		file_name = self.files_list[index].name
		self.files_list[index].close()
		self.files_list[index] = open(file_name, "rb")
		shutil.copyfileobj(self.files_list[index] , outputfile)
		self.files_list[index].close()
		self.files_list[index] = open(file_name, "ab")
	
	# Extracts the needed file's name from the message path variable and sends the neccesary
	# headers for the HEAD and GET Methods.	
	def handle_file_headers(self, file_path):
		# Extracting the file's name
		file_path = file_path.split('.')[0]
		index = ''
		for i in reversed(range(len(file_path))):
			if((file_path[i] > '9') or (file_path[i] < '0')):
				break
			index = file_path[i] + index
		index = int(index) - 1
		f = self.files_list[index]
		fs = os.fstat(f.fileno())
		
		# Sending the headers.
		self.send_header("Content-type","text/plain")
		self.send_header("Content-Length", str(fs[6]))
		self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
		self.end_headers()
		return index
	
	# Common method shared by both GET and HEAD methods to update the clients' list,
	# send the neccesary headers whether it's an empty GET request or one requesting a
	# file, to flush the writing buffer and update the page incase of an empty GET (Refresh)
	# Returns the index of the file in files_list or -1 for an empty GET request.			
	def send_head(self, file_path):
		self.register_client()
		num_of_clients = len(self.clients_list)
		print('No of Clients = {}'.format(num_of_clients))
		print(self.clients_list)
		self.send_response(200)
		
		if(len(file_path) > 1):
			return self.handle_file_headers(file_path)
		
		# For an Empty GET request
		self.send_header("Content-type","text/html")
		self.end_headers()
		
		dir_list = self.list_directory()
		self.wfile.write(bytes('\
		<html>\
			<title>\
				ESP32 Local HTTP Server\
			</title>\
			<body>\
				<h1 style="font-size:2vw">\
					<center>\
						HTTP Server<br><br>Number of Clients is {}\
					</center>\
				</h1>\
				<h2 style="font-size:1.7vw">\
					Directory List:\
					<p style="font-size:1.3vw">'.format(num_of_clients),'utf-8'))
		for dir_file in dir_list:
			self.wfile.write(bytes('\
						<a href="/{}">\
							Client{}\
						</a><br><br>'.format(dir_file,dir_list.index(dir_file)+1),'utf-8'))
		self.wfile.write(bytes('\
					</p>\
				</h2>\
			</body>\
		</html>','utf-8'))
		return -1
		
	# Redefining the GET method for handling both empty and file GET requests.				
	def do_GET(self):
		self.wfile.flush()
		index = self.send_head(self.path)
		if(index >= 0):
			self.copy_file(index, self.wfile)
	
	# Shares most of the GET method's procedures except for actually copying the files.		
	def do_HEAD(self):
		self.send_head(self.path)
	
	# Receives the POST request from the input (read) buffer by reading the specified
	# message length in bytes from its header, stores it in the right file by making use
	# of the clients IP and sends OK response (Code:200) to the client.
	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		index = self.register_client()
		if(len(post_data) == 0):
			self.send_response(204)
		else:
			self.files_list[index].write(post_data)
			self.files_list[index].write("\r\n".encode("utf-8"))
			
			self.send_response(202)
			self.send_header("Content-type","text/html")
		self.end_headers()
		
	def set_protocol_response(self):
		
		self.responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Partial information', 'Request fulfilled from cache'),
        204: ('No response', 'Request fulfilled, nothing follows'),

        301: ('Moved', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('Method', 'Object moved -- see Method and URL list'),
        304: ('Not modified',
              'Document has not changed sincee given time'),

        400: ('Bad request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not found', 'Nothing matches the given URI'),

        500: ('Internal error', 'Server got itself in trouble'),
        501: ('Not implemented',
              'Server does not support this operation'),
        502: ('Service temporarily overloaded',
              'The server cannot process the request due to a high load'),
        503: ('Gateway timeout',
              'The gateway server did not receive a timely response'),

        }
# Condition that ensures that the class was called from its .py file and not imported
# into another file, in that case this portion would need to be redefined in the caller class.		
if __name__ == "__main__":
	import argparse # Parses the arguements from the CMD command
	
	parser = argparse.ArgumentParser()
	# -b or -bind for specifing an IP address for the server
	parser.add_argument(
		"--bind",
        "-b",
        metavar="ADDRESS",
        default="127.0.0.1", # Localhost Address
        help="Specify alternate bind address " "[default: localhost]",
    )
	
	parser.add_argument(
        "port",
        action="store",
        default=8000,
        type=int,
        nargs="?",
        help="Specify alternate port [default: 8000]",
    )
	args = parser.parse_args()
	# Object of the type HTTPServer takes the IP, Port number and the defined 
	# HTTP request handler class.
	server = HTTPServer((args.bind, args.port), HTTPHandler)
	server.RequestHandlerClass.set_protocol_response(server.RequestHandlerClass)
	print("HTTP Server Running!")
	print("Hosting on Address: {}, Port: {}".format(args.bind,args.port))
	try: 
		server.serve_forever() # Polls the server to check for requests
	except KeyboardInterrupt: # Server stopped using (Ctrl + C) in CMD
		pass
	
	server.RequestHandlerClass.close_all_files(server.RequestHandlerClass)
	server.server_close()
	print("Server Stopped")
