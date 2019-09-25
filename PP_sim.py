from Mapping import DefaultMapping
from Mapping import ParallelismMapping
from Mapping import TransferMapping

from OrderGenerator import OrderGenerator
from Controller import Controller

import time, sys

def main():
    mapping = int(sys.argv[1])
    scheduling = int(sys.argv[2])

    ### Mapping ##
    print("Mapping policy:  ", end="")
    if mapping == 0: # DefaultMapping
        print("DefaultMapping")
        mapping_information = DefaultMapping()
        mapping_str = "DefaultMapping"
    elif mapping == 1: # ParallelismMapping
        print("ParallelismMapping")
        mapping_information = ParallelismMapping()
        mapping_str = "ParallelismMapping"
    elif mapping == 2: # TransferMapping
        print("TransferMapping") 
        mapping_information = TransferMapping()
        mapping_str = "TransferMapping"
    
    ### Scheduling ###
    print("Scheduling policy: ", end="")
    if scheduling == 0: # Non-pipeline
        print("Non-pipeline")
        isPipeLine = False
    elif scheduling == 1: # Pipeline
        print("Pipeline")
        isPipeLine = True
    print()

    ### Free buffer ###
    isFreeBuffer = True

    ### Trace ###
    isTrace_order = False
    isTrace_controller = False

    ### Generate computation order graph ### 
    start_order_time = time.time()
    print("--- Generate computation order graph ---")

    order_generator = OrderGenerator(mapping_information, isTrace_order, isFreeBuffer)

    end_order_time = time.time()
    print("--- Computation order graph is generated in %s seconds ---\n" % (end_order_time - start_order_time))
    
    ## Power and performance simulation ###
    start_simulation_time = time.time()
    print("--- Power and performance simulation---")

    controller = Controller(order_generator, isPipeLine, isTrace_controller, mapping_str, isFreeBuffer)
    controller.run()

    end_simulation_time = time.time()
    print("--- Simulate in %s seconds ---\n" % (end_simulation_time - start_simulation_time))

    controller.print_statistics_result()


    # ### Energy估算
    # from configs.ModelConfig import ModelConfig
    # from HardwareMetaData import HardwareMetaData
    # input_bit = ModelConfig().input_bit
    # filter_bit = ModelConfig().filter_bit

    # router = 0
    # edram_rd = 0
    # edram_wr = 0

    # edram_rd_bus = 0
    # pe_saa_bus = 0
    # act_bus = 0
    # edram_wr_bus = 0

    # act = 0
    # pe_saa = 0
    # pe_or = 0
    # cu_saa = 0
    # adc = 0
    # dac = 0
    # crossbar = 0
    # cu_ir = 0
    # cu_or = 0

    # # layer1
    # window = 9 #(7-5+1)**2
    # filter_size = 75 # 5*5*3
    # filter_num = 20
    # ou_per_filter = filter_size / HardwareMetaData().OU_h # 75 / 5
    # filter_per_cu = 4 # 會分配到n個CU
    # num_ou = 4320
    # cu_per_input = 4
    # pe_per_input = 2

    # # saa data transfer
    # ## 寫到自己的buffer
    # # edram_wr_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus * 2 # 下面的PE有2個CU
    # # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer * 2 # 下面的PE有2個CU
    # # router += window * filter_num * input_bit * HardwareMetaData().Energy_router * cu_per_input
    # ## 寫到目標buffer
    # # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer * 2 # 下面的PE有2個CU

    # # off chip transfer
    # router += window * filter_size * input_bit * HardwareMetaData().Energy_router * pe_per_input * 2# 這邊沒做PE內CU要求依樣的資料連擊
    # edram_wr += window * filter_size * input_bit * HardwareMetaData().Energy_edram_buffer * pe_per_input
    
    # edram_rd += window * filter_size * input_bit * HardwareMetaData().Energy_edram_buffer * cu_per_input
    # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer
    
    # # transfer between layer
    # router += window * filter_num * input_bit * HardwareMetaData().Energy_router 
    # edram_rd += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer 
    # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer

    # # bus
    # edram_rd_bus += window * filter_size * input_bit * HardwareMetaData().Energy_bus * cu_per_input
    # pe_saa_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus * filter_per_cu * 2 # read + write
    # act_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus
    # edram_wr_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus

    # act += window * filter_num * HardwareMetaData().Energy_activation
    # pe_saa += window * filter_num * HardwareMetaData().Energy_shift_and_add * filter_per_cu 
    # pe_or += window * filter_num * input_bit * HardwareMetaData().Energy_or * filter_per_cu * 2 # saa: read + write
    # pe_or += window * filter_num * input_bit * HardwareMetaData().Energy_or # act
    # cu_saa += window * filter_num * filter_bit * HardwareMetaData().Energy_shift_and_add * input_bit * ou_per_filter
    # adc += num_ou * HardwareMetaData().Energy_adc
    # dac += num_ou * HardwareMetaData().Energy_dac
    # crossbar += num_ou * HardwareMetaData().Energy_crossbar
    # cu_ir += window * filter_size * input_bit * HardwareMetaData().Energy_ir_in_cu # write to ir
    # cu_ir += window * filter_size * input_bit * HardwareMetaData().Energy_ir_in_cu # 分到多CU不能reuse input才會變多
    # cu_or += input_bit * window * filter_num * filter_bit * HardwareMetaData().Energy_or_in_cu * input_bit * ou_per_filter * 2 # read+write

    # layer2
    # window = 4
    # filter_size = 80 # 5*5*3
    # filter_num = 10
    # ou_per_filter = filter_size / HardwareMetaData().OU_h
    # filter_per_cu = 4 # 會分配到n個CU
    # num_ou = 1024
    # cu_per_input = 2
    # pe_per_input = 1

    # saa data transfer
    ## 寫到自己的buffer
    # edram_wr_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus * 2 # 下面的PE有2個CU
    # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer * 2 # 下面的PE有2個CU
    # router += window * filter_num * input_bit * HardwareMetaData().Energy_router * cu_per_input
    ## 寫到目標buffer
    # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer * 2 # 下面的PE有2個CU

    # off chip transfer
    # router += window * filter_size * input_bit * HardwareMetaData().Energy_router * pe_per_input * 2# 這邊沒做PE內CU要求依樣的資料連擊
    # edram_wr += window * filter_size * input_bit * HardwareMetaData().Energy_edram_buffer * pe_per_input
    
    # edram_rd += window * filter_size * input_bit * HardwareMetaData().Energy_edram_buffer * cu_per_input
    # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer
    
    # # transfer between layer
    # router += window * filter_num * input_bit * HardwareMetaData().Energy_router 
    # edram_rd += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer 
    # edram_wr += window * filter_num * input_bit * HardwareMetaData().Energy_edram_buffer

    # bus
    # edram_rd_bus += window * filter_size * input_bit * HardwareMetaData().Energy_bus * cu_per_input
    # pe_saa_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus * filter_per_cu * 2 # read + write
    # act_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus
    # edram_wr_bus += window * filter_num * input_bit * HardwareMetaData().Energy_bus

    # act += window * filter_num * HardwareMetaData().Energy_activation
    # pe_saa += window * filter_num * HardwareMetaData().Energy_shift_and_add * filter_per_cu 
    # pe_or += window * filter_num * input_bit * HardwareMetaData().Energy_or * filter_per_cu * 2 # saa: read + write
    # pe_or += window * filter_num * input_bit * HardwareMetaData().Energy_or # act
    # cu_saa += window * filter_num * filter_bit * HardwareMetaData().Energy_shift_and_add * input_bit * ou_per_filter
    # adc += num_ou * HardwareMetaData().Energy_adc
    # dac += num_ou * HardwareMetaData().Energy_dac
    # crossbar += num_ou * HardwareMetaData().Energy_crossbar
    # cu_ir += window * filter_size * input_bit * HardwareMetaData().Energy_ir_in_cu * 2 # write to ir, input cannot reuse 2個CU
    # cu_ir += window * filter_size * input_bit * HardwareMetaData().Energy_ir_in_cu * 2 * 4 # read ir, input cannot reuse 2個CU, CU內有4XB
    # cu_or += input_bit * window * filter_num * filter_bit * HardwareMetaData().Energy_or_in_cu * input_bit * ou_per_filter * 2 # read+write


    # edram = edram_wr + edram_rd
    # bus = edram_rd_bus + pe_saa_bus + act_bus + edram_wr_bus

    # print("router: %.4e" %(router))
    # print("edram: %.4e" %(edram))
    # print("bus: %.4e" %(bus))
    # print("act: %.4e" %(act))
    # print("pe_saa: %.4e" %(pe_saa))
    # print("pe_or: %.4e" %(pe_or))
    # print("cu_saa: %.4e" %(cu_saa))
    # print("adc: %.4e" %(adc))
    # print("dac: %.4e" %(dac))
    # print("crossbar: %.4e" %(crossbar))
    # print("cu_ir: %.4e" %(cu_ir))
    # print("cu_or: %.4e" %(cu_or))

if __name__ == '__main__':
    main()

