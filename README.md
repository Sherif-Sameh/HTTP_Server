# HTTP_Server
HTTP server built using Python's http.server library.

The Python programming language was used to build a simple local HTTP server, accessable
only by clients in the same Local Area Network as its host and capable of handling all the basic
HTTP requests specifically: GET, HEAD and POST requests. The server was built by making
use of Python’s http.server library which is capable of creating an HTTPServer object given its IP
address, Port number and request handler class. The request handler forms the core of the server by
defining the server’s behavior to requests; one could make use of the SimpleHTTPRequestHandler
class, which has simple methods defining the behavior of the server to external requests, or to create
your own class which extends the BaseHTTPRequestHandler class for which the user must define
the methods for handling requests by creating methods with the name do METHOD, for example to
define the server’s behavior to a GET request one would create a do GET method which executes
all the neccessary steps involved in handling GET requests. Of the two previous options, the latter
was chosen to be used in creating this project. The development of this class was driven with the
purpose of creating a server capable of serving two types of clients: the ESP32 MCU, which would
be making POST requests that give new information to the server, and a Web Browser client, which
would be the owner of the MCU monitoring the data that has been sent to the server and thereby
making GET or HEAD requests to the server.


Code Flow:

Common to all requests
1. Call on the BaseHTTPRequestHandler class function address string() which retrieves the IP
address of the client that initiated the request.
2. Compares that IP to the ones in its instance variable clients list and if its there then just return
the index of that IP, if not then an exception is raised upon which the new client’s IP is added
to the address list and a new text file with its name is opened for accepting and storing its data
and in the end the function return the new client’s index in the list.

GET Requests:
  With empty path variable (Refresh from browser)
1. Check and print the number of clients registered on the server as well as the server’s clients list
to the active console or terminal (CMD or Linux Terminal).
2. Flush (clear) the request handler’s buffer for writing data, wfile.
3. Send the appropriate response code to the client’s request
4. Send the ”Content-Type” header, specifing text in the HTML fromat for the server’s response
message and ending the headers portion in the response message.
5. Write to the wfile buffer the updated format of the main page which includes number of
registered clients and a list of all the accessable text files in the current working directory.

  With path variable (File requests)
1. Same as in previous section.
2. Same as in previous section.
3. Same as in previous section.
4. Using the given file path in the request, the handle file headers function splits the file name
from the file-type identifier after the ”.”, extracts the client’s number from the remaining path
by looking at the numbers at the end of the path and converting them to an integer which is
the client’s index + 1.
5. Using that index it retrieves the file’s object reference from the files list to get the files information
such as: mode, length, etc..
16
6. Using the file’s info, it sends all the file specific headers and ends the headers portion in the
response message.
7. Then, the file is closed and reopened in binary reading mode for copying its contents in to the
server.
8. Finally, the file’s contents are copied into the wfile buffer and the file is reopened in binary
append mode.

HEAD Requests
The process of handling HEAD request follows the exact same flow of handling file GET requests,
the only difference is that the HEAD request does not actually copy and load the specified file’s
contents into the wfile buffer thus it also does not clear the buffer.

POST Request
1. Read the request’s ”Content-Length” header, from the class specific variable for storing headers,
headers.
2. Based on the the value of ”Content-Length”: read that that amount of bytes from rfile, the
request handler’s buffer for request data.
3. Send the appropriate response code and headers then ending the header portion of the response
message.
4. Appending the request’s body to the client’s specefic text file.
