
from math import floor

class HardwareConfig(object):
    def __init__(self, buffer_size):
        # Architecture
        self.Router_num_y = 14
        self.Router_num_x = 13
        self.Router_num = self.Router_num_y * self.Router_num_x
        self.PE_num_y = 2 # c-mesh
        self.PE_num_x = 2 # c-mesh
        self.PE_num = self.PE_num_y * self.PE_num_x
        self.CU_num = 12
        self.Xbar_num = 8
        self.Xbar_h = 128
        self.Xbar_w = 128
        self.OU_h = 9   
        self.OU_w = 8
        self.total_pe_num = self.Router_num * self.PE_num
        
        self.PE_frequency = 1.2 # GHz
        
        # on-chip eDRAM buffer
        self.eDRAM_buffer_size  = buffer_size # KB
        self.eDRAM_buffer_bandwidth = 20.48 # GB/s
        self.eDRAM_buffer_bus_width = 256 # bits
        self.eDRAM_buffer_rd_wr_data_per_cycle = None
        self.eDRAM_buffer_read_to_IR_cycles = None

        # bus
        self.bus_wires = 384

        # router
        self.router_frequency = 1.2 # GHz
        self.router_flit_size = 32 # bits
        self.router_ports = 8

        # activation
        self.activation_num = 2
        
        # shift-and-add
        self.shift_and_add_num_in_PE = 1

        # pooling
        self.pooling_num = 1

        # OR
        self.OR_size_in_PE = 3 # KB
        self.OR_bus_width = 128

        # CU
        self.DAC_num_in_CU = 1024 # 8x128
        self.DAC_resolution = 1  # cannot change
        self.crossbar_num_in_CU = 8
        self.SH_num_in_CU = 1024
        self.cell_bit_width = 2
        self.ADC_num = 8
        self.ADC_resolution = 3
        self.shift_and_add_num_in_CU = 4
        self.IR_size = 2 # KB
        self.OR_size_in_CU = 256 # B

        # links
        # self.links_frequency = 1.6 # GHz
        # self.links_bw = 6.4 # GB/s

        self.cycle_time = 7.68 # 15.6 * (self.ADC_resolution/3) * (32/65) # scaling from W. H. Chen's paper
        self.interconnect_step_num = int(self.cycle_time * self.router_frequency) # router frequency = PE frequency

        # Dynamic power (mW)
        self.Power_eDRAM_buffer    = 20.7
        self.Power_eDRAM_to_CU_bus = 7
        self.Power_activation      = 0.52 / self.shift_and_add_num_in_PE
        self.Power_shift_and_add_in_PE = 0.05 / self.shift_and_add_num_in_PE
        self.Power_pooling  = 0.4 / self.pooling_num
        self.Power_OR_in_PE = 1.68
        self.Power_router   = 42 / 4

        self.Power_DAC = 4 / self.DAC_num_in_CU
        self.Power_crossbar = 2.4 / self.crossbar_num_in_CU
        self.Power_S_H = 0.01 / self.SH_num_in_CU
        self.Power_ADC = 16 / self.ADC_num * (2**self.ADC_resolution / (self.ADC_resolution+1)) / (2**8/(8+1)) # scaling
        self.Power_IR = 1.24
        self.Power_OR_in_CU = 0.23
        self.Power_shift_and_add_in_CU = 0.2 / self.shift_and_add_num_in_CU

        # Leakage
        self.Leakage_eDRAM_buffer = 0
        self.Leakage_eDRAM_to_CU_bus = 0
        self.Leakage_activation = 0
        self.Leakage_shift_and_add_in_PE = 0
        self.Leakage_pooling = 0
        self.Leakage_OR_in_PE = 0
        self.Leakage_router = 0

        self.Leakage_DAC = 0
        self.Leakage_crossbar = 0
        self.Leakage_S_H = 0
        self.Leakage_ADC = 0
        self.Leakage_IR =  0
        self.Leakage_OR_in_CU = 0
        self.Leakage_shift_and_add_in_CU = 0
        #self.Leakage_link = 0
        #self.Leakage_off_chip = 52.8mW

        
        # mW = 10^-3 nJ/ns
        # Energy consumption (nJ per data)
        self.Energy_eDRAM_buffer    = self.Power_eDRAM_buffer * 0.1 / 1024
        self.Energy_eDRAM_to_CU_bus = self.Power_eDRAM_to_CU_bus * 0.1 / 1024
        self.Energy_activation      = self.Power_activation * 0.1 / 64
        self.Energy_shift_and_add_in_PE = self.Power_shift_and_add_in_PE * 0.1 / 128
        self.Energy_pooling   = self.Power_pooling * 0.1 / 1024
        self.Energy_OR_in_PE  = self.Power_OR_in_PE * 0.1 / 128
        self.Energy_router = self.Power_router * 0.1 / 128

        self.Energy_DAC = self.Power_DAC * 0.1
        self.Energy_crossbar = self.Power_crossbar * 0.1 / (128*128) # per cell
        self.Energy_S_H = self.Power_S_H * 0.1
        self.Energy_ADC = self.Power_ADC * 0.1 / 128
        self.Energy_IR =  self.Power_IR * 0.1 / 1024
        self.Energy_OR_in_CU = self.Power_OR_in_CU * 0.1 / 1024
        self.Energy_shift_and_add_in_CU =  self.Power_shift_and_add_in_CU * 0.1 / 256

        # per operation unit (ou)
        # self.Energy_ou_dac        = self.Power_DAC / self.PE_frequency / self.DAC_num * self.OU_h
        # self.Energy_ou_crossbar   = self.Power_crossbar / self.PE_frequency / self.crossbar_num * ((self.OU_h * self.OU_w) / (self.Xbar_h * self.Xbar_w))
        # self.Energy_ou_adc        = self.Power_ADC / self.PE_frequency / self.ADC_num * self.OU_w
        # self.Energy_ou_ssa        = self.Energy_shift_and_add_in_CU * self.OU_w
        # self.Energy_ir_in_cu      = self.Power_IR / self.PE_frequency / self.eDRAM_buffer_bus_width
        # self.Energy_or_in_cu      = self.Power_OR_in_CU / self.PE_frequency / 128
        
        #self.Energy_link          = self.Power_link / self.links_frequency / self.links_bw / 8 / 77 / 4 # 8 bits = 1 byte # total links = 7*6+5*7=77

        

        # Off-chip:
        self.off_chip_Rd_bw = 3.2 # GB/s
        self.off_chip_Wr_bw = 3.2 # GB/s
        self.Energy_off_chip_Rd = 80.3  * 0.001  / 8 # nJ per bit (0.16 nJ per 16 bit data)
        self.Energy_off_chip_Wr = 82.719 * 0.001 / 8 # nJ per bit
        
    def __str__(self):
        return str(self.__dict__)
