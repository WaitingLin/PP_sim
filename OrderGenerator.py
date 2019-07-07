from PE import PE
from XBAR import XBAR
from EventMetaData import EventMetaData
import numpy as np 

class OrderGenerator(object):
    def __init__(self, model_information, hardware_information, mapping_information, isPipeline):
        self.model_information = model_information
        self.hardware_information = hardware_information
        self.mapping_information = mapping_information
        self.isPipeline = isPipeline

        self.Computation_order = []
        # model
        self.input_n = model_information.input_n

        self.layer_list = model_information.layer_list  # conv, pool, conv, ...
        self.layer_length = len(model_information.layer_list)  # how many layer
        self.input_h = [model_information.input_h] # input feature map height (each layer)
        self.input_w = [model_information.input_w] # input feature map width (each layer)
        self.input_c = [model_information.input_c] # input feature map channel (each layer)
        self.input_number = [] # input windows number
        self.filter_n = [] 
        self.filter_h = []
        self.filter_w = []
        self.filter_c = []
        self.filter_length = [] # Straighten kernel length
        self.pooling_h = []
        self.pooling_w = []
        
        self.pe_saa_mat = []
        self.feature_mat = []

        self.input_bit = model_information.input_bit 
        self.filter_bit = model_information.filter_bit

        self.cu_traverse_idx = []
        
        for i in range(len(self.layer_list)):
            if self.layer_list[i].layer_type == "convolution":
                self.filter_n.append(self.layer_list[i].filter_n)
                self.filter_h.append(self.layer_list[i].filter_h)
                self.filter_w.append(self.layer_list[i].filter_w)
                self.filter_c.append(self.layer_list[i].filter_c)
                self.filter_length.append(self.layer_list[i].filter_h * self.layer_list[i].filter_w * self.layer_list[i].filter_c)
                self.pooling_h.append(0)
                self.pooling_w.append(0)
                self.input_h.append(self.input_h[i] - self.layer_list[i].filter_h + 1)
                self.input_w.append(self.input_w[i] - self.layer_list[i].filter_w + 1)
                self.input_c.append(self.layer_list[i].filter_n)
                self.input_number.append((self.input_h[i] - self.layer_list[i].filter_h + 1) * (self.input_w[i] - self.layer_list[i].filter_w + 1))
                
                self.pe_saa_mat.append(np.zeros((self.input_number[i], self.layer_list[i].filter_n)).tolist())
                
                if i+1 < len(self.layer_list):
                    if self.layer_list[i+1].layer_type == "fully":
                        self.feature_mat.append(np.zeros((self.input_h[i+1] * self.input_w[i+1] * self.input_c[i+1], 1, 1)).tolist())
                    else:
                        self.feature_mat.append(np.zeros((self.input_h[i+1], self.input_w[i+1], self.input_c[i+1])).tolist())
                        #print(self.input_h[i+1], self.input_w[i+1])

            elif self.layer_list[i].layer_type == "pooling":
                self.filter_n.append(0)
                self.filter_h.append(0)
                self.filter_w.append(0)
                self.filter_c.append(0)
                self.filter_length.append(0)
                self.pooling_h.append(self.layer_list[i].pooling_h)
                self.pooling_w.append(self.layer_list[i].pooling_w)
                self.input_h.append(self.input_h[i] // self.layer_list[i].pooling_h)
                self.input_w.append(self.input_w[i] // self.layer_list[i].pooling_w)
                self.input_c.append(self.input_c[i])
                self.input_number.append((self.input_h[i] // self.layer_list[i].pooling_h) * (self.input_w[i] // self.layer_list[i].pooling_w) * (self.input_c[i]))
                
                self.pe_saa_mat.append([])
                if i+1 < len(self.layer_list):
                    if self.layer_list[i+1].layer_type == "fully":
                        self.feature_mat.append(np.zeros((self.input_h[i+1] * self.input_w[i+1] * self.input_c[i+1], 1, 1)).tolist())
                    else:
                        self.feature_mat.append(np.zeros((self.input_h[i+1], self.input_w[i+1], self.input_c[i+1])).tolist())

            elif self.layer_list[i].layer_type == "fully":
                self.filter_n.append(self.layer_list[i].neuron_n)
                self.filter_h.append(0)
                self.filter_w.append(0)
                self.filter_c.append(0)
                self.filter_length.append(self.input_h[i] * self.input_w[i] * self.input_c[i])
                self.pooling_h.append(0)
                self.pooling_w.append(0)
                self.input_h.append(self.filter_n[i])
                self.input_w.append(1)
                self.input_c.append(1)
                self.input_number.append(self.layer_list[i].neuron_n)

                self.pe_saa_mat.append(np.zeros((self.input_number[i], self.filter_n[i])).tolist())
                if i+1 < len(self.layer_list):
                    self.feature_mat.append(np.zeros((self.filter_n[i], 1, 1)).tolist())

        # hardware
        self.Xbar_h = self.hardware_information.Xbar_h
        self.Xbar_w = self.hardware_information.Xbar_w
        self.OU_h = self.hardware_information.OU_h
        self.OU_w = self.hardware_information.OU_w
        self.RT_num_y = self.hardware_information.Router_num_y
        self.RT_num_x = self.hardware_information.Router_num_x
        self.RT_num = self.hardware_information.Router_num
        self.PE_num_y = self.hardware_information.PE_num_y
        self.PE_num_x = self.hardware_information.PE_num_x
        self.PE_num = self.hardware_information.PE_num
        self.CU_num_y = self.hardware_information.CU_num_y
        self.CU_num_x = self.hardware_information.CU_num_x
        self.CU_num = self.hardware_information.CU_num
        self.XB_num_y = self.hardware_information.Xbar_num_y
        self.XB_num_x = self.hardware_information.Xbar_num_x
        self.XB_num = self.hardware_information.Xbar_num

        # mapping
        self.layer_mapping_to_xbar = self.mapping_information.layer_mapping_to_xbar
        self.layer_mapping_to_pe = self.mapping_information.layer_mapping_to_pe
        self.CU_array = []
        self.XB_array = []
        idx = 0
        for rty_idx in range(self.RT_num_y):
            for rtx_idx in range(self.RT_num_x):
                for pey_idx in range(self.PE_num_y):
                    for pex_idx in range(self.PE_num_x):

                        for cuy_idx in range(self.CU_num_y):
                            for cux_idx in range(self.CU_num_x):
                                cu_pos = (rty_idx, rtx_idx, pey_idx, pex_idx, cuy_idx, cux_idx)
                                self.cu_traverse_idx.append(cu_pos)
                                for xby_idx in range(self.XB_num_y):
                                    for xbx_idx in range(self.XB_num_x):
                                        xb_pos = (rty_idx, rtx_idx, pey_idx, pex_idx, cuy_idx, cux_idx, xby_idx, xbx_idx)
                                        self.XB_array.append(XBAR(self.Xbar_h, self.Xbar_w, xb_pos))
                                        self.XB_array[idx].crossbar_array = \
                                            mapping_information.crossbar_array[rty_idx][rtx_idx][pey_idx][pex_idx][cuy_idx][cux_idx][xby_idx][xbx_idx]
                                        for mapping_data in self.layer_mapping_to_xbar[rty_idx][rtx_idx][pey_idx][pex_idx][cuy_idx][cux_idx][xby_idx][xbx_idx]:
                                            if mapping_data.eventtype == "convolution":
                                                self.XB_array[idx].Convolution.append(mapping_data)
                                            if mapping_data.eventtype == "fully":
                                                self.XB_array[idx].Fully.append(mapping_data)
                                        idx += 1   

        

        for nlayer in range(len(self.layer_list)):
            print("layer", nlayer, self.layer_list[nlayer].layer_type)
            if self.layer_list[nlayer].layer_type == "convolution":
                for nCU in range(len(self.cu_traverse_idx)):
                      ##############################
                     ##### Event: edram_rd_ir ##### 
                    ##############################
                    max_xb_input_len = 0
                    pos = self.cu_traverse_idx[nCU]
                    rty_idx, rtx_idx= pos[0], pos[1]
                    pey_idx, pex_idx = pos[2], pos[3]
                    cuy_idx, cux_idx = pos[4], pos[5]

                    for xby_idx in range(self.XB_num_y):
                        for xbx_idx in range(self.XB_num_x):
                            xbar_array_idx = xbx_idx + (xby_idx * self.XB_num_x) + \
                                            (cux_idx * self.XB_num) + \
                                            (cuy_idx * self.CU_num_x * self.XB_num) + \
                                            (pex_idx * self.CU_num * self.XB_num) + \
                                            (pey_idx * self.PE_num_x * self.XB_num * self.CU_num) + \
                                            (rtx_idx * self.PE_num * self.CU_num * self.XB_num) + \
                                            (rty_idx * self.RT_num_x * self.PE_num * self.CU_num * self.XB_num)
                            for conv in self.XB_array[xbar_array_idx].Convolution:
                                if conv.nlayer == nlayer:
                                    max_xb_input_len = max(max_xb_input_len, len(conv.inputs))
                    #print(self.cu_traverse_idx[nCU], max_xb_input_len)

                    for nInp in range(max_xb_input_len):
                        data_feed_to_cu = []
                        for xby_idx in range(self.XB_num_y):
                            for xbx_idx in range(self.XB_num_x):
                                xbar_array_idx = xbx_idx + (xby_idx * self.XB_num_x) + \
                                                (cux_idx * self.XB_num) + \
                                                (cuy_idx * self.CU_num_x * self.XB_num) + \
                                                (pex_idx * self.CU_num * self.XB_num) + \
                                                (pey_idx * self.PE_num_x * self.XB_num * self.CU_num) + \
                                                (rtx_idx * self.PE_num * self.CU_num * self.XB_num) + \
                                                (rty_idx * self.RT_num_x * self.PE_num * self.CU_num * self.XB_num)
                                for conv in self.XB_array[xbar_array_idx].Convolution:
                                    #print(conv)
                                    if conv.nlayer == nlayer:
                                        inp = conv.inputs[nInp]
                                        for d in inp:
                                            if d not in data_feed_to_cu:
                                                data_feed_to_cu.append(d)

                        #print("nCU", nCU, "data_feed_to_cu", data_feed_to_cu)

                        ### add dependency
                        edram_rd_ir_event_idx = len(self.Computation_order)
                        #print(edram_rd_ir_event_idx)
                        preceding_event_list = []
                        preceding_count = 0
                        des_pe_idx = pos[:-2]
                        if nlayer != 0: 
                            for input_data in data_feed_to_cu:
                                preceding_list = self.feature_mat[nlayer-1][input_data[1]][input_data[2]][input_data[3]]
                                #print(preceding_list)
                                if preceding_list != 0.0:
                                    for pre_event in preceding_list:
                                        if pre_event not in preceding_event_list:
                                            self.Computation_order[pre_event].proceeding_event.append(edram_rd_ir_event_idx)
                                            self.Computation_order[pre_event].position_idx.append(des_pe_idx)
                                            #print(self.Computation_order[pre_event].position_idx)
                                            preceding_count += 1
                                        
                        
                        input_sequence = data_feed_to_cu
                        output_sequence = []
                        position_idx = pos # cu position
                        event = EventMetaData("edram_rd_ir", position_idx, preceding_count, [], nlayer, input_sequence, output_sequence)
                        self.Computation_order.append(event)
                        
                          ############################### 
                         ##### Event: ou_operation ##### 
                        ###############################
                        for xby_idx in range(self.XB_num_y):
                            for xbx_idx in range(self.XB_num_x):
                                xbar_array_idx = xbx_idx + (xby_idx * self.XB_num_x) + \
                                                (cux_idx * self.XB_num) + \
                                                (cuy_idx * self.CU_num_x * self.XB_num) + \
                                                (pex_idx * self.CU_num * self.XB_num) + \
                                                (pey_idx * self.PE_num_x * self.XB_num * self.CU_num) + \
                                                (rtx_idx * self.PE_num * self.CU_num * self.XB_num) + \
                                                (rty_idx * self.RT_num_x * self.PE_num * self.CU_num * self.XB_num)
                                for conv in self.XB_array[xbar_array_idx].Convolution:
                                    if conv.nlayer == nlayer:
                                        #print("conv  ", "nlayer", nlayer,"xbar_array_idx", xbar_array_idx)
                                        this_input = conv.inputs[nInp]
                                        num_input = this_input[0][0]
                                        #print(this_input, num_input)
                                        
                                        #print(this_input, num_input)
                                        xbar_block = []
                                        index = 0
                                        while index < len(conv.xbar_column):
                                            this_block = conv.xbar_column[index:index + self.OU_w]
                                            xbar_block.append(this_block)
                                            index += self.OU_w
                                        #print(xbar_block)
                                        index = 0
                                        while index < len(this_input):
                                            input_sequence = [] # [[h, w, c]] each ou
                                            xbar_sequence = []
                                            input_count = 0

                                            while input_count < self.OU_h and index < len(this_input):
                                                #if this_input[index] != -1:
                                                input_sequence.append(this_input[index])
                                                xbar_sequence.append(index)
                                                index += 1
                                                input_count += 1
                                            for input_bit in range(self.input_bit):
                                                for w in xbar_block:
                                                    #print(input_bit, input_sequence, w)
                                                    
                                                    output_sequence = []  # [[(input_h, input_w, input_c, input_bit), (nfilter, ngrid, filter_bit)]]
                                                    for length in range(len(input_sequence)):
                                                        for column in range(len(w)):
                                                            hinput = input_sequence[length][0]
                                                            winput = input_sequence[length][1]
                                                            cinput = input_sequence[length][2]
                                                            crossbar_grid = self.XB_array[xbar_array_idx].crossbar_array[xbar_sequence[length]][w[column]]
                                                            filter_nfilter = crossbar_grid.nfilter
                                                            filter_ngrid = crossbar_grid.ngrid
                                                            filter_nbit = crossbar_grid.nbit
                                                            output_sequence.append([(num_input, hinput, winput, cinput, input_bit, ), (filter_nfilter, filter_ngrid, filter_nbit, )])

                                                    #print(output_sequence)
                                                
                                                    ### for input requirement CU的level才對
                                                    #for input_s in input_sequence:
                                                    #    idx = input_s[2] * self.input_h[nlayer] * self.input_w[nlayer] + input_s[0] * self.input_w[nlayer] + input_s[1]
                                                    #    if self.XB_array[xbar_array_idx].input_require[nlayer][idx] == -1:
                                                    #        self.XB_array[xbar_array_idx].input_require[nlayer][idx] = 1
                                                    #    else:
                                                    #        self.XB_array[nXxbar_array_idxB].input_require[nlayer][idx] += 1

                
                                                    ### add dependency
                                                    preceding_count = 1
                                                    ou_event_idx = len(self.Computation_order)
                                                    self.Computation_order[edram_rd_ir_event_idx].proceeding_event.append(ou_event_idx)


                                                    position_idx = self.XB_array[xbar_array_idx].position
                                                    event = EventMetaData("ou_operation", position_idx, preceding_count, [], nlayer, input_sequence, output_sequence)
                                                    self.Computation_order.append(event)
            
                                                        #########################
                                                      ##### Event: cu_saa ##### 
                                                    #########################
                                                    filter_list = []
                                                    cu_saa_output_sequence = []
                                                    position_idx = position_idx[:-2]
                                                    preceding_count = 1
                                                    input_nbit = output_sequence[0][0][4]
                                                                                                   
                                                    for col in range(len(w)): #同個ou col必須是同一張filter
                                                        filter_nfilter = output_sequence[col][1][0]
                                                        filter_nbit = output_sequence[col][1][2]
                                                        if filter_nfilter not in filter_list:
                                                            filter_list.append(filter_nfilter)

                                                    for nfilter in filter_list:
                                                        cu_saa_input_sequence = []  #[(input_nbit, filter_nfilter, filter_nbit)]   
                                                        for col in range(len(w)):
                                                            if nfilter == output_sequence[col][1][0]:
                                                                filter_nbit = output_sequence[col][1][2]
                                                                cu_saa_input_sequence.append((input_nbit, nfilter, filter_nbit))

                                                        ### add dependency
                                                        cu_saa_event_idx = len(self.Computation_order)
                                                        self.Computation_order[ou_event_idx].proceeding_event.append(cu_saa_event_idx)

                                                        grid = self.pe_saa_mat[nlayer][num_input][nfilter]
                                                        if grid == 0.0:
                                                            self.pe_saa_mat[nlayer][num_input][nfilter] = []

                                                        self.pe_saa_mat[nlayer][num_input][nfilter].append(cu_saa_event_idx)
                                                        
                                                        event = EventMetaData("cu_saa", position_idx, preceding_count, [], nlayer, cu_saa_input_sequence, cu_saa_output_sequence)
                                                        self.Computation_order.append(event)
                                                  
                
                
                windowlen_w = self.input_w[nlayer] - self.filter_w[nlayer] + 1
                windowlen_h = self.input_h[nlayer] - self.filter_h[nlayer] + 1
                for window_h in range(windowlen_h):
                    for window_w in range(windowlen_w):
                        for nfilter in range(self.filter_n[nlayer]):
                              #########################
                             ##### Event: pe_saa ##### 
                            #########################
                            pe_saa_input_sequence = [] # [[window_h, window_w, nfilter, pre_CU_idx]] 
                            output_sequence = [[window_h, window_w, nfilter]] # [input_window_h, input_window_w, nfilter]
                            num_input = window_h * windowlen_w + window_w

                            grid = self.pe_saa_mat[nlayer][num_input][nfilter]
                            if grid == 0.0:
                                self.pe_saa_mat[nlayer][num_input][nfilter] = []

                            ### add dependency
                            preceding_count = 0
                            preceding_list = self.pe_saa_mat[nlayer][num_input][nfilter]
                            append_event_idx = len(self.Computation_order)
                            data_transfer_event_idx = append_event_idx
                            
                            if preceding_list != 0:
                                #print(preceding_list)
                                ### do PE SAA in first Pre CU SAA event
                                first_pre_event_idx = preceding_list[0] 
                                pe_saa_position_idx = self.Computation_order[first_pre_event_idx].position_idx[:-2]
                                # print(pe_saa_position_idx) 

                                for pre_event_idx in preceding_list:
                                    if self.Computation_order[pre_event_idx].position_idx[:-2] != pe_saa_position_idx: # in different PE, need data transfer
                                        #print("different pe")
                                        #print(self.Computation_order[pre_event_idx].position_idx[:-2])
                                        self.Computation_order[pre_event_idx].proceeding_event.append(data_transfer_event_idx)
                                        data_transfer_event_idx += 1
                                        preceding_count += 1
                                        source_pe_idx = self.Computation_order[pre_event_idx].position_idx[:-2]
                                          ################################
                                         ##### Event: data_transfer ##### 
                                        ################################
                                        data_transfer_input_sequence = []
                                        data_transfer_output_sequence = []
                                        event = EventMetaData("data_transfer", [source_pe_idx, pe_saa_position_idx], 1, [], nlayer, data_transfer_input_sequence, data_transfer_output_sequence)
                                        self.Computation_order.append(event)

                                pe_saa_event_idx = data_transfer_event_idx
                                for pre_event_idx in preceding_list:
                                    if self.Computation_order[pre_event_idx].position_idx[:-2] == pe_saa_position_idx: # in same PE
                                        #print("same pe")
                                        self.Computation_order[pre_event_idx].proceeding_event.append(pe_saa_event_idx)
                                        pre_CU_idx = self.Computation_order[pre_event_idx].position_idx
                                        pe_saa_input_sequence.append([window_h, window_w, nfilter, pre_CU_idx])
                                        preceding_count += 1

                                ### data transfer dependency
                                #print(append_event_idx, pe_saa_event_idx)
                                for idx in range(append_event_idx, pe_saa_event_idx):
                                    self.Computation_order[idx].proceeding_event.append(pe_saa_event_idx)
                                
                            #print(pe_saa_input_sequence, position_idx)

                            event = EventMetaData("pe_saa", pe_saa_position_idx, preceding_count, [], nlayer, pe_saa_input_sequence, output_sequence)
                            self.Computation_order.append(event)

                              #############################
                             ##### Event: activation ##### 
                            #############################
                            act_position_idx = pe_saa_position_idx 
                            act_preceding_count = 1
                            act_input_sequence = [[window_h, window_w, nfilter]]
                            act_output_sequence = []
                            ### add dependency
                            act_event_idx = len(self.Computation_order)
                            self.Computation_order[pe_saa_event_idx].proceeding_event.append(act_event_idx)
                            
                            event = EventMetaData("activation", act_position_idx, act_preceding_count, [], nlayer, act_input_sequence, act_output_sequence)
                            self.Computation_order.append(event)

                               ##########################
                             ##### Event: edram_wr ##### 
                            ###########################
                            edram_wr_position_idx = act_position_idx
                            edram_wr_preceding_count = 1
                            edram_wr_input_sequence = [[window_h, window_w, nfilter]]
                            edram_wr_output_sequence = []
                            ### add dependency
                            edram_wr_event_idx = len(self.Computation_order)
                            self.Computation_order[act_event_idx].proceeding_event.append(edram_wr_event_idx)
                            
                            event = EventMetaData("edram_wr", edram_wr_position_idx, edram_wr_preceding_count, [], nlayer, edram_wr_input_sequence, edram_wr_output_sequence)
                            self.Computation_order.append(event) 
                            
                               ################################
                             ##### Event: data_transfer ###### 
                            #################################
                            if nlayer+1 < len(self.layer_list):
                                data_transfer_source = edram_wr_position_idx
                                data_transfer_preceding_count = 1
                                data_transfer_input_sequence = []
                                data_transfer_output_sequence = []
                                ### add dependency
                                data_transfer_event_idx = len(self.Computation_order)
                                self.Computation_order[edram_wr_event_idx].proceeding_event.append(data_transfer_event_idx)

                                event = EventMetaData("data_transfer", [data_transfer_source], data_transfer_preceding_count, [], nlayer, data_transfer_input_sequence, data_transfer_output_sequence)
                                self.Computation_order.append(event) 
                            
                            
                                if self.layer_list[nlayer+1].layer_type != "fully":
                                    if self.feature_mat[nlayer][window_h][window_w][nfilter] == 0.0:
                                        self.feature_mat[nlayer][window_h][window_w][nfilter] = []
                                    self.feature_mat[nlayer][window_h][window_w][nfilter].append(data_transfer_event_idx)
                                else:
                                    if self.feature_mat[nlayer][window_h * self.input_w[nlayer+1] + window_w + nfilter * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0] == 0.0:
                                        self.feature_mat[nlayer][window_h * self.input_w[nlayer+1] + window_w + nfilter * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0] = []
                                    self.feature_mat[nlayer][window_h * self.input_w[nlayer+1] + window_w + nfilter * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0].append(data_transfer_event_idx)
                            

            elif self.layer_list[nlayer].layer_type == "pooling":
                for rty_idx in range(self.RT_num_y):
                    for rtx_idx in range(self.RT_num_x):
                        for pey_idx in range(self.PE_num_y):
                            for pex_idx in range(self.PE_num_x):
                                for mapping_data in self.layer_mapping_to_pe[rty_idx][rtx_idx][pey_idx][pex_idx]:
                                    if mapping_data.nlayer == nlayer:
                                        for inputs in mapping_data.inputs:
                                              ################################
                                             ##### Event: edram_rd_pool ##### 
                                            ################################
                                            input_sequence = inputs # [[h, w, c]]
                                            output_sequence = [[input_sequence[0][0] // self.pooling_h[nlayer], input_sequence[0][1] // self.pooling_w[nlayer], input_sequence[0][2]]] # [h, w, c]
                                            #print(input_sequence)
                                            #print(output_sequence)
                                            edram_rd_pool_position_idx = (rty_idx, rtx_idx, pey_idx, pex_idx) # pe position
                                            des_pe_idx = edram_rd_pool_position_idx
                                            ### add dependency
                                            edram_rd_pool_preceding_count = 0
                                            edram_rd_pool_preceding_event_list = []
                                            edram_rd_pool_event_index = len(self.Computation_order)
                                            for input_data in input_sequence:
                                                #print(input_data)
                                                preceding_list = self.feature_mat[nlayer-1][input_data[0]][input_data[1]][input_data[2]]
                                                if preceding_list != 0:
                                                    for pre_event in preceding_list:
                                                        if pre_event not in edram_rd_pool_preceding_event_list:
                                                            self.Computation_order[pre_event].proceeding_event.append(edram_rd_pool_event_index)
                                                            self.Computation_order[pre_event].position_idx.append(des_pe_idx)
                                                            edram_rd_pool_preceding_event_list.append(pre_event)
                                                            edram_rd_pool_preceding_count += 1

                                            #pool_preceding_count = len(edram_rd_pool_preceding_event_list)
                                            #print(pool_preceding_count)
                

                                        
                                            event = EventMetaData("edram_rd_pool", edram_rd_pool_position_idx, edram_rd_pool_preceding_count, [edram_rd_pool_event_index+1], nlayer, input_sequence, output_sequence)
                                            self.Computation_order.append(event)


                                              ##########################
                                             ##### Event: pooling ##### 
                                            ##########################
                                            pool_position_idx = edram_rd_pool_position_idx
                                            pool_preceding_count = 1
                                            pool_event_index = len(self.Computation_order)
                                            event = EventMetaData("pooling", pool_position_idx, pool_preceding_count, [pool_event_index+1], nlayer, input_sequence, output_sequence)
                                            self.Computation_order.append(event)

                                              ##########################
                                             ##### Event: edram_wr #### 
                                            ##########################
                                            edram_wr_position_idx = pool_position_idx
                                            edram_wr_preceding_count = 1
                                            event = EventMetaData("edram_wr", edram_wr_position_idx, edram_wr_preceding_count, [], nlayer, input_sequence, output_sequence)
                                            self.Computation_order.append(event)
                                            
                                              ################################
                                             ##### Event: data_transfer ##### 
                                            ################################
                                            if nlayer+1 < len(self.layer_list):
                                                data_transfer_source = edram_wr_position_idx
                                                data_transfer_preceding_count = 1
                                                data_transfer_input_sequence = []
                                                data_transfer_output_sequence = []
                                                ### add dependency
                                                data_transfer_event_idx = len(self.Computation_order)
                                                self.Computation_order[edram_wr_event_idx].proceeding_event.append(data_transfer_event_idx)

                                                event = EventMetaData("data_transfer", [data_transfer_source], data_transfer_preceding_count, [], nlayer, data_transfer_input_sequence, data_transfer_output_sequence)
                                                self.Computation_order.append(event) 
                                                        
                                                if self.layer_list[nlayer+1].layer_type != "fully":
                                                    if self.feature_mat[nlayer][output_sequence[0][0]][output_sequence[0][1]][output_sequence[0][2]] == 0.0:
                                                        self.feature_mat[nlayer][output_sequence[0][0]][output_sequence[0][1]][output_sequence[0][2]] = []
                                                    self.feature_mat[nlayer][output_sequence[0][0]][output_sequence[0][1]][output_sequence[0][2]].append(data_transfer_event_idx)
                                                else:
                                                    if self.feature_mat[nlayer][output_sequence[0][0] * self.input_w[nlayer+1] + output_sequence[0][1] + output_sequence[0][2] * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0] == 0.0:
                                                        self.feature_mat[nlayer][output_sequence[0][0] * self.input_w[nlayer+1] + output_sequence[0][1] + output_sequence[0][2] * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0] = []
                                                    self.feature_mat[nlayer][output_sequence[0][0] * self.input_w[nlayer+1] + output_sequence[0][1] + output_sequence[0][2] * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0].append(data_transfer_event_idx)
 
            
            elif self.layer_list[nlayer].layer_type == "fully":
                
                for nCU in range(len(self.cu_traverse_idx)):
                      ##############################
                     ##### Event: edram_rd_ir ##### 
                    ##############################
                    max_xb_input_len = 0
                    pos = self.cu_traverse_idx[nCU]
                    rty_idx, rtx_idx= pos[0], pos[1]
                    pey_idx, pex_idx = pos[2], pos[3]
                    cuy_idx, cux_idx = pos[4], pos[5]

                    for xby_idx in range(self.XB_num_y):
                        for xbx_idx in range(self.XB_num_x):
                            xbar_array_idx = xbx_idx + (xby_idx * self.XB_num_x) + \
                                            (cux_idx * self.XB_num) + \
                                            (cuy_idx * self.CU_num_x * self.XB_num) + \
                                            (pex_idx * self.CU_num * self.XB_num) + \
                                            (pey_idx * self.PE_num_x * self.XB_num * self.CU_num) + \
                                            (rtx_idx * self.PE_num * self.CU_num * self.XB_num) + \
                                            (rty_idx * self.RT_num_x * self.PE_num * self.CU_num * self.XB_num)
                            for fully in self.XB_array[xbar_array_idx].Fully:
                                if fully.nlayer == nlayer:
                                    max_xb_input_len = max(max_xb_input_len, len(fully.inputs))
                    #print(self.cu_traverse_idx[nCU], max_xb_input_len)
                
                    for nInp in range(max_xb_input_len):
                        data_feed_to_cu = []
                        for xby_idx in range(self.XB_num_y):
                            for xbx_idx in range(self.XB_num_x):
                                xbar_array_idx = xbx_idx + (xby_idx * self.XB_num_x) + \
                                                (cux_idx * self.XB_num) + \
                                                (cuy_idx * self.CU_num_x * self.XB_num) + \
                                                (pex_idx * self.CU_num * self.XB_num) + \
                                                (pey_idx * self.PE_num_x * self.XB_num * self.CU_num) + \
                                                (rtx_idx * self.PE_num * self.CU_num * self.XB_num) + \
                                                (rty_idx * self.RT_num_x * self.PE_num * self.CU_num * self.XB_num)
                                for fully in self.XB_array[xbar_array_idx].Fully:
                                    #print(fully)
                                    if fully.nlayer == nlayer:
                                        inp = fully.inputs[nInp]
                                        for d in inp:
                                            if d not in data_feed_to_cu:
                                                data_feed_to_cu.append(d)

                        #print("nCU", nCU, "data_feed_to_cu", data_feed_to_cu)
                
                        ### add dependency
                        edram_rd_ir_event_idx = len(self.Computation_order)
                        #print(edram_rd_ir_event_idx)
                        preceding_event_list = []
                        preceding_count = 0
                        des_pe_idx = pos[:-2]
                        if nlayer != 0: 
                            for input_data in data_feed_to_cu:
                                #print(input_data)
                                preceding_list = self.feature_mat[nlayer-1][input_data[1]][input_data[2]][input_data[3]]
                                #print(preceding_list)
                                if preceding_list != 0.0:
                                    for pre_event in preceding_list:
                                        if pre_event not in preceding_event_list:
                                            self.Computation_order[pre_event].proceeding_event.append(edram_rd_ir_event_idx)
                                            self.Computation_order[pre_event].position_idx.append(des_pe_idx)
                                            preceding_count += 1

                        input_sequence = data_feed_to_cu
                        output_sequence = []
                        position_idx = pos # cu position
                        event = EventMetaData("edram_rd_ir", position_idx, preceding_count, [], nlayer, input_sequence, output_sequence)
                        self.Computation_order.append(event)
                        
                          ############################### 
                         ##### Event: ou_operation ##### 
                        ###############################
                        for xby_idx in range(self.XB_num_y):
                            for xbx_idx in range(self.XB_num_x):
                                xbar_array_idx = xbx_idx + (xby_idx * self.XB_num_x) + \
                                                (cux_idx * self.XB_num) + \
                                                (cuy_idx * self.CU_num_x * self.XB_num) + \
                                                (pex_idx * self.CU_num * self.XB_num) + \
                                                (pey_idx * self.PE_num_x * self.XB_num * self.CU_num) + \
                                                (rtx_idx * self.PE_num * self.CU_num * self.XB_num) + \
                                                (rty_idx * self.RT_num_x * self.PE_num * self.CU_num * self.XB_num)
                                for fully in self.XB_array[xbar_array_idx].Fully:
                                    if fully.nlayer == nlayer:
                                        #print("fully  ", "nlayer", nlayer,"xbar_array_idx", xbar_array_idx)
                                        this_input = fully.inputs[nInp]
                                        num_input = this_input[0][0]
                                        #print(this_input, num_input)
                                        
                                        #print(this_input, num_input)
                                        xbar_block = []
                                        index = 0
                                        while index < len(fully.xbar_column):
                                            this_block = fully.xbar_column[index:index + self.OU_w]
                                            #this_block = [x for x in fully.xbar_column if x >= index and x < (index + self.OU_w)]
                                            xbar_block.append(this_block)
                                            index += self.OU_w
                                        #print(xbar_block)
                                        index = 0
                                        while index < len(this_input):
                                            input_sequence = [] # [[h, w, c]] each ou
                                            xbar_sequence = []
                                            input_count = 0

                                            while input_count < self.OU_h and index < len(this_input):
                                                #if this_input[index] != -1:
                                                input_sequence.append(this_input[index])
                                                xbar_sequence.append(index)
                                                index += 1
                                                input_count += 1
                                            for input_bit in range(self.input_bit):
                                                for w in xbar_block:
                                                    #print(input_bit, input_sequence, w)
                                                    
                                                    output_sequence = []  # [[(input_h, input_w, input_c, input_bit), (nfilter, ngrid, filter_bit)]]
                                                    for length in range(len(input_sequence)):
                                                        for column in range(len(w)):
                                                            hinput = input_sequence[length][0]
                                                            winput = input_sequence[length][1]
                                                            cinput = input_sequence[length][2]
                                                            crossbar_grid = self.XB_array[xbar_array_idx].crossbar_array[xbar_sequence[length]][w[column]]
                                                            filter_nfilter = crossbar_grid.nfilter
                                                            filter_ngrid = crossbar_grid.ngrid
                                                            filter_nbit = crossbar_grid.nbit
                                                            output_sequence.append([(num_input, hinput, winput, cinput, input_bit, ), (filter_nfilter, filter_ngrid, filter_nbit, )])

                                                    #print(output_sequence)
                                                
                                                    ### for input requirement CU的level才對, Todo
                                                    #for input_s in input_sequence:
                                                    #    idx = input_s[2] * self.input_h[nlayer] * self.input_w[nlayer] + input_s[0] * self.input_w[nlayer] + input_s[1]
                                                    #    if self.XB_array[xbar_array_idx].input_require[nlayer][idx] == -1:
                                                    #        self.XB_array[xbar_array_idx].input_require[nlayer][idx] = 1
                                                    #    else:
                                                    #        self.XB_array[nXxbar_array_idxB].input_require[nlayer][idx] += 1

                
                                                    ### add dependency
                                                    preceding_count = 1
                                                    ou_event_idx = len(self.Computation_order)
                                                    self.Computation_order[edram_rd_ir_event_idx].proceeding_event.append(ou_event_idx)


                                                    position_idx = self.XB_array[xbar_array_idx].position
                                                    event = EventMetaData("ou_operation", position_idx, preceding_count, [], nlayer, input_sequence, output_sequence)
                                                    self.Computation_order.append(event)
                
                                                        #########################
                                                      ##### Event: cu_saa ##### 
                                                    #########################
                                                    filter_list = []
                                                    cu_saa_output_sequence = []
                                                    position_idx = position_idx[:-2]
                                                    preceding_count = 1
                                                    input_nbit = output_sequence[0][0][4]
                                                                                                   
                                                    for col in range(len(w)): #同個ou col必須是同一張filter
                                                        filter_nfilter = output_sequence[col][1][0]
                                                        filter_nbit = output_sequence[col][1][2]
                                                        if filter_nfilter not in filter_list:
                                                            filter_list.append(filter_nfilter)

                                                    for nfilter in filter_list:
                                                        cu_saa_input_sequence = []  #[(input_nbit, filter_nfilter, filter_nbit)]   
                                                        for col in range(len(w)):
                                                            if nfilter == output_sequence[col][1][0]:
                                                                filter_nbit = output_sequence[col][1][2]
                                                                cu_saa_input_sequence.append((input_nbit, nfilter, filter_nbit))

                                                        ### add dependency
                                                        cu_saa_event_idx = len(self.Computation_order)
                                                        self.Computation_order[ou_event_idx].proceeding_event.append(cu_saa_event_idx)

                                                        grid = self.pe_saa_mat[nlayer][num_input][nfilter]
                                                        if grid == 0.0:
                                                            self.pe_saa_mat[nlayer][num_input][nfilter] = []

                                                        self.pe_saa_mat[nlayer][num_input][nfilter].append(cu_saa_event_idx)
                                                        
                                                        event = EventMetaData("cu_saa", position_idx, preceding_count, [], nlayer, cu_saa_input_sequence, cu_saa_output_sequence)
                                                        self.Computation_order.append(event)
             
                for nfilter in range(self.filter_n[nlayer]):
                      #########################
                     ##### Event: pe_saa ##### 
                    #########################
                    pe_saa_input_sequence = [] # [[window_h, window_w, nfilter, pre_CU_idx]] 
                    output_sequence = [[0, 0, nfilter]] # [input_window_h, input_window_w, nfilter]
                    num_input = 0

                    grid = self.pe_saa_mat[nlayer][num_input][nfilter]
                    if grid == 0.0:
                        self.pe_saa_mat[nlayer][num_input][nfilter] = []
                    

                    ### add dependency
                    preceding_count = 0
                    preceding_list = self.pe_saa_mat[nlayer][num_input][nfilter]
                    append_event_idx = len(self.Computation_order)
                    data_transfer_event_idx = append_event_idx

                    if preceding_list != 0:
                        first_pre_event_idx = preceding_list[0] 
                        pe_saa_position_idx = self.Computation_order[first_pre_event_idx].position_idx[:-2]
                        
                        for pre_event_idx in preceding_list:
                            if self.Computation_order[pre_event_idx].position_idx[:-2] != pe_saa_position_idx: # in different PE, need data transfer
                                self.Computation_order[pre_event_idx].proceeding_event.append(data_transfer_event_idx)
                                data_transfer_event_idx += 1
                                preceding_count += 1
                                source_pe_idx = self.Computation_order[pre_event_idx].position_idx[:-2]
                                  ################################
                                 ##### Event: data_transfer ##### 
                                ################################                                         
                                data_transfer_input_sequence = []
                                data_transfer_output_sequence = []
                                event = EventMetaData("data_transfer", [source_pe_idx, pe_saa_position_idx], 1, [], nlayer, data_transfer_input_sequence, data_transfer_output_sequence)
                                self.Computation_order.append(event)

                        pe_saa_event_idx = data_transfer_event_idx
                        for pre_event_idx in preceding_list:
                            if self.Computation_order[pre_event_idx].position_idx[:-2] == pe_saa_position_idx: # in same PE
                                self.Computation_order[pre_event_idx].proceeding_event.append(pe_saa_event_idx)
                                pre_CU_idx = self.Computation_order[pre_event_idx].position_idx
                                pe_saa_input_sequence.append([0, 0, nfilter, pre_CU_idx])
                                preceding_count += 1

                        ### data transfer dependency
                        #print(append_event_idx, pe_saa_event_idx)
                        for idx in range(append_event_idx, pe_saa_event_idx):
                            self.Computation_order[idx].proceeding_event.append(pe_saa_event_idx)

                                
                        pe_saa_position_idx = pe_saa_input_sequence[0][3][:-2] # pe_index
                        #print(pe_saa_input_sequence, position_idx)

                        event = EventMetaData("pe_saa", pe_saa_position_idx, preceding_count, [], nlayer, pe_saa_input_sequence, output_sequence)
                        self.Computation_order.append(event)
                
                      #############################
                     ##### Event: activation ##### 
                    #############################
                    act_position_idx = pe_saa_position_idx 
                    act_preceding_count = 1
                    act_input_sequence = [[0, 0, nfilter]]
                    act_output_sequence = []
                    ### add dependency
                    act_event_idx = len(self.Computation_order)
                    self.Computation_order[pe_saa_event_idx].proceeding_event.append(act_event_idx)
                    
                    event = EventMetaData("activation", act_position_idx, act_preceding_count, [], nlayer, act_input_sequence, act_output_sequence)
                    self.Computation_order.append(event)

            
                      ###########################
                     ##### Event: edram_wr #####
                    ###########################
                    edram_wr_position_idx = act_position_idx
                    edram_wr_preceding_count = 1
                    edram_wr_input_sequence = [[0, 0, nfilter]]
                    edram_wr_output_sequence = []
                    ### add dependency
                    edram_wr_event_idx = len(self.Computation_order)
                    self.Computation_order[act_event_idx].proceeding_event.append(edram_wr_event_idx)        

                    event = EventMetaData("edram_wr", edram_wr_position_idx, edram_wr_preceding_count, [], nlayer, edram_wr_input_sequence, edram_wr_output_sequence)
                    self.Computation_order.append(event) 

                      ################################
                     ##### Event: data_transfer ##### 
                    ################################
                    if nlayer+1 < len(self.layer_list):
                        data_transfer_source = edram_wr_position_idx
                        data_transfer_preceding_count = 1
                        data_transfer_input_sequence = []
                        data_transfer_output_sequence = []
                        ### add dependency
                        data_transfer_event_idx = len(self.Computation_order)
                        self.Computation_order[edram_wr_event_idx].proceeding_event.append(data_transfer_event_idx)

                        event = EventMetaData("data_transfer", [data_transfer_source], data_transfer_preceding_count, [], nlayer, data_transfer_input_sequence, data_transfer_output_sequence)
                        self.Computation_order.append(event) 
                                
                        
                        if self.layer_list[nlayer+1].layer_type != "fully":
                            if self.feature_mat[nlayer][window_h][window_w][nfilter] == 0.0:
                                self.feature_mat[nlayer][window_h][window_w][nfilter] = []
                            self.feature_mat[nlayer][window_h][window_w][nfilter].append(data_transfer_event_idx)
                        else:
                            if self.feature_mat[nlayer][window_h * self.input_w[nlayer+1] + window_w + nfilter * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0] == 0.0:
                                self.feature_mat[nlayer][window_h * self.input_w[nlayer+1] + window_w + nfilter * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0] = []
                            self.feature_mat[nlayer][window_h * self.input_w[nlayer+1] + window_w + nfilter * self.input_h[nlayer+1] * self.input_w[nlayer+1]][0][0].append(data_transfer_event_idx)
                    

        print('Order generated!')
    
    def __str__(self):
        return str(self.__dict__)