#define MAX(a, b) (((a)>(b))?(a):(b))
#define MAX3(a,b,c) ((MAX(a,b) < c) ? (c) :(MAX(a,b)))
#define MAX4(a,b,c,d) ((MAX3(a,b,c) < d) ? (d) :(MAX3(a,b,c)))
#define DEBUG_PRINT(X) printf("%d\n",X);

#Overhead define
#L1 Level
weight_l1_overhead   = 1
data_l1_overhead     = 5
SIMD_overhead        = 16 #//fixed
output_l1_overhead   = 5
#L2 Level
weight_l2_overhead   = 3
l1_loop_overhead     = 2
data_l2_overhead     = 88
output_l2_overhead   = 163
#DRAM Level
bias_read_overhead   = 3
bias_write_overhead  = 121
l2_loop_overhead     = 2
output_II            = 2
#burst read
dram_burst_delay     = 76 #//??????
#dram_burst_delay     = 64 #//??????
dram_continous_delay = 2
dram_burst_size      = 4096 #//TODO: Caculate correctly

class HW_DEF:
    def __init__(self, ARRAY_K, ARRAY_C, ARRAY_W):
        self.ARRAY_K = ARRAY_K #//if output stationary, 1
        self.ARRAY_C = ARRAY_C #//if input stationary,  1
        self.ARRAY_W = ARRAY_W #//if weight stationary, 1

class MAPPING_DEF:
    def __init__(self,
                 L2_TILENUM_K, L2_TILENUM_C, L2_TILENUM_H, L2_TILENUM_W, L2_TILENUM_R, L2_TILENUM_S,
                 L2_ORDER_K, L2_ORDER_C, L2_ORDER_H, L2_ORDER_W, L2_ORDER_R, L2_ORDER_S,
                 L1_TILENUM_K, L1_TILENUM_C, L1_TILENUM_H, L1_TILENUM_W, L1_TILENUM_R, L1_TILENUM_S,
                 L1_ORDER_K, L1_ORDER_C, L1_ORDER_H, L1_ORDER_W, L1_ORDER_R, L1_ORDER_S,
                 TILE_K, TILE_C, TILE_H, TILE_W, TILE_R, TILE_S):
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

