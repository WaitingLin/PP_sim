from LayerMetaData import LayerMetaData

class ModelConfig(object):
    def __init__(self):
        model_type = 1
        if model_type == 0: # TestModelConfig
            self.layer_list = [
                LayerMetaData("convolution", 2, 2, 2, 1, 0, 0, 0),
                #LayerMetaData("convolution", 1, 2, 2, 1, 0, 0, 0),
                LayerMetaData("pooling",     0, 0, 0, 0, 2, 2, 0),
                LayerMetaData("fully",       0, 0, 0, 0, 0, 0, 2),
                ]
            self.input_n = 1
            self.input_h = 3
            self.input_w = 3
            self.input_c = 1
            self.input_bit = 1
            self.filter_bit = 2
        elif model_type == 1: # TestModelConfig2
            self.layer_list = [
                LayerMetaData("convolution", 20, 5, 5,  3, 0, 0,  0),
                LayerMetaData("convolution", 10, 2, 2, 20, 0, 0,  0),
                #LayerMetaData("pooling",      0, 0, 0,  0, 2, 2,  0),
                LayerMetaData("fully",        0, 0, 0,  0, 0, 0, 10)
                ]
            self.input_n = 1
            self.input_h = 7
            self.input_w = 7
            self.input_c = 3
            self.input_bit = 2
            self.filter_bit = 4
        elif model_type == 2: # Cifar10Config
            self.layer_list = [
                LayerMetaData("convolution", 8, 3, 3, 3, 0, 0,  0),
                #LayerMetaData("pooling",     0, 0, 0, 0, 2, 2,  0),
                #LayerMetaData("pooling",     0, 0, 0, 0, 2, 2,  0),
                LayerMetaData("convolution", 4, 3, 3, 8, 0, 0,  0),
                LayerMetaData("convolution", 4, 3, 3, 4, 0, 0,  0),
                LayerMetaData("convolution", 4, 3, 3, 4, 0, 0,  0),
                #LayerMetaData("pooling",     0, 0, 0, 0, 2, 2,  0),
                LayerMetaData("fully",       0, 0, 0, 0, 0, 0, 10)
                ]
            self.input_n = 1
            self.input_h = 12
            self.input_w = 12
            self.input_c = 3
            self.input_bit = 2
            self.filter_bit = 2
        elif model_type == 3: # CaffenetConfig
            self.layer_list = [
                LayerMetaData("convolution",  96, 11, 11,   3, 0, 0,    0),
                LayerMetaData("convolution", 256,  5,  5,  96, 0, 0,    0),
                LayerMetaData("convolution", 348,  3,  3, 256, 0, 0,    0),
                LayerMetaData("convolution", 348,  3,  3, 348, 0, 0,    0),
                LayerMetaData("convolution", 256,  3,  3, 348, 0, 0,    0),
                LayerMetaData("fully",         0,  0,  0,   0, 0, 0, 4096),
                LayerMetaData("fully",         0,  0,  0,   0, 0, 0, 4096),
                LayerMetaData("fully",         0,  0,  0,   0, 0, 0,   10)
                ]
            self.input_n = 1
            self.input_h = 224
            self.input_w = 224
            self.input_c = 3
            self.input_bit = 16
            self.filter_bit = 16
        elif model_type == 4: # LenetConfig
            self.layer_list = [
                LayerMetaData("convolution",  6, 5, 5, 1, 0, 0,   0),
                LayerMetaData("pooling",      0, 0, 0, 0, 2, 2,   0),
                LayerMetaData("convolution", 16, 5, 5, 6, 0, 0,   0),
                LayerMetaData("fully",        0, 0, 0, 0, 0, 0, 120),
                LayerMetaData("fully",        0, 0, 0, 0, 0, 0,  84),
                LayerMetaData("fully",        0, 0, 0, 0, 0, 0,  10)
                ]
            self.input_n = 1
            self.input_h = 32
            self.input_w = 32
            self.input_c = 1
            self.input_bit = 2
            self.filter_bit = 16
    
    def __str__(self):
            return str(self.__dict__)