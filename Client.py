import socket
import sys
import threading
import argparse
import json

# TK
import tkinter as tk

# Image manipulation
import numpy
import PIL
from PIL import Image, ImageTk, ImageEnhance


# Server
import Server as server


class thread(threading.Thread):
    def __init__(self, socket, **callbacks):
        threading.Thread.__init__(self)
        self.socket = socket
        self.callbacks = callbacks

    def run(self):
        while True:
            try:
                message = self.socket.receive()
                if message == 'disconnect':
                    self.socket.disconnect()
                    break
            except OSError:
                break

# Client class incharge of sending and receiving socket messages


class Client:

    def __init__(self):
        self.socket = None
        self.isClientConnected = False

        # setting initial slider options
        self.options = {
            "brightness": 0,
            "contrast": 0,
            "sharpness": 0,
            "saturation": 0
        }

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect((host, port))
            self.isClientConnected = True

        except socket.error as errorMessage:
            if errorMessage.errno == socket.errno.ECONNREFUSED:
                sys.stderr.write(
                    'Connection refused to {0} on port {1}'.format(host, port))
            else:
                sys.stderr.write(
                    'Error, unable to connect: {0}'.format(errorMessage))

    def disconnect(self):
        if self.isClientConnected:
            self.socket.close()
            self.isClientConnected = False

    """
    Send all our clients the updated values
    """

    def send(self, data):
        d = json.loads(data)
        self.socket.sendall(json.dumps(d).encode())

    """
        Receives the data as a buffer
        turns it into a str
        transforms the string into a dict
        update client values
    """

    def receive(self, size=4096):
        data = self.socket.recv(size)

        if(data[0:1] != b'\x11'):
            dataStr = data.decode()
            dataDict = json.loads(dataStr)
            self.options['brightness'] = dataDict['brightness']
            self.options['contrast'] = dataDict['contrast']
            self.options['sharpness'] = dataDict['sharpness']
            self.options['saturation'] = dataDict['saturation']
            print(self.options)
            return self.socket.recv(size).decode('utf8')

# Header menu entry


class TopMenu(tk.Entry):
    def __init__(self, root=None, placeholder="PlaceHolder", color="grey", **options):
        super().__init__(root, options)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def focus_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()

# Header menu which allows us to connect to a specific host & port


class Menu(TopMenu):
    def body(self, master):
        tk.Label(master, text="Enter host:").grid(row=0, sticky="w")
        tk.Label(master, text="Enter port:").grid(row=1, sticky="w")

        self.hostEntryField = TopMenu(master, placeholder="Enter host")
        self.portEntryField = TopMenu(master, placeholder="Enter port")

        self.hostEntryField.grid(row=0, column=1)
        self.portEntryField.grid(row=1, column=1)
        return self.hostEntryField

    def validate(self):
        host = str(self.hostEntryField.get())

        try:
            port = int(self.portEntryField.get())

            if(port >= 0 and port < 65536):
                self.result = (host, port)
                return True
            else:
                print("Error")
                return False
        except ValueError:
            print("Error")
            return False


class ImageGUI(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.options = {}
        self.init(parent)

    # Load our initial image

    def init(self, parent):
        # Image
        self.imgPath = ("./images/img.jpg")
        self.img_arr = numpy.asarray(PIL.Image.open(self.imgPath))
        self.img = Image.fromarray(self.img_arr, 'RGB')
        self.background_image = ImageTk.PhotoImage(self.img)
        self.background = tk.Label(
            parent, image=self.background_image)
        self.background.grid(row=0, column=0)

        """""""""""""""
            Scales
        """""""""""""""
        # Brightness scale
        self.brightnessLabel = tk.Label(
            parent, text="Brightness").grid(row=1, column=0, sticky="nesw")
        self.brightness = tk.Scale(
            parent, from_=0, to=200, orient=tk.HORIZONTAL, command=lambda val, slider="brightness": self.change_slider(val, slider))
        self.brightness.set(100)
        self.brightness.grid(row=2, column=0, sticky="nsew")

        # Contrast scale
        self.contrastLabel = tk.Label(parent, text="Contrast")
        self.contrastLabel.grid(row=3, column=0, sticky="nsew")

        self.contrast = tk.Scale(
            parent, from_=0, to=100, orient=tk.HORIZONTAL, command=lambda val, slider="contrast": self.change_slider(val, slider))
        self.contrast.set(100)
        self.contrast.grid(row=4, column=0, sticky="nsew")

        # Sharpness scale
        self.sharpnessLabel = tk.Label(parent, text="Sharpness")
        self.sharpnessLabel.grid(row=5, column=0, sticky="nsew")

        self.sharpness = tk.Scale(
            parent, from_=0, to=200, orient=tk.HORIZONTAL, command=lambda val, slider="sharpness": self.change_slider(val, slider))
        self.sharpness.set(100)
        self.sharpness.grid(row=6, column=0, sticky="nsew")

        # Saturation scale
        self.saturationLabel = tk.Label(parent, text="Saturation")
        self.saturationLabel.grid(row=7, column=0, sticky="nsew")

        self.saturation = tk.Scale(
            parent, from_=0, to=500, orient=tk.HORIZONTAL, command=lambda val, slider="saturation": self.change_slider(val, slider))
        self.saturation.set(100)
        self.saturation.grid(row=8, column=0, sticky="nsew")
    """""""""""""""""
        Functions
    """""""""""""""""

    def connect(self, host, port):

        client.clientSocket.connect(host, port)
        thread(client.clientSocket,
               change_slider=self.change_slider).start()

    """
        change_slider
        Lambda function incharge of setting the slider values
        @params: val: int
        @params: slider: str
    """

    def change_slider(self, val, slider):

        # Get the options from our main client class
        # Send the updated values whenever they get changed
        option = client.clientSocket.options
        print(option)
        self.brightness.set(option['brightness'])
        self.contrast.set(option['contrast'])
        self.sharpness.set(option['sharpness'])
        option[slider] = val

        client.clientSocket.send(json.dumps(option))

        if slider == "brightness":
            i = Image.open(self.imgPath)
            brightness = ImageEnhance.Brightness(i).enhance(float(val) / 100)
            self.img_arr = numpy.asarray(brightness)
            self.img = Image.fromarray(self.img_arr, 'RGB')
            self.background_image = ImageTk.PhotoImage(self.img)
            self.background = tk.Label(
                self.parent, image=self.background_image)
            self.background.grid(row=0, column=0)
        elif slider == "contrast":
            i = Image.open(self.imgPath)
            contrast = ImageEnhance.Contrast(i).enhance(float(val) / 100)
            self.img_arr = numpy.asarray(contrast)
            self.img = Image.fromarray(self.img_arr, 'RGB')
            self.background_image = ImageTk.PhotoImage(self.img)
            self.background = tk.Label(
                self.parent, image=self.background_image)
            self.background.grid(row=0, column=0)
        elif slider == "sharpness":
            i = Image.open(self.imgPath)
            sharpness = ImageEnhance.Sharpness(i).enhance(float(val) / 100)
            self.img_arr = numpy.asarray(sharpness)
            self.img = Image.fromarray(self.img_arr, 'RGB')
            self.background_image = ImageTk.PhotoImage(self.img)
            self.background = tk.Label(
                self.parent, image=self.background_image)
            self.background.grid(row=0, column=0)
        elif slider == "saturation":
            i = Image.open(self.imgPath)
            saturation = ImageEnhance.Color(i).enhance(float(val) / 100)
            self.img_arr = numpy.asarray(saturation)
            self.img = Image.fromarray(self.img_arr, 'RGB')
            self.background_image = ImageTk.PhotoImage(self.img)
            self.background = tk.Label(
                self.parent, image=self.background_image)
            self.background.grid(row=0, column=0)


"""
    Main Class GUI 
"""


class ClientGUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.init(parent)

        self.ImageGUI = ImageGUI(self.parent)
        self.clientSocket = Client()
        self.ImageGUI.bind(self.clientSocket.send)
        self.ImageGUI.bind(self.clientSocket.receive)
        # Closing will call the 'closing' function
        self.parent.protocol("WM_DELETE_WINDOW", self.closing)

    def init(self, parent):
        self.parent = parent
        self.parent.title("iCollab")
        self.parent.resizable(True, True)

        self.mainMenu = tk.Menu(self.parent)
        self.parent.config(menu=self.mainMenu)

        self.subMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label='File', menu=self.subMenu)
        self.subMenu.add_command(
            label='Connect', command=self.connect)
        self.subMenu.add_command(label='Exit', command=self.closing)

    # Connect the specific use using the host & port

    def connect(self, host, port):

        self.clientSocket.connect(host, port)
        if client.clientSocket.isClientConnected:
            thread(client.clientSocket,
                   change_slider=ImageGUI.change_slider,
                   connect=self.ImageGUI.connect).start()
        else:
            print("Unable to connect to the server.")
            sys.exit(0)

    # Once the user is done, remove them from the sockets

    def closing(self):
        self.clientSocket.disconnect()
        self.quit()
        self.destroy()


# Helper function to see if we can connect
def connect(host, port):

    if host == None:
        return False

    if port == None:
        return False

    if host and port:
        return True


"""
    Begin the Application
"""
if __name__ == "__main__":
    # Init Tkinter GUI
    app = tk.Tk()
    client = ClientGUI(app)

    # Parsing the passed in argyments
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str)
    parser.add_argument("-P", "--port", type=int)
    args = parser.parse_args()

    # extract port & host from args
    host = args.host
    port = args.port

    # check if host & port are provided throught the args
    isConnected = connect(host, port)

    if isConnected:
        client.connect(host, port)
    else:
        print('Please provide a host and a port, -H , -P')
        sys.exit(0)

    app.mainloop()
