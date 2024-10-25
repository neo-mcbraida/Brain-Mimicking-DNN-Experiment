import numpy as np
import visualisation
import random
from math import exp

# for a single input node the max input voltage should be 20, so max weight = 40v/activation_func(20)

class EmptyLayer:
    def __init__(self, width=0):
        self.WIDTH = width

class Layer:
    def __init__(self, width, input_layer) -> None:
        self.WIDTH = width
        self.conductivity = 30
        self.input_charges = []
        self.input_layer = input_layer  
        self.potential_differences = []
        self.weights = []
        self.firing_sliders = []
        self.firing_pds = []
        self.are_firing = []
        self.add_nodes()
        
    def add_nodes(self):
        for i in range(self.WIDTH):
            self.input_charges.append(0)
            self.potential_differences.append(-70)
            self.firing_sliders.append(0)
            self.firing_pds.append(30)
            self.are_firing.append(False)
            input_weights = []
            for j in range(self.input_layer.WIDTH):
                weight = random.random()-0.3
                input_weights.append(weight)
            self.weights.append(input_weights)
    
    def get_firing_pd(self, firing_slide):
        return 10/(1+exp(2-(.3*firing_slide))) + 30

    def get_activation(self, index):
        # print(self.input_charges[index])
        denominator = max(0.05, exp(-3+0.5*self.input_charges[index]))
        # if denominator == 0:
        #     print("test")
        pd = (-1/denominator)-50
        # if pd >= -55:
        #     pd = self.firing_pds[index]
        return pd
    
    def update_weight(self, node_index, weight_index):
        if self.are_firing[node_index]:
            if self.input_layer.are_firing[weight_index]:
                self.weights[node_index][weight_index] += 0.01
            else: # try removing the else first
                self.weights[node_index][weight_index] -= 0.005
        else:
            if self.input_layer.are_firing[weight_index]:
                self.weights[node_index][weight_index] -= 0.005
            else:
                self.weights[node_index][weight_index] /= 0.8
        
        if self.weights[node_index][weight_index] > 0:
            self.weights[node_index][weight_index] = min(0.25, self.weights[node_index][weight_index])
        else:
            self.weights[node_index][weight_index] = max(-0.25, self.weights[node_index][weight_index])
            
        # if self.input_layer.are_firing[weight_index] == self.are_firing[node_index]:
        #     self.weights[node_index][weight_index] += 0.05
        # else:
        #     self.weights[node_index][weight_index] -= 0.05
            
    def limit_input_charge(self, input_charge):
        if input_charge >= 0:
            return min(10, input_charge)
        else:
            return max(-1, input_charge)

    def train_step(self):
        for i in range(self.WIDTH):
            self.input_charges[i] = 0
            for j in range(self.input_layer.WIDTH):
                if self.input_layer.are_firing[j]:
                    self.input_charges[i] += self.weights[i][j] * self.input_layer.potential_differences[j]
                self.update_weight(i, j)
            self.input_charges[i] = self.limit_input_charge(self.input_charges[i])
            self.potential_differences[i] = self.get_activation(i)
            self.potential_differences[i] = min(-50, self.potential_differences[i])
            if self.potential_differences[i] >= -55:
                self.potential_differences[i] = self.firing_pds[i]
                self.are_firing[i] = True
                self.firing_sliders[i] = min(500, self.firing_sliders[i]+1)
            else:
                self.are_firing[i] = False
                self.firing_sliders[i] = max(-500, self.firing_sliders[i]-1)
            self.firing_pds[i] = self.get_firing_pd(self.firing_sliders[i])
            
    def output_step(self, output):
        for i in range(self.WIDTH):
            self.potential_differences[i] = output[i]
            if self.potential_differences[i] >= -55:
                self.are_firing[i] = True
            else:
                self.are_firing[i] = False
            for j in range(self.input_layer.WIDTH):
                self.update_weight(i, j)
                
    def step(self):
        for i in range(self.WIDTH):
            self.input_charges[i] = 0
            for j in range(self.input_layer.WIDTH):
                if self.input_layer.are_firing[j]:
                    self.input_charges[i] += self.weights[i][j] * self.input_layer.potential_differences[j]
            #self.input_charges[i] = min(-50, self.input_charges[i])
            self.input_charges[i] = self.limit_input_charge(self.input_charges[i])
            self.potential_differences[i] = self.get_activation(i)
            self.potential_differences[i] = min(-50, self.potential_differences[i])
            if self.potential_differences[i] >= -55:
                self.potential_differences[i] = self.firing_pds[i]
                self.are_firing[i] = True
            else:
                self.are_firing[i] = False
                
        
            
    def input_step(self, input_activations):
        for i in range(len(input_activations)):
            self.potential_differences[i] = input_activations[i]
            if self.potential_differences[i] >= -55:
                self.are_firing[i] = True
            else:
                self.are_firing[i] = False