def calculate_time(hw_def, mapping_def, verbose=False, ID=0):

    #FIXME if needed
    weight_bandwidth = hw_def.ARRAY_C
    data_bandwidth   = hw_def.ARRAY_C
    output_bandwidth = hw_def.ARRAY_K
    

    #iteration
    l2_loop_iteration = mapping_def.L2_TILENUM_K*mapping_def.L2_TILENUM_C*mapping_def.L2_TILENUM_R*mapping_def.L2_TILENUM_S*mapping_def.L2_TILENUM_W*mapping_def.L2_TILENUM_H;
    l1_loop_iteration = mapping_def.L1_TILENUM_K*mapping_def.L1_TILENUM_C*mapping_def.L1_TILENUM_R*mapping_def.L1_TILENUM_S*mapping_def.L1_TILENUM_W*mapping_def.L1_TILENUM_H;
    

    #SIMD
    SIMD_iteration     = mapping_def.W_L1*mapping_def.H_L1*mapping_def.C_L1*mapping_def.K_L1/(hw_def.ARRAY_K*hw_def.ARRAY_C*hw_def.ARRAY_W);
    SIMD_cycle         = SIMD_iteration     +SIMD_overhead;
    
    #//L2 TX
    weight_l1_iteration= mapping_def.K_L1*mapping_def.C_L1*mapping_def.R_L1*mapping_def.S_L1 / weight_bandwidth;
    data_l1_iteration  = mapping_def.W_L1*mapping_def.H_L1*mapping_def.C_L1                  / data_bandwidth;
    output_l1_iteration= mapping_def.W_L1*mapping_def.H_L1*mapping_def.K_L1                  / output_bandwidth;    
    weight_l1_cycle    = weight_l1_iteration+weight_l1_overhead
    data_l1_cycle      = data_l1_iteration  +data_l1_overhead
    output_l1_cycle    = output_l1_iteration+output_l1_overhead
    
    #//TODO:this is diffenrent between stationary
    weight_l2_burst_size= mapping_def.K_L2*mapping_def.C_L2*mapping_def.R_L2*mapping_def.S_L2
    data_l2_burst_size  = mapping_def.W_in_L2*data_bandwidth
    output_l2_burst_size= mapping_def.W_L2 *output_bandwidth    
    
    weight_l2_iteration = 1
    data_l2_iteration   = mapping_def.C_L2*mapping_def.H_in_L2*mapping_def.W_in_L2/data_l2_burst_size;
    output_l2_iteration = mapping_def.K_L2*mapping_def.H_L2*mapping_def.W_L2      /output_l2_burst_size;
    
    weight_l2_cycle=(weight_l2_burst_size/weight_bandwidth+ \
                        int(weight_l2_burst_size/dram_burst_size/weight_bandwidth)*dram_continous_delay+ \
                        dram_burst_delay)*weight_l2_iteration \
                        +weight_l2_overhead
    data_l2_cycle=    (data_l2_burst_size/data_bandwidth+ \
                        int(data_l2_burst_size/dram_burst_size/data_bandwidth)*dram_continous_delay+ \
                        dram_burst_delay)*data_l2_iteration \
                        +data_l2_overhead

    output_l2_cycle=((output_l2_burst_size*output_II/output_bandwidth+ \
                        int(output_l2_burst_size/dram_burst_size/output_bandwidth)*dram_continous_delay+ \
                        dram_burst_delay)*output_l2_iteration \
                        +output_l2_overhead)*2
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
    #weight_reuse_count = min(L2_loop_iter[mapping_def.L2_ORDER_K], L2_loop_iter[mapping_def.L2_ORDER_C], L2_loop_iter[mapping_def.L2_ORDER_R], L2_loop_iter[mapping_def.L2_ORDER_S])
    weight_reuse_count = L2_loop_iter[min(mapping_def.L2_ORDER_K if mapping_def.L2_TILENUM_K is not 1 else 6,
                                          mapping_def.L2_ORDER_C if mapping_def.L2_TILENUM_C is not 1 else 6,
                                          mapping_def.L2_ORDER_R if mapping_def.L2_TILENUM_R is not 1 else 6,
                                          mapping_def.L2_ORDER_S if mapping_def.L2_TILENUM_S is not 1 else 6)]

    #output_reuse_count = min(L2_loop_iter[mapping_def.L2_ORDER_K], L2_loop_iter[mapping_def.L2_ORDER_H], L2_loop_iter[mapping_def.L2_ORDER_W])
    output_reuse_count = L2_loop_iter[min(mapping_def.L2_ORDER_K if mapping_def.L2_TILENUM_K is not 1 else 6,
                                          mapping_def.L2_ORDER_H if mapping_def.L2_TILENUM_H is not 1 else 6,
                                          mapping_def.L2_ORDER_W if mapping_def.L2_TILENUM_W is not 1 else 6)]

    block_size = data_reuse_count*weight_reuse_count*output_reuse_count

    

    #//TODO:calc correctly for last and first
    #//TODO: calc dram once unwrite
    

    L1_conv_L2_cycle= max(SIMD_cycle,weight_l1_cycle,data_l1_cycle,output_l1_cycle)*l1_loop_iteration
    
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
                        +max(data_l1_cycle,weight_l1_cycle)+output_l1_cycle \
                        +max(data_l2_cycle,weight_l2_cycle)+output_l2_cycle

    if(verbose):
        print("ID:", ID)
        print("Analysis Insight:")
        print("L2 Weight bottleneck: ", (weight_l2_cycle*block_size/weight_reuse_count)*l2_loop_iteration/block_size)
        print("L2 Data bottleneck: ", (data_l2_cycle*block_size/data_reuse_count)*l2_loop_iteration/block_size)
        print("L2 Output bottleneck: ", (output_l2_cycle*block_size/output_reuse_count)*l2_loop_iteration/block_size)
        print("PE bottleneck: ", L1_conv_L2_cycle*block_size*l2_loop_iteration/block_size)
        print("Total Cycle: ", total_cycle)
        print(data_reuse_count)
        print(weight_reuse_count)
        print(output_reuse_count)
        print(dram_only_write_speedup)
        print(weight_l2_cycle, data_l2_cycle, output_l2_cycle)
        print(block_middle, block_first, block_last)


    return total_cycle #//TODO: Return time
if __name__=="__main__":
    hw_def = HW_DEF(32, 32, 1)
    mapping_def = MAPPING_DEF(2, 1, 2, 2, 1, 1,
                               5, 4, 3, 2, 1, 0, #KCHWRS
                               8, 4, 1, 1, 1, 1,
                               5, 4, 3, 2, 1, 0,
                               32, 32, 14, 14, 1, 1)
    print(calculate_time(hw_def, mapping_def))

    data = [2,1,16,16,1,1,5,4,3,2,1,0,1,1,1,1,7,7,5,4,3,2,1,0,32,32,14,14,1,1,
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

    for i in range(53):
        mapping_def = MAPPING_DEF(data[i*30+ 0], data[i*30+ 1], data[i*30+ 2], data[i*30+ 3], data[i*30+ 4], data[i*30+ 5],
                                  data[i*30+ 6], data[i*30+ 7], data[i*30+ 8], data[i*30+ 9], data[i*30+10], data[i*30+11],
                                  data[i*30+12], data[i*30+13], data[i*30+14], data[i*30+15], data[i*30+16], data[i*30+17],
                                  data[i*30+18], data[i*30+19], data[i*30+20], data[i*30+21], data[i*30+22], data[i*30+23],
                                  data[i*30+24], data[i*30+25], data[i*30+26], data[i*30+27], data[i*30+28], data[i*30+29])

        print(calculate_time(hw_def, mapping_def, verbose=False, ID=i+1))


