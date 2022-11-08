'''
#L1 Level
weight_l1_overhead   = 0#1
data_l1_overhead     = 0#5
SIMD_overhead        = 0#16 #//fixed
output_l1_overhead   = 0#5
#L2 Level
weight_l2_overhead   = 0#3
l1_loop_overhead     = 0#2
data_l2_overhead     = 0#88
output_l2_overhead   = 0#163
#DRAM Level
bias_read_overhead   = 0#3
bias_write_overhead  = 0#121
l2_loop_overhead     = 0#2
output_II            = 2
'''

#Overhead define
#L1 Level
weight_l1_overhead   = 1
data_l1_overhead     = 5
SIMD_overhead        = 8#16 #//fixed
output_l1_overhead   = 5
#L2 Level
weight_l2_overhead   = 3
l1_loop_overhead     = 2
data_l2_overhead     = 88
output_l2_overhead   = 163/2

#data precision
scale = 1#2 #1=INT8/2=INT4
out_scale = 4
#scale = 0.25 #FP32
#out_scale = 1 #FP32
input_byte = 1 / scale
weight_byte = 1 / scale
output_byte = out_scale / scale
#DRAM Level
bias_read_overhead   = 3
bias_write_overhead  = 121
l2_loop_overhead     = 2
#output_II            = 2
#burst read
dram_burst_delay     = 76 #//??????
#dram_burst_delay     = 64 #//??????
dram_continous_delay = 2
dram_burst_size      = 4096 #//TODO: Caculate correctly

class HW_DEF:
    def __init__(self, ARRAY_K, ARRAY_C, ARRAY_H, ARRAY_W, L1_BANK, L2_BANK):
        self.ARRAY_K = ARRAY_K #//if output stationary, 1
        self.ARRAY_C = ARRAY_C #//if input stationary,  1
        self.ARRAY_H = ARRAY_H #//if weight stationary, 1
        self.ARRAY_W = ARRAY_W #//if weight stationary, 1
        self.L1_BANK = L1_BANK
        self.L2_BANK = L2_BANK

class MAPPING_DEF:
    def __init__(self,
                 L2_TILENUM_K, L2_TILENUM_C, L2_TILENUM_H, L2_TILENUM_W, L2_TILENUM_R, L2_TILENUM_S,
                 L2_ORDER_K, L2_ORDER_C, L2_ORDER_H, L2_ORDER_W, L2_ORDER_R, L2_ORDER_S,
                 L1_TILENUM_K, L1_TILENUM_C, L1_TILENUM_H, L1_TILENUM_W, L1_TILENUM_R, L1_TILENUM_S,
                 L1_ORDER_K, L1_ORDER_C, L1_ORDER_H, L1_ORDER_W, L1_ORDER_R, L1_ORDER_S,
                 TILE_K, TILE_C, TILE_H, TILE_W, TILE_R, TILE_S,
                 density):
        self.L2_TILENUM_K = L2_TILENUM_K
        self.L2_TILENUM_C = L2_TILENUM_C
        self.L2_TILENUM_H = L2_TILENUM_H
        self.L2_TILENUM_W = L2_TILENUM_W
        self.L2_TILENUM_R = L2_TILENUM_R
        self.L2_TILENUM_S = L2_TILENUM_S

        self.L2_ORDER_K = L2_ORDER_K #0~5, smaller is inner
        self.L2_ORDER_C = L2_ORDER_C
        self.L2_ORDER_H = L2_ORDER_H
        self.L2_ORDER_W = L2_ORDER_W
        self.L2_ORDER_R = L2_ORDER_R
        self.L2_ORDER_S = L2_ORDER_S

        self.L1_TILENUM_K = L1_TILENUM_K
        self.L1_TILENUM_C = L1_TILENUM_C
        self.L1_TILENUM_H = L1_TILENUM_H
        self.L1_TILENUM_W = L1_TILENUM_W
        self.L1_TILENUM_R = L1_TILENUM_R
        self.L1_TILENUM_S = L1_TILENUM_S

        self.L1_ORDER_K = L1_ORDER_K #0~5, smaller is inner
        self.L1_ORDER_C = L1_ORDER_C
        self.L1_ORDER_H = L1_ORDER_H
        self.L1_ORDER_W = L1_ORDER_W
        self.L1_ORDER_R = L1_ORDER_R
        self.L1_ORDER_S = L1_ORDER_S

        self.TILE_K = TILE_K
        self.TILE_C = TILE_C
        self.TILE_H = TILE_H
        self.TILE_W = TILE_W
        self.TILE_R = TILE_R
        self.TILE_S = TILE_S

        self.K_L1 = TILE_K
        self.C_L1 = TILE_C
        self.H_L1 = TILE_H
        self.W_L1 = TILE_W
        self.R_L1 = TILE_R
        self.S_L1 = TILE_S
        self.H_in_L1 = self.H_L1 + self.R_L1 -1
        self.W_in_L1 = self.W_L1 + self.S_L1 -1

        self.K_L2 = self.K_L1 *self.L1_TILENUM_K
        self.C_L2 = self.C_L1 *self.L1_TILENUM_C
        self.H_L2 = self.H_L1 *self.L1_TILENUM_H
        self.W_L2 = self.W_L1 *self.L1_TILENUM_W
        self.R_L2 = self.R_L1 *self.L1_TILENUM_R
        self.S_L2 = self.S_L1 *self.L1_TILENUM_S
        self.H_in_L2 = self.H_L2 + self.R_L2 -1
        self.W_in_L2 = self.W_L2 + self.S_L2 -1

        self.density = density

def checkFitBufferMappingSparseAccel(hw_def, mapping_def, buffer_estimated, verbose=0, ID=0):
    weight_l2_size = mapping_def.K_L2 * mapping_def.C_L2 * mapping_def.R_L2 * mapping_def.S_L2
    input_l2_size = mapping_def.C_L2 * mapping_def.H_in_L2 * mapping_def.W_in_L2
    output_l2_size = mapping_def.K_L2 * mapping_def.H_L2 * mapping_def.W_L2

    weight_l1_size = mapping_def.K_L1 * mapping_def.C_L1 * mapping_def.R_L1 * mapping_def.S_L1
    input_l1_size = mapping_def.C_L1 * mapping_def.H_in_L1 * mapping_def.W_in_L1
    output_l1_size = mapping_def.K_L1 * mapping_def.H_L1 * mapping_def.W_L1

    input_l1_loop_size = mapping_def.H_in_L1 * mapping_def.W_in_L1
    output_l1_loop_size = mapping_def.H_L1 * mapping_def.W_L1

    alert_weight_l1_constraint = weight_l1_size > buffer_estimated['l1_weight']
    alert_input_l1_constraint = input_l1_size > buffer_estimated['l1_input']
    alert_output_l1_constraint = output_l1_size > buffer_estimated['l1_output']
    alert_weight_l2_constraint = weight_l2_size > buffer_estimated['l2_weight']
    alert_input_l2_constraint = input_l2_size > buffer_estimated['l2_input']
    alert_output_l2_constraint = output_l2_size > buffer_estimated['l2_output']
    alert_l1_larger_than_l2 = (buffer_estimated['l1_weight'] > buffer_estimated['l2_weight']) or \
                                (buffer_estimated['l1_input'] > buffer_estimated['l2_input']) or \
                                (buffer_estimated['l1_output'] > buffer_estimated['l2_output'])
    #alert_input_l1_loop_constraint = input_l1_loop_size > (56*56)
    #alert_output_l1_loop_constraint = output_l1_loop_size > (56*56)

    if alert_weight_l1_constraint or alert_input_l1_constraint or alert_output_l1_constraint or \
        alert_weight_l2_constraint or alert_input_l2_constraint or alert_output_l2_constraint or \
        alert_l1_larger_than_l2:
        #print(alert_weight_l1_constraint, alert_input_l1_constraint, alert_output_l1_constraint, alert_weight_l2_constraint, alert_input_l2_constraint, alert_output_l2_constraint, alert_l1_larger_than_l2)
        #print(buffer_estimated['l2_weight'], weight_l2_size)
        #print(buffer_estimated['l2_input'], input_l2_size)
        #print(buffer_estimated['l2_output'], output_l2_size)
        return False
    return True #Buffer mapping is valid

