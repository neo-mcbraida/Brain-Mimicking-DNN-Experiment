from tkinter import *
from datetime import datetime
import random

GRAPHIC_HEIGHT = 700
GRAPHIC_WIDTH = 700
# CIRCLE_RADIUS = 50
START_TIME = datetime.now()

nodes = [] # actually is a list of layers each layer being a list of nodes
offsets = [] # list of layers of each of which being a list of nodes, each of which being a list of connections
connections = []

window = Tk()
window.title("Visual Representation")
window.configure(bg='black', width=GRAPHIC_WIDTH, height=GRAPHIC_HEIGHT)
c = Canvas(window, width=GRAPHIC_WIDTH, height=GRAPHIC_HEIGHT)
c.pack()
c.configure(bg='black')

def create_layer(width, x, circle_radius, y=0):
    layer = []
    layer_consts = []
    y = 0
    for i in range(width):
        gap = GRAPHIC_HEIGHT/(width+1)
        y += gap
        circle = c.create_oval(x, y, x+circle_radius, y+circle_radius)
        c.itemconfig(circle, fill='white')
        layer.append(circle)
        layer_consts.append(random.randint(0, 256))
    nodes.append(layer)
    offsets.append(layer_consts)
        
def add_connections(nodes, circle_radius):
    diff = circle_radius/2
    for i in range(1, len(nodes)): # for each layer apart from the first
        connection_set_nodes = []
        for j in range(len(nodes[i])): # for each node in the current layer
            connection_set_lines = []
            for u in range(len(nodes[i-1])): # for each node in the previous layer
                coords1 = c.coords(nodes[i][j]) # current node coords
                coords2 = c.coords(nodes[i-1][u]) # previous node coords
                line = c.create_line(coords1[0]+diff, coords1[1]+diff, coords2[0]+diff, coords2[1]+diff, fill='white')
                c.lower(line)
                connection_set_lines.append(line)
            connection_set_nodes.append(connection_set_lines)
        connections.append(connection_set_nodes)

def create_network(layers, width):
    x = 0
    x_gap = width / (len(layers) + 1)
    max_width = max(layers)
    circle_radius = GRAPHIC_HEIGHT/(2*max_width)
    for layer_width in layers:
        x += x_gap
        create_layer(layer_width, x, circle_radius)
    add_connections(nodes, circle_radius)
    return circle_radius


def update_colours(layers):
    # ffXX00
    # XX0000
    #time_delta = datetime.now() - START_TIME
    #time_delta = time_delta.total_seconds() * 100
    #window.after(1, update_colours)
    for i in range(len(layers)):
        #print("i: ", i)
        for n in range(layers[i].WIDTH):
            #print("n: ", n)
            pd = layers[i].potential_differences[n]
            activation_percentage = (pd+(70))/(110)
            node_saturation = hex(int(activation_percentage * 255)) # hex percentage of saturation 0-256
            if len(node_saturation) == 4:
                hex_val = "#" + node_saturation[2:4] + "0000"
            else:
                hex_val = "#" + node_saturation[2:4] + "00000"
            c.itemconfig(nodes[i][n], fill=hex_val)
            if i > 0:
                #print(node.input_weights)
                for j in range(len(layers[i].weights[n])):
                    #print("j: ", j)
                    #activation_percentage = (node.potential_difference+(70*(10**-3)))/(110*(10**-3))
                    weight = layers[i].weights[n][j]
                    if weight > 0:
                        weight = min(5, weight)
                    else:
                        weight = max(-5, weight)
                    weight_percentage = ((weight+0.25)/0.5) # assuming weights are between -5 and 5
                    #offset = offsets[i][j]
                    # node_saturation = hex(int(activation_percentage * 256)) # hex percentage of saturation 0-256
                    line_hue = hex(int(weight_percentage * 255))
                    # #diff = hex(int((time_delta+offset)%256))
                    # if len(node_saturation) == 4:
                    #     hex_val = "#" + node_saturation[2:4] + "0000"
                    # else:
                    #     hex_val = "#" + node_saturation[2:4] + "00000"
                        
                    if len(line_hue) == 4:
                        line_hex = "#ff" + line_hue[2:4] + "00"
                    else:
                        line_hex = "#ff0" + line_hue[2:4] + "00"
                    # c.itemconfig(nodes[i][j], fill=hex_val)
                   # print("x",line_hex)
                    c.itemconfig(connections[i-1][n][j], fill=line_hex)
                    #print("y",c.itemcget(connections[i-1][j], 'fill'))

# layers = [25, 25, 2]
#circle_width = create_network(layers, GRAPHIC_WIDTH)
# def t():
#     print("d")
#     window.after(1,t)
# window.after(10, t)
# window.mainloop()
# test()