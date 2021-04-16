from LayerMetaData import LayerMetaData
import tensorflow as tf

# load tensorflow model

class ModelConfig(object):
    def __init__(self):
        self.Model_type = "Lenet"
        model_file = "mnist_model.h5"
        model = tf.keras.models.load_model(model_file)
        model.summary()
        self.layer_list = []
        self.input_n = 1
        self.input_h = 28
        self.input_w = 28
        self.input_c = 1
        self.input_bit = 16
        self.input_bit = 16
        self.filter_bit = 16
        
        filter_c = self.input_c
        for layer in model.layers:
            if isinstance(layer, tf.keras.layers.Conv2D):
                config = layer.get_config()
                n_filter = config['filters']
                filter_h = config['kernel_size'][0]
                filter_w = config['kernel_size'][1]
                stride = config['strides'][0]
                padding = config['padding'].upper()
                self.layer_list.append(LayerMetaData("convolution", n_filter, filter_h, filter_w, filter_c, stride, padding, 0, 0, 0, 0))
                filter_c = n_filter

            elif isinstance(layer, tf.keras.layers.Dense):
                config = layer.get_config()
                units = config['units']
                self.layer_list.append(LayerMetaData("fully", 0, 0, 0, 0, 0, 0, 0, 0, 0, units))

            elif isinstance(layer, tf.keras.layers.MaxPooling2D):
                config = layer.get_config()
                pool_h = config['pool_size'][0]
                pool_w = config['pool_size'][1]
                stride = config['strides'][0]
                self.layer_list.append(LayerMetaData("pooling", 0, 0, 0, 0, 0, 0, pool_h, pool_w, stride,   0))

            else:
                pass

    def __str__(self):
            return str(self.__dict__)