def checkLegalConstraintSparseAccel(hw_def, mapping_def, verbose=0, ID=0):
    #FIXME for weight stationary
    return True #constraint passed
    weight_buffer_size = mapping_def.K_L2 * mapping_def.C_L2 * mapping_def.R_L2 * mapping_def.S_L2 / hw_def.ARRAY_K
    input_buffer_size = mapping_def.C_L2 * mapping_def.H_in_L2 * mapping_def.W_in_L2 / hw_def.ARRAY_C
    output_buffer_size = mapping_def.K_L2 * mapping_def.H_L2 * mapping_def.W_L2 / hw_def.ARRAY_K
    input_l1_loop_size = mapping_def.H_in_L1 * mapping_def.W_in_L1
    output_l1_loop_size = mapping_def.H_L1 * mapping_def.W_L1

    alert_weight_buffer_constraint = weight_buffer_size > 2304
    alert_input_buffer_constraint = input_buffer_size > 2304
    alert_output_buffer_constraint = output_buffer_size > 1600
    alert_input_l1_loop_constraint = input_l1_loop_size > (56*56)
    alert_output_l1_loop_constraint = output_l1_loop_size > (56*56)

    if alert_weight_buffer_constraint or alert_input_buffer_constraint or alert_output_buffer_constraint \
        or alert_input_l1_loop_constraint or alert_output_l1_loop_constraint:
        #print(weight_buffer_size,input_buffer_size,output_buffer_size,input_l1_loop_size,output_l1_loop_size)
        return False #Err
    return True #constraint passed

def calculateSparseAccel(hw_def, mapping_def, verbose=0, ID=0):

    is_weight_stationary = hw_def.ARRAY_W * hw_def.ARRAY_H == 1
    is_output_stationary = hw_def.ARRAY_C == 1
    is_input_stationary = hw_def.ARRAY_K == 1

    if is_weight_stationary:
        #HW : PE size
        PE_num           = hw_def.ARRAY_K * hw_def.ARRAY_C * hw_def.ARRAY_H * hw_def.ARRAY_W
        #HW : L1 BW
        weight_bandwidth = hw_def.ARRAY_K * hw_def.L1_BANK
        data_bandwidth   = hw_def.ARRAY_C * hw_def.L1_BANK
        output_bandwidth = hw_def.ARRAY_K * hw_def.L1_BANK
        #HW : L2 BW
        weight_l2_bandwidth = hw_def.ARRAY_K * hw_def.L2_BANK
        data_l2_bandwidth   = hw_def.ARRAY_C * hw_def.L2_BANK
        output_l2_bandwidth = hw_def.ARRAY_K * hw_def.L2_BANK #GROUP is just partial sum
        #HW : DRAM bitwidth
        weight_dram_bitwidth = hw_def.ARRAY_K
        data_dram_bitwidth   = hw_def.ARRAY_C
        output_dram_bitwidth = hw_def.ARRAY_K
        #HW : DRAM burst
        weight_l2_burst_size = (mapping_def.K_L2/hw_def.ARRAY_K)*mapping_def.C_L2*mapping_def.R_L2*mapping_def.S_L2*weight_dram_bitwidth
        data_l2_burst_size   = mapping_def.W_in_L2*data_dram_bitwidth
        output_l2_burst_size = mapping_def.W_L2*output_dram_bitwidth
    elif is_output_stationary:
        #HW : PE size
        PE_num           = hw_def.ARRAY_K * hw_def.ARRAY_C * hw_def.ARRAY_H * hw_def.ARRAY_W
        #HW : L1 BW
        weight_bandwidth = hw_def.ARRAY_K * hw_def.L1_BANK #GROUP is just copy
        data_bandwidth   = hw_def.ARRAY_H * hw_def.ARRAY_W * hw_def.L1_BANK
        output_bandwidth = hw_def.ARRAY_H * hw_def.ARRAY_W * hw_def.L1_BANK
        #HW : L2 BW
        weight_l2_bandwidth = hw_def.ARRAY_K * hw_def.L2_BANK
        data_l2_bandwidth   = hw_def.ARRAY_H * hw_def.ARRAY_W * hw_def.L2_BANK
        output_l2_bandwidth = hw_def.ARRAY_H * hw_def.ARRAY_W * hw_def.L2_BANK
        #HW : DRAM bitwidth
        weight_dram_bitwidth = hw_def.ARRAY_K
        data_dram_bitwidth   = hw_def.ARRAY_H * hw_def.ARRAY_W
        output_dram_bitwidth = hw_def.ARRAY_H * hw_def.ARRAY_W
        #HW : DRAM burst
        weight_l2_burst_size = (mapping_def.K_L2/hw_def.ARRAY_K)*mapping_def.C_L2*mapping_def.R_L2*mapping_def.S_L2*weight_dram_bitwidth
        data_l2_burst_size   = mapping_def.C_L2*data_dram_bitwidth
        output_l2_burst_size = mapping_def.K_L2*output_dram_bitwidth
    elif is_input_stationary:
        #raise "unsupported"
        #HW : PE size
        PE_num           = hw_def.ARRAY_K * hw_def.ARRAY_C * hw_def.ARRAY_H * hw_def.ARRAY_W
        #HW : L1 BW
        weight_bandwidth = hw_def.ARRAY_C * hw_def.L1_BANK
        data_bandwidth   = hw_def.ARRAY_W * hw_def.L1_BANK
        output_bandwidth = hw_def.ARRAY_W * hw_def.L1_BANK
        #HW : L2 BW
        weight_l2_bandwidth = hw_def.ARRAY_C * hw_def.L2_BANK
        data_l2_bandwidth   = hw_def.ARRAY_W * hw_def.L2_BANK
        output_l2_bandwidth = hw_def.ARRAY_W * hw_def.L2_BANK
        #HW : DRAM bitwidth
        weight_dram_bitwidth = hw_def.ARRAY_C
        data_dram_bitwidth   = hw_def.ARRAY_W
        output_dram_bitwidth = hw_def.ARRAY_W
        #HW : DRAM burst
        weight_l2_burst_size = mapping_def.K_L2*(mapping_def.C_L2/hw_def.ARRAY_C)*mapping_def.R_L2*mapping_def.S_L2*weight_dram_bitwidth
        data_l2_burst_size   = mapping_def.C_L2*data_dram_bitwidth
        output_l2_burst_size = mapping_def.K_L2*output_dram_bitwidth
    else:
        raise "unsupported dataflow"


    #iteration
    l2_loop_iteration = mapping_def.L2_TILENUM_K*mapping_def.L2_TILENUM_C*mapping_def.L2_TILENUM_R*mapping_def.L2_TILENUM_S*mapping_def.L2_TILENUM_W*mapping_def.L2_TILENUM_H
    l1_loop_iteration = mapping_def.L1_TILENUM_K*mapping_def.L1_TILENUM_C*mapping_def.L1_TILENUM_R*mapping_def.L1_TILENUM_S*mapping_def.L1_TILENUM_W*mapping_def.L1_TILENUM_H
    

    #SIMD
    SIMD_iteration     = (mapping_def.W_L1*mapping_def.H_L1*mapping_def.C_L1*mapping_def.K_L1 * mapping_def.density)/(PE_num)
    SIMD_cycle         = (SIMD_iteration     +SIMD_overhead)*l1_loop_iteration
    
    #L1 cycle
    weight_l1_iteration= mapping_def.K_L1*mapping_def.C_L1*mapping_def.R_L1*mapping_def.S_L1 / weight_bandwidth
    data_l1_iteration  = mapping_def.W_L1*mapping_def.H_L1*mapping_def.C_L1                  / data_bandwidth
    output_l1_iteration= mapping_def.W_L1*mapping_def.H_L1*mapping_def.K_L1                  / output_bandwidth
    weight_l1_cycle    = (weight_l1_iteration+weight_l1_overhead)*l1_loop_iteration
    data_l1_cycle      = (data_l1_iteration  +data_l1_overhead)*l1_loop_iteration
    output_l1_cycle    = (output_l1_iteration+output_l1_overhead)*l1_loop_iteration
       
    #L2 cycle
    weight_l2_size = mapping_def.K_L2*mapping_def.C_L2*mapping_def.R_L2*mapping_def.S_L2
    data_l2_size   = mapping_def.C_L2*mapping_def.H_in_L2*mapping_def.W_in_L2
    output_l2_size = mapping_def.K_L2*mapping_def.H_L2*mapping_def.W_L2
    #print(weight_l2_size*mapping_def.L2_TILENUM_K*mapping_def.L2_TILENUM_C*mapping_def.L2_TILENUM_R*mapping_def.L2_TILENUM_S,
    #         data_l2_size*mapping_def.L2_TILENUM_C*mapping_def.L2_TILENUM_W*mapping_def.L2_TILENUM_H,
    #         output_l2_size*mapping_def.L2_TILENUM_K*mapping_def.L2_TILENUM_W*mapping_def.L2_TILENUM_H)
    #print(weight_l2_size/weight_l2_burst_size, data_l2_size/data_l2_burst_size, output_l2_size/output_l2_burst_size)
    
    #weight_l2_cycle = (weight_l2_size*max(1, weight_dram_bitwidth*(weight_byte*8)/512) / weight_dram_bitwidth) + (weight_l2_size/weight_l2_burst_size)*dram_burst_delay \
    weight_l2_cycle = (weight_l2_size*(weight_dram_bitwidth*(weight_byte*8)/512) / weight_dram_bitwidth) + (weight_l2_size/weight_l2_burst_size)*dram_burst_delay \
                        + (weight_l2_size / dram_burst_size)*dram_continous_delay + weight_l2_overhead #TODO: exchange dram_burst_delay<->dram_continous_delay

    #data_l2_cycle = (data_l2_size*max(1, data_dram_bitwidth*(input_byte*8)/512) / data_dram_bitwidth) + (data_l2_size/data_l2_burst_size)*dram_burst_delay \
    data_l2_cycle = (data_l2_size*(data_dram_bitwidth*(input_byte*8)/512) / data_dram_bitwidth) + (data_l2_size/data_l2_burst_size)*dram_burst_delay \
                        + (data_l2_size / dram_burst_size)*dram_continous_delay + data_l2_overhead #TODO: exchange dram_burst_delay<->dram_continous_delay

    output_l2_cycle = ((output_l2_size*max(1, output_dram_bitwidth*(output_byte*8)/512) / output_dram_bitwidth) + (output_l2_size/output_l2_burst_size)*dram_burst_delay \
                        + (output_l2_size / dram_burst_size)*dram_continous_delay + output_l2_overhead)*2 #TODO: exchange dram_burst_delay<->dram_continous_delay
    '''
    dram_bw = 73
    weight_l2_cycle = weight_l2_size / dram_bw
    data_l2_cycle = data_l2_size / dram_bw
    output_l2_cycle =  output_l2_size / dram_bw
    '''

    dram_only_write_speedup = 1 - ((mapping_def.L2_TILENUM_K*mapping_def.L2_TILENUM_H*mapping_def.L2_TILENUM_W)/l2_loop_iteration)/2
    output_l2_cycle *= dram_only_write_speedup


    #if 1, their is no reuse
    #FIXME: for weight stationary
    L2_loop_iter = [1, 1, 1, 1, 1, 1, 1]
    for i in range(mapping_def.L2_ORDER_K+1, 6): L2_loop_iter[i] *= mapping_def.L2_TILENUM_K
    for i in range(mapping_def.L2_ORDER_C+1, 6): L2_loop_iter[i] *= mapping_def.L2_TILENUM_C
    for i in range(mapping_def.L2_ORDER_H+1, 6): L2_loop_iter[i] *= mapping_def.L2_TILENUM_H
    for i in range(mapping_def.L2_ORDER_W+1, 6): L2_loop_iter[i] *= mapping_def.L2_TILENUM_W
    for i in range(mapping_def.L2_ORDER_R+1, 6): L2_loop_iter[i] *= mapping_def.L2_TILENUM_R
    for i in range(mapping_def.L2_ORDER_S+1, 6): L2_loop_iter[i] *= mapping_def.L2_TILENUM_S

    data_reuse_count   = L2_loop_iter[min(mapping_def.L2_ORDER_C if mapping_def.L2_TILENUM_C is not 1 else 6,
                                          mapping_def.L2_ORDER_H if mapping_def.L2_TILENUM_H is not 1 else 6,
                                          mapping_def.L2_ORDER_W if mapping_def.L2_TILENUM_W is not 1 else 6)]
    weight_reuse_count = L2_loop_iter[min(mapping_def.L2_ORDER_K if mapping_def.L2_TILENUM_K is not 1 else 6,
                                          mapping_def.L2_ORDER_C if mapping_def.L2_TILENUM_C is not 1 else 6,
                                          mapping_def.L2_ORDER_R if mapping_def.L2_TILENUM_R is not 1 else 6,
                                          mapping_def.L2_ORDER_S if mapping_def.L2_TILENUM_S is not 1 else 6)]
    output_reuse_count = L2_loop_iter[min(mapping_def.L2_ORDER_K if mapping_def.L2_TILENUM_K is not 1 else 6,
                                          mapping_def.L2_ORDER_H if mapping_def.L2_TILENUM_H is not 1 else 6,
                                          mapping_def.L2_ORDER_W if mapping_def.L2_TILENUM_W is not 1 else 6)]

    block_size = data_reuse_count*weight_reuse_count*output_reuse_count

    

    #//TODO:calc correctly for last and first
    #//TODO: calc dram once unwrite
    

    L1_conv_L2_cycle= max(SIMD_cycle,weight_l1_cycle,data_l1_cycle,output_l1_cycle)
    
    #//first
    #block_first  = max((L1_conv_L2_cycle*block_size)
    #                        ,(output_l2_cycle*(block_size/output_reuse_count-1)) #//actuaclly we need to add more to prevent miscalculation
    #                        ,(data_l2_cycle  *block_size/data_reuse_count)
    #                        ,(weight_l2_cycle*block_size/weight_reuse_count))
                            
    block_middle= max((L1_conv_L2_cycle*block_size)
                            ,(output_l2_cycle*block_size/output_reuse_count)
                            ,(data_l2_cycle  *block_size/data_reuse_count)
                            ,(weight_l2_cycle*block_size/weight_reuse_count))
                            
    #block_last  = max((L1_conv_L2_cycle*block_size)
    #                        ,(output_l2_cycle*block_size/output_reuse_count)
    #                        ,(data_l2_cycle  *(block_size/data_reuse_count-1)) #//actuaclly we need to add more to prevent miscalculation
    #                        ,(weight_l2_cycle*(block_size/weight_reuse_count-1))) #//actuaclly we need to add more to prevent miscalculation

    block_first =max((L1_conv_L2_cycle*block_size)
							,(output_l2_cycle*(block_size/output_reuse_count-1)+max(data_l2_cycle,weight_l2_cycle,L1_conv_L2_cycle))
							,(data_l2_cycle  *block_size/data_reuse_count)
							,(weight_l2_cycle*block_size/weight_reuse_count))

    block_last  =max((L1_conv_L2_cycle*block_size)
				,(output_l2_cycle*block_size/output_reuse_count)
				,(data_l2_cycle  *(block_size/data_reuse_count-1)+max(L1_conv_L2_cycle,output_l2_cycle))
				,(weight_l2_cycle*(block_size/weight_reuse_count-1)+max(L1_conv_L2_cycle,output_l2_cycle)))


    total_cycle = block_middle*max((l2_loop_iteration/block_size-2),0)+block_first+block_last \
                        + (max(data_l1_cycle,weight_l1_cycle)+output_l1_cycle)/l1_loop_iteration \
                        +max(data_l2_cycle,weight_l2_cycle)+output_l2_cycle

    if verbose > 0:
        print()
        print("ID:", ID)
        if is_weight_stationary:
            print("Weight stationary")
        elif is_output_stationary:
            print("Output stationary")
        elif is_input_stationary:
            print("Input stationary")
        print("Analysis Insight:")
        l2_weight_bottleneck = (weight_l2_cycle*block_size/weight_reuse_count)*l2_loop_iteration/block_size
        l2_data_bottleneck = (data_l2_cycle*block_size/data_reuse_count)*l2_loop_iteration/block_size
        l2_output_bottleneck = (output_l2_cycle*block_size/output_reuse_count)*l2_loop_iteration/block_size
        l1_weight_bottleneck = weight_l1_cycle*block_size*l2_loop_iteration/block_size
        l1_data_bottleneck = data_l1_cycle*block_size*l2_loop_iteration/block_size
        l1_output_bottleneck = output_l1_cycle*block_size*l2_loop_iteration/block_size
        pe_bottleneck = SIMD_cycle*block_size*l2_loop_iteration/block_size
        bottleneck = max(l2_weight_bottleneck, l2_data_bottleneck, l2_output_bottleneck, l1_weight_bottleneck, l1_data_bottleneck, l1_output_bottleneck, pe_bottleneck)
        if verbose == 1:
            print("L2 Weight bottleneck: ", l2_weight_bottleneck)
            print("L2 Data bottleneck: ", l2_data_bottleneck)
            print("L2 Output bottleneck: ", l2_output_bottleneck)
            print("L1 Weight bottleneck: ", l1_weight_bottleneck)
            print("L1 Data bottleneck: ", l1_data_bottleneck)
            print("L1 Output bottleneck: ", l1_output_bottleneck)
            print("PE bottleneck: ", pe_bottleneck)
            print("Total Cycle: ", total_cycle)
        if bottleneck == l2_weight_bottleneck:
            bottleneck_type = "DRAM->L2 weight"
        elif bottleneck == l2_data_bottleneck:
            bottleneck_type = "DRAM->L2 data"
        elif bottleneck == l2_output_bottleneck:
            bottleneck_type = "DRAM->L2 output"
        elif bottleneck == l1_weight_bottleneck:
            bottleneck_type = "L2->L1 weight"
        elif bottleneck == l1_data_bottleneck:
            bottleneck_type = "L2->L1 data"
        elif bottleneck == l1_output_bottleneck:
            bottleneck_type = "L2->L1 output"
        elif bottleneck == pe_bottleneck:
            bottleneck_type = "PE"
        else:
            bottleneck_type = "?"
        print("  ==> Maybe, {} Layer is {} bottleneck".format(ID, bottleneck_type))
        if verbose == 1:
            print(l2_loop_iteration)
            print(data_reuse_count)
            print(weight_reuse_count)
            print(output_reuse_count)
            print(dram_only_write_speedup)
            print(weight_l2_cycle, data_l2_cycle, output_l2_cycle)
            print(weight_l1_cycle, data_l1_cycle, output_l1_cycle, SIMD_cycle)
            print(block_middle, block_first, block_last)

    return total_cycle #//TODO: Return time

