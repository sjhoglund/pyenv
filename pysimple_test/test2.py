import socket
import PySimpleGUI as sg

#sg.theme_previewer()

sg.theme('Dark2')   # Add a touch of color
# All the stuff inside your window.

text_elem = sg.Text(size=(10,1))

layout = [ [sg.Button('ON'), sg.Button('OFF'), sg.Button('Cancel')],
            [text_elem] ]

# Create the Window
window = sg.Window('Brewery UI', layout, return_keyboard_events=True, use_default_focus=False)
# Event Loop to process "events" and get the "values" of the inputs

while True:
    event, values = window.read(timeout = 100)

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    elif event == 'ON':
        # create our udp socket
        try:
            socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            text_elem.update("Oops, something went wrong connecting the socket")

        while 1:
            message = "16 on"

            # encode the message
            message = message.encode()

            try:
                # send the message
                socket.sendto(message, ("192.168.0.10", 9999))

                # output the response (if any)
                data, ip = socket.recvfrom(1024)

                text_elem.update("{}: {}".format(ip, data.decode()))

            except socket.error:
                window['_RESPONSE_'].update("Error! {}".format(socket.error))
    elif event == 'OFF':
        # create our udp socket
        try:
            socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            text_elem.update("Oops, something went wrong connecting the socket")

        while 1:
            message = "16 off"

            # encode the message
            message = message.encode()

            try:
                # send the message
                socket.sendto(message, ("192.168.0.10", 9999))

                # output the response (if any)
                data, ip = socket.recvfrom(1024)

                text_elem.update("{}: {}".format(ip, data.decode()))

            except socket.error:
                text_elem.update("Error! {}".format(socket.error))