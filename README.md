# Simulator

run: python3 PP_sim.py [model] [scheduling] [partitioning_h] [partitioning_w] [buffer_size]

Parameters:
  * model:  NN model name. The model topology is defined in ModelConfig.py
  * scheduling: Non-pipeline/Pipeline
  * partitioning_h (or partitioning_w): partition the height (or width) of crossbar array
    * For example: partitioning_h = 2; partitioning_w = 2; the crossbar array size is 128x128; the partitioning size is (128/2)x(128/2)
  * buffer_size: The on-chip eDRAM buffer capacity

* The Hardware configuration is defined in HardwareConfig.py