if __name__=="__main__":

    for l in range(53):
        import sys
        #with open("./../../../outdir/res/00/hw_.yaml", "r") as f:
        #with open(sys.argv[1], "r") as f:
        with open("../SparseNAAS/outdir/res/{:02d}/hw_.yaml".format(l), "r") as f:
            data = [float(dt) for dt in f.readline().split(',')]
            hw_sample = HW_DEF(data[0], data[1], data[2], data[4], data[4])
            d = []
            for i in range(5):
                d += [int(dt) for dt in f.readline().split(',')]
            mapping_sample_def = MAPPING_DEF(d[0], d[1], d[2], d[3], d[4], d[5], 
                                            d[6], d[7], d[8], d[9], d[10], d[11], 
                                            d[12], d[13], d[14], d[15], d[16], d[17], 
                                            d[18], d[19], d[20], d[21], d[22], d[23], 
                                            d[24], d[25], d[26], d[27], d[28], d[29], 
                                       1.0)
        #print(calculateSparseAccel(hw_sample, mapping_sample_def, verbose=0, ID=l+1))
        calculateSparseAccel(hw_sample, mapping_sample_def, verbose=1, ID=l+1)
    print()

    hw_def_weight_sta = HW_DEF(32, 32, 1, 1, 1)
    hw_def_output_sta = HW_DEF(32, 1, 8, 1, 1)

    hw_def = hw_def_output_sta
    mapping_def = MAPPING_DEF(2, 1, 2, 2, 1, 1,
                               5, 4, 3, 2, 1, 0, #KCHWRS
                               8, 4, 1, 1, 1, 1,
                               5, 4, 3, 2, 1, 0,
                               32, 32, 14, 14, 1, 1,
                               0.5)
    print(calculateSparseAccel(hw_def, mapping_def, verbose=0))

    #weight stationary example
    weight_sta_data = [2,1,16,16,1,1,5,4,3,2,1,0,1,1,1,1,7,7,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,2,2,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,2,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,8,2,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,8,2,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,2,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,2,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,8,2,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,2,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,2,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,8,2,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,1,4,4,1,1,5,4,3,2,1,0,4,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        2,1,4,4,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,1,2,2,1,1,5,4,3,2,1,0,8,4,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        2,1,2,2,1,1,5,4,3,2,1,0,8,4,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        2,1,2,2,1,1,5,4,3,2,1,0,8,4,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        2,1,2,2,1,1,5,4,3,2,1,0,8,4,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,2,2,2,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        4,2,2,2,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        4,1,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        4,1,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        4,1,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        4,1,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        4,1,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        1,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,14,14,1,1,
        4,1,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        2,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        4,8,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,7,7,1,1,
        8,4,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,14,14,1,1,
        8,2,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,7,7,1,1,
        2,8,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,7,7,1,1,
        4,8,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,7,7,1,1,
        8,2,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,7,7,1,1,
        2,8,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,7,7,1,1,
        4,8,1,1,1,1,5,4,3,2,1,0,4,2,1,1,3,3,5,4,3,2,1,0,32,32,7,7,1,1,
        8,2,1,1,1,1,5,4,3,2,1,0,8,8,1,1,1,1,5,4,3,2,1,0,32,32,7,7,1,1]
    #output stationary example
    output_sta_data = [
        2,1,14,14,1,1,5,2,1,0,3,2,1,1,16,2,7,7,1,2,4,3,5,0,32,4,1,8,1,1,
        1,1,4,7,1,1,5,2,1,0,3,2,2,1,16,1,1,1,1,2,4,3,5,0,32,64,1,8,1,1,
        1,1,4,7,1,1,5,2,1,0,3,2,2,1,16,1,3,3,1,2,4,3,5,0,32,64,1,8,1,1,
        2,1,7,7,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,64,1,8,1,1,
        2,1,7,7,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,64,1,8,1,1,
        1,1,7,7,1,1,5,2,1,0,3,2,2,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        1,1,4,7,1,1,5,2,1,0,3,2,2,1,16,1,3,3,1,2,4,3,5,0,32,64,1,8,1,1,
        2,1,7,7,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,64,1,8,1,1,
        1,1,7,7,1,1,5,2,1,0,3,2,2,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        1,1,4,7,1,1,5,2,1,0,3,2,2,1,16,1,3,3,1,2,4,3,5,0,32,64,1,8,1,1,
        2,1,7,7,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,64,1,8,1,1,
        1,1,7,7,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,1,7,4,1,1,5,2,1,0,3,2,2,1,4,1,3,3,1,2,4,3,5,0,32,128,1,8,1,1,
        4,1,7,7,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        4,1,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,128,1,8,1,1,
        1,2,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,1,7,4,1,1,5,2,1,0,3,2,2,1,4,1,3,3,1,2,4,3,5,0,32,128,1,8,1,1,
        4,1,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,128,1,8,1,1,
        1,2,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,1,7,4,1,1,5,2,1,0,3,2,2,1,4,1,3,3,1,2,4,3,5,0,32,128,1,8,1,1,
        4,1,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,128,1,8,1,1,
        1,2,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,1,7,4,1,1,5,2,1,0,3,2,2,1,4,1,3,3,1,2,4,3,5,0,32,128,1,8,1,1,
        4,1,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,128,1,8,1,1,
        2,2,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,7,2,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        8,2,4,4,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,2,2,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,7,2,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,2,2,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,7,2,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,2,2,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,7,2,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,2,2,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,7,2,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,2,2,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        2,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,7,2,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        8,1,2,2,1,1,5,2,1,0,3,2,4,1,8,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        4,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        16,2,4,1,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        16,2,4,2,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        16,1,2,1,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        4,4,4,1,1,1,5,2,1,0,3,2,4,2,2,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        16,2,4,1,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        16,1,2,1,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        4,4,4,1,1,1,5,2,1,0,3,2,4,2,2,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,
        16,2,4,1,1,1,5,2,1,0,3,2,1,1,2,1,3,3,1,2,4,3,5,0,32,256,1,8,1,1,
        16,1,2,1,1,1,5,2,1,0,3,2,4,2,4,1,1,1,1,2,4,3,5,0,32,256,1,8,1,1,]

    hw_def = hw_def_weight_sta
    data = weight_sta_data
    #hw_def = hw_def_output_sta
    #data = output_sta_data
    density = 1.0

    for i in range(53):
        mapping_def = MAPPING_DEF(data[i*30+ 0], data[i*30+ 1], data[i*30+ 2], data[i*30+ 3], data[i*30+ 4], data[i*30+ 5],
                                  data[i*30+ 6], data[i*30+ 7], data[i*30+ 8], data[i*30+ 9], data[i*30+10], data[i*30+11],
                                  data[i*30+12], data[i*30+13], data[i*30+14], data[i*30+15], data[i*30+16], data[i*30+17],
                                  data[i*30+18], data[i*30+19], data[i*30+20], data[i*30+21], data[i*30+22], data[i*30+23],
                                  data[i*30+24], data[i*30+25], data[i*30+26], data[i*30+27], data[i*30+28], data[i*30+29], density)

        print(calculateSparseAccel(hw_def, mapping_def, verbose=0, ID=i+1))