class MLP:
    def __init__(self, layers):
        self.dims = layers
        self.layers = []
        self.add_layers()
        self.DEPTH = len(layers)
        
    def add_layers(self):
        input_layer = Layer(self.dims[0], EmptyLayer())
        self.layers.append(input_layer)
        for i in range(1, len(self.dims)):
            layer = Layer(self.dims[i], self.layers[i-1])
            self.layers.append(layer)
            
    def train_on_sample(self, input, output):
        self.layers[0].input_step(input)
        for i in range(1, self.DEPTH-1):
            self.layers[i].train_step()
        self.layers[self.DEPTH-1].output_step(output)
        
    def predict_on_sample(self, input):
        self.layers[0].input_step(input)
        for i  in range(1, self.DEPTH):
            self.layers[i].step()
        return self.layers[self.DEPTH-1].potential_differences.copy()
            
    def train_visually(self, inputs, outputs, test_inputs, test_outputs, training_index=0):
        if training_index < len(inputs):
            #n = input()
            self.train_on_sample(inputs[training_index], outputs[training_index])
            visualisation.update_colours(self.layers)
            visualisation.window.after(1, self.train_visually, inputs, outputs, test_inputs, test_outputs, training_index+1)
        else:
            self.test(test_inputs, test_outputs)
            
    def test(self, inputs, outputs):
        predictions = []
        accuracy = 0
        denominator = self.dims[self.DEPTH-1]
        for i in range(len(inputs)):
            prediction = self.predict_on_sample(inputs[i])
            predictions.append(prediction)
            for j in range(len(prediction)):
                if (outputs[i][j] == 40):
                    accuracy += int(prediction[j] > 20) / denominator
        print(predictions[0:10])
        print(outputs[0:10])
        print("accuracy: ", accuracy, "%")
            
            
            
input_data = []
output_data = []
for i in range(2000):
    inp1 = random.randint(0, 4)
    output = random.randint(inp1+1, 5)
    inp2 = output-inp1
    input_sample = []
    output_array = []
    for i in range(0,6):
        if i == inp1 or i == inp2:
            input_sample.append(40)
        else:
            input_sample.append(-70)
    input_data.append(input_sample)
    for i in range(1, 6):
        if i == output:
            output_array.append(40)
        else:
            output_array.append(-70)
    output_data.append(output_array)
            
# print(input_data)
# print(output_data)
    # if output == 1:
    #     input_sample = [40 if i < 4 else -70 for i in range(8)]
    #     output_sample = [40, -70]
    # else:
    #     input_sample = [-70 if i < 4 else 40 for i in range(8)]
    #     output_sample = [-70, 40]
    # input_data.append(input_sample)
    # output_data.append(output_sample)
    
test_inputs = []
test_outputs = []
for i in range(200):
    inp1 = random.randint(0, 4)
    output = random.randint(inp1+1, 5)
    inp2 = output-inp1
    input_sample = []
    output_array = []
    for i in range(0,6):
        if i == inp1 or i == inp2:
            input_sample.append(40)
        else:
            input_sample.append(-70)
    test_inputs.append(input_sample)
    for i in range(1, 6):
        if i == output:
            output_array.append(40)
        else:
            output_array.append(-70)
    test_outputs.append(output_array)

layers = [6, 25, 5]
circle_rad = visualisation.create_network(layers, visualisation.GRAPHIC_HEIGHT)
model = MLP(layers)
def t():
    print("d")
    visualisation.window.after(1,t)
visualisation.window.after(1, model.train_visually, input_data, output_data, test_inputs, test_outputs)
# visualisation.window.after(1, t)
visualisation.window.mainloop()
#model.train(input_data, output_data)
model.test(test_inputs, test_outputs)
print("DONE")
# layers = [3, 5, 5, 5, 2]
# create_network(layers, GRAPHIC_WIDTH)

# window.after(1, update_colours)
# window.mainloop()