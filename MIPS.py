######### GEORGE SAMAN
######### 5 Stage MIPS Simulator
######### NOTE: It deals with memory stalls, and data hazards
######### 12/08/2017

from sys import argv
from parser import parser
import memory_init

powers = {'mult' : 2717287.74, 'alu' : 671381.11, 'regbank' : 1465626.89, 'cacheR' : 12000000.00, 'cacheW' : 13000000.0, 'dram' : 2000000.0}

leakage_power = {'mult' : 131465.84, 'alu' : 16992.06, 'regbank' : 44461.77, 'cacheR' : 12000000.00, 'cacheW' : 13000000.0, 'dram' : 2000000.0}

dynamic_power = {'mult' : 2460760.74, 'alu' : 509204.37, 'regbank' : 2385461.93, 'cacheR' : 12000000.00, 'cacheW' : 13000000.0, 'dram' : 2000000.0}

regs = [[0,0,"$zero","constant zero"],
        [1,0,"$at","assembler temporary"],
        [2,0,"$v0","value for function results"],
        [3,0,"$v1","value for function results"],
        [4,0,"$a0","arguments"],
        [5,0,"$a1","arguments"],
        [6,0,"$a2","arguments"],
        [7,0,"$a3","arguments"],
        [8,0,"$t0","temporaries"],
        [9,0,"$t1","temporaries"],
        [10,0,"$t2","temporaries"],
        [11,0,"$t3","temporaries"],
        [12,0,"$t4","temporaries"],
        [13,0,"$t5","temporaries"],
        [14,0,"$t6","temporaries"],
        [15,0,"$t7","temporaries"],
        [16,0,"$s0","saved temporaries"],
        [17,0,"$s1","saved temporaries"],
        [18,0,"$s2","saved temporaries"],
        [19,0,"$s3","saved temporaries"],
        [20,0,"$s4","saved temporaries"],
        [21,0,"$s5","saved temporaries"],
        [22,0,"$s6","saved temporaries"],
        [23,0,"$s7","saved temporaries"],
        [24,0,"$t8","temporaries"],
        [25,0,"$t9","temporaries"],
        [26,0,"$k0","reserved for OS kernel"],
        [27,0,"$k1","reserved for OS kernel"],
        [28,0,"$gp","global pointer"],
        [29,[0,0,0,0,0,0,0,0], "xmm","vector 1"],
        [30,[0,0,0,0,0,0,0,0], "ymm", "vector 2"],
        [31,[0,0,0,0,0,0,0,0], "rmm"," vector 3"],
        ]

# vec_regs = [[29,[0,0,0,0,0,0,0,0], "xmm"],
#             [30,[0,0,0,0,0,0,0,0], "ymm"],
#             [31,[0,0,0,0,0,0,0,0], "rmm"],
#             ]

LO_REG = 0
HI_REG = 0

IF_ID = [0, 0] # Current instruction | Next instruction
ID_EX = [[0 , 0 , 0, 0],[0 , 0 , 0, 0]]  #current READ REG1 | READ REG2 | SIGN EXTEND | READ REG3...NEXT
EX_MEM= [[0, 0],[0, 0]] # ALU result | alu_sr2 , CUrrent and next
MEM_WB =[[0, 0],[0, 0]] # MEMORY_READ_DATA | ALU_result

RegDst =[0, 0, 0, 0] #WB | MEM | EX | DECODE stage
MemtoReg = [0, 0, 0, 0] #WB | MEM | EX | DECODE stage
RegWrite = [0, 0, 0, 0] #WB | MEM | EX | DECODE stage
MemRead =  [0, 0, 0] # MEM | EX | DECODE stage
MemWrite = [0, 0, 0, 0] # WB| MEM | EX | DECODE stage
ALUOp = [0, 0]   # EX | DECODE stage
ALUSrc = [0, 0]  # EX | DECODE stage
VectorizeSource = [0, 0]  # EX | DECODE stage
VectorizeDest = [0, 0, 0, 0]  # WB | MEM | EX | DECODE stage
stallDetected = 0

my_rs = [0, 0, 0, 0] #WB | MEM | EX | DECODE stage
my_rt = [0, 0, 0, 0] #WB | MEM | EX | DECODE stage
my_ra = [0, 0] # EX | DECODE stage
my_rd = [0, 0, 0, 0] #WB | MEM | EX | DECODE stage
my_funct=[0, 0] # EX | DECODE stage
my_shamt=[0, 0] # EX | DECODE stage
my_op   =[0,0] # EX | DECODE stage
Branch  =[0,0] # EX | DECODE stage
branch_target = 0 # EX 

inst_assembly = [0, 0, 0, 0, 0]

def display_regs():
    x = [x*2 for x in range(16)]
    for i in x:
        print(regs[i][2] + "=", "{}".format(regs[i][1])+'    '+regs[i+1][2] + "=", "{}".format(regs[i+1][1]))
    print("LO_REG = " + str(LO_REG) + '    ' + "HI_REG = " + str(HI_REG))
    return
def display_mem():
    print("data Memory")
    for i in range(len(data_mem)):
        print("location {}".format(i) + " = " + str(data_mem[i]))    
    

# ---- CONTROL FIELDS ----
# From Page 266 - Figure 4.18 
# RegDst -- Destination Register selection based upon R or I Format
# ALUSrc -- ALU operand from either register file or sign extended immediate
# MemtoReg -- Loads - selects register write data from memory
# RegWrite -- Write Enable for Register File
# MemRead -- Read Enable for Data Memory
# MemWrite -- Write Enable for Data Memory
# Branch -- Branch instruction used to qualify next PC address
# ALUOp -- ALU operation predecode
# VectorizeSource -- using vector instructions
#| RegDst | ALUSrc | MemtoReg | RegWrite | MemRead | MemWrite | Branch | ALUOp | VectorizeSource | VectorizeDest
control = { 0b000000 : [1,0,0,1,0,0,0,2,0,0],     #R Format
            0b100011 : [0,1,1,1,1,0,0,0,0,0],     #lw
            0b101011 : [0,1,0,0,0,1,0,0,0,0],     #sw
            0b000100 : [0,0,0,0,0,0,1,1,0,0],     #beq
            # 0b001101 : [0,1,0,1,0,0,0,3,0,0],     #ori
            0b001000 : [0,1,0,1,0,0,0,3,0,0],     #addi
            # 0b000001 : [0,0,0,0,0,0,1,1,0,0],     #bgez
            0b000010 : [1,0,1,1,1,0,0,2,0,0],     #rlw
            0b000011 : [1,0,0,0,0,1,0,2,0,0],     #rsw
            # 0b000101 : [1,0,0,1,0,0,0,2,1],     #mac
            # 0b000110 : [1,0,1,1,1,0,0,2,1],     #mal
            # 0b000111 : [1,0,0,0,0,1,0,2,1],     #mas
            0b001001 : [0,0,0,0,0,0,1,1,0,0],     #bne
            0b000101 : [1,0,1,1,1,0,0,2,0,1],     #vrlw
            0b000110 : [1,0,0,0,0,1,0,2,0,1],     #vrsw
            0b000111 : [1,0,0,1,0,0,0,2,1,1],     #VR Format
            0b001010 : [1,0,0,1,0,0,0,2,0,0],     #GET
            }

dynamic_power_usage = { 0b000000 : dynamic_power['alu'] + dynamic_power['regbank']*3,     #R Format
            0b100011 : dynamic_power['alu'] + dynamic_power['regbank']*2 + dynamic_power['cacheR'],     #lw
            0b101011 : dynamic_power['alu'] + dynamic_power['regbank']*2 + dynamic_power['cacheW'],     #sw
            0b000100 : dynamic_power['alu'] + dynamic_power['regbank']*2,     #beq
            # 0b001101 : [0,1,0,1,0,0,0,3,0,0],     #ori
            0b001000 : dynamic_power['alu'] + dynamic_power['regbank']*2,     #addi
            # 0b000001 : [0,0,0,0,0,0,1,1,0,0],     #bgez
            0b000010 : dynamic_power['alu'] + dynamic_power['regbank']*3 + dynamic_power['cacheR'],     #rlw
            0b000011 : dynamic_power['alu'] + dynamic_power['regbank']*3 + dynamic_power['cacheW'],     #rsw
            # 0b000101 : [1,0,0,1,0,0,0,2,1],     #mac
            # 0b000110 : [1,0,1,1,1,0,0,2,1],     #mal
            # 0b000111 : [1,0,0,0,0,1,0,2,1],     #mas
            0b001001 : dynamic_power['alu'] + dynamic_power['regbank']*2,     #bne
            0b000101 : dynamic_power['alu'] + dynamic_power['regbank']*10 + dynamic_power['cacheR'],     #vrlw
            0b000110 : dynamic_power['alu'] + dynamic_power['regbank']*10 + dynamic_power['cacheW'],     #vrsw
            0b000111 : dynamic_power['alu']*8 + dynamic_power['regbank']*8 + dynamic_power['cacheR'],     #VR Format
            0b001010 : dynamic_power['regbank']*10,     #GET
            }
            



ALU = { 0b0000 : lambda src1, src2 : ["and", src1 & src2, "bitwise and"],
        0b0001 : lambda src1, src2 : ["or",  src1 | src2, "bitwise or"],
        0b0010 : lambda src1, src2 : ["add", src1 + src2, "add signed"],
        0b0011 : lambda src1, src2 : ["sll", src1 << src2, "shift logical left"],
        0b0100 : lambda src1, src2 : ["srl", (src1 >> src2), "shift logical right"],
        0b0110 : lambda src1, src2 : ["sub", src1 - src2, "sub signed"],
        0b0111 : lambda src1, src2 : ["slt", 1 if src1 < src2 else 0, "set on less than"],
        0b1100 : lambda src1, src2 : ["nor", ~(src1 | src2), "bitwise nor"],
        0b1101 : lambda src1, src2 : ["multu", src1 * src2, "multiply"],
        # 0b1101 : lambda src1, src2 : ["multu", src1, "multiply"],
        0b1110 : lambda src1, src2 : ["mflo",LO_REG,"move from LO_REG"],
        0b1111 : lambda src1, src2 : ["not",0 if src1 > 0 else 1,"bitwise not"],
        }

decode_funct = { 0b000000 : ["sll",   0b0011],
                 0b000001 : ["srl",   0b0100],
                 0b100000 : ["add",   0b0010],
                 0b100010 : ["sub",   0b0110],
                 0b100100 : ["and",   0b0000],
                 0b100101 : ["or",    0b0001],
                 0b101010 : ["slt",   0b0111],
                 0b011001 : ["multu", 0b1101],
                 0b010010 : ["mflo",  0b1110],
                 0b011011 : ["nor",   0b1100],
                 0b000010 : ['not',   0b1111]}

decode_Ifunct ={ 0b001101 : ["ori", 0b0001],
                 0b001000 : ["addi", 0b0010]}

BranchAddress = { 0b000100 : lambda Zero, greaterThanZero: (branch_target if (Zero) else PC_plus_4), # beq
                  0b000001 : lambda Zero, greaterThanZero: (branch_target if ((greaterThanZero==1)or(Zero==1)) else PC_plus_4), #bgez
                  0b001001 : lambda Zero, greaterThanZero: (PC_plus_4 if (Zero) else branch_target), #bne
                  } 

def ALU_control(ALUOp, funct,opcode):
    if (ALUOp == 0): #lw, sw => add
        return(0b0010)
    
    if (ALUOp == 1):  #beq/bgez/bne  => sub
        return(0b0110)
    if (ALUOp == 2): # R or M type
        return (decode_funct[funct][1])
    if ALUOp ==3:
        return (decode_Ifunct[opcode][1])

# Initialize Memory

inst_mem = []

data_mem = memory_init.mxm(64)# matA= [1,2],[3,4] matX=[4,5], matB=[0,0]
# print(data_mem)

# file = open("../outputs/out.out", 'w+')
def read_instr(path):
    p = parser(path)
    program = p.parse()
    lines = program.splitlines()
    codelines = [x for x in lines if x[0] != "#"]
    for line in codelines:
        words = line.split()
        mem = (int(words[0],2),int(words[1],2),words[2])
        inst_mem.append(mem)
    return

read_instr(argv[1])   #Read Instruction Memory

inst_mem_len = len(inst_mem)


# BRANCH PREDICTOR
# 0: strongly not taken
# 1: weakly not taken
# 2: weakly taken
# 4: strongly taken
branch_predictor = {}

def update_branch_predictor(branch_pc, taken):
    if branch_pc in branch_predictor:
        last_taken = branch_predictor[branch_pc]
        new_taken = last_taken
        
        if taken and last_taken < 3:
            new_taken += 1
        elif not taken and last_taken > 0:
            new_taken -= 1

        branch_predictor[branch_pc] =  new_taken

    else:
        branch_predictor[branch_pc] = 2 if taken else 1

def flush_pipe():
    IF_ID = [0, 0] # Current instruction | Next instruction
    ID_EX = [[0 , 0 , 0],[0 , 0 , 0]]  #current READ REG1 | READ REG2 | SIGN EXTEND...NEXT

        
    RegDst[3] = 0
    MemtoReg[3] = 0
    RegWrite[3] = 0
    MemRead[2] = 0 
    MemWrite[3] = 0
    ALUOp[1] = 0 
    ALUSrc[1] = 0
    VectorizeSource[1] = 0
    VectorizeDest[2] = 0
    

    my_rs[3] = 0
    my_rt[3] = 0
    my_rd[3] = 0
    my_ra[1] = 0
    my_funct[1] = 0
    my_shamt[1] = 0
    my_op[1]   = 0
    Branch[1]  = 0

    inst_assembly[4] = 0
    inst_assembly[3] = 0 

#**** Statistics *****#
clock = 0 # a variable holding clock counts
inst_executed = 0
mem_accesses = 0 # a variable holding mem access counts
cache_latency = 2
multiplier_latency = 3
multiplications = 0
power_array = {}
power_sum = 0
leak_sum = 0
for leak in leakage_power.values():
    leak_sum += leak;


#***** Start of Machine *****
PC = 0
Zero  = 0
greaterThanZero = 0

while PC in range(inst_mem_len * 4):
    

################################## FETCH STAGE ######################################
    #fetch instruction
    addr = inst_mem[PC>>2][0]
    inst_assembly[4] = inst_mem[PC>>2][2]
    instruction = inst_mem[PC>>2][1]
    inst_executed += 1
   
    #latch result of this stage into its pipeline reg
    IF_ID[1] = instruction
    
    clock = clock +1
    # print(clock)
    # print(inst_assembly)
    #increment PC if there is no STALL
    if stallDetected == 0:
        PC_plus_4 = PC + 4
        PC = PC_plus_4
        releaseStall = 0
    else:
        releaseStall = 1
        
    # print('----------------------------------------------------')
    # print('/F\ Fetched = ' + str(inst_assembly[4])+    '  ------Clock cycle = '+ str(clock))
    # print('IF/ID ----- To decode = '+ "%#010x"%(IF_ID[0])+'  fetched = '+ "%#010x".format(IF_ID[1]))
   
        
################################### DECODE STAGE ######################################
    if (clock >= 2):
        ################### WRITE FIRST THEN READ#########################
        if (clock >= 5):
            #register write back


            register_write_data = MEM_WB[0][0] if MemtoReg[0] else MEM_WB[0][1]
            write_register = my_rd[0] if RegDst[0] else my_rt[0]
            if VectorizeDest[0]:
                # print("wb vec")
                # print(write_register)
                # print(vec_regs[write_register])
                # print(register_write_data)
                # print(inst_assembly[0])
                if(RegWrite[0]):
                    # print(my_rd, my_rt, my_rs)
                    # print(register_write_data)
                    # print(write_register)
                    # write_register -= 29
                    regs[write_register][1] = register_write_data
            else:
                # print("wb norm")
                # print(write_register)
                # print(regs[write_register])
                # print(register_write_data)
                # print(inst_assembly[0])
                
                if (RegWrite[0] and (write_register!= 0)): # do not write to reg zero. FOR MULTU
                    regs[write_register][1] = register_write_data
            
            # print("/W\ WriteBack = "+str(inst_assembly[0]))
            
        #decode instruction
        my_op[1] = IF_ID[0] >> 26
        my_rs[3] = (IF_ID[0] >> 21) & 0x1F
        my_rt[3] = (IF_ID[0] >> 16) & 0x1F # store in next3 since it is used in WB
        my_rd[3] = (IF_ID[0] >> 11) & 0x1F
        my_ra[1] = (IF_ID[0] >> 6) & 0x1F
        my_shamt[1] = (IF_ID[0] >> 6) & 0x1F
        my_funct[1] = IF_ID[0] & 0x3F
        my_imm = IF_ID[0] & 0xFFFF
       
        #control signals
        control_word = control[my_op[1]]
        ALUSrc[1] = control_word[1] 
        RegDst[3] = control_word[0] 
        MemtoReg[3] = control_word[2] 
        RegWrite[3] = control_word[3] 
        MemRead[2] = control_word[4]  
        MemWrite[3] = control_word[5] 
        Branch[1] = control_word[6]
        ALUOp[1] = control_word[7] 
        VectorizeSource[1] = control_word[8]
        VectorizeDest[3] = control_word[9]

        #register file sources
        read_register1 = my_rs[3]
        read_register2 = my_rt[3]
        read_register3 = my_ra[1]
        read_data1 = regs[read_register1][1] 
        read_data2 = regs[read_register2][1]
        read_data3 = regs[read_register3][1]
    
        #power usage:
        dynamic_energy = dynamic_power_usage[my_op[1]]
        if (my_funct[1] == 0b011001):
            mult_power = dynamic_power['mult']
            if(my_op[1] == 0b000000):
                dynamic_energy += mult_power
            else:
                dynamic_energy += 8*mult_power
            
        inst_power = dynamic_energy + leak_sum
        power_sum += inst_power
        if inst_assembly[3] not in power_array:
            power_array[inst_assembly[3]] = inst_power

        #sign extension of immediate data
        sign_bit = (my_imm >> 15) & 0x1
        sign_ext = (my_imm-(0x10000)) if (sign_bit == 1) else my_imm
        
        
        #Latch results of that stage into its pipeline reg
        ID_EX[1] = [read_data1, read_data2, sign_ext, read_data3]
        # print('/D\ Decoded = ' + str(inst_assembly[3]))
        # print("ID/EX -----  for current execute= [{}, {}, {}]".format((ID_EX[0][0]),(ID_EX[0][1]),(ID_EX[0][2]))," result of current decode =[{},{},{}]".format((ID_EX[1][0]),(ID_EX[1][1]),(ID_EX[1][2])))
        # print('vecdest' + str(VectorizeDest))
        # print("RD = [{}, {}, {}, {}]".format((my_rd[0]) ,(my_rd[1]), (my_rd[2]) ,(my_rd[3])))
        # print("RS =  [{}, {}, {}, {}]".format((my_rs[0]) ,(my_rs[1]), (my_rs[2]) ,(my_rs[3])))
        # print("RT =  [{}, {}, {}, {}]".format((my_rt[0]) ,(my_rt[1]), (my_rt[2]) ,(my_rt[3])))
        # print("RA =  [{}, {}]".format((my_ra[0]) ,(my_ra[1])))
        
        # print("MemRead=      ", MemRead)
        # print("MemWrite = ", MemWrite)
        # print("MemToReg = " , MemtoReg)
        # print("RegWrite = ", RegWrite)
        # print("regDst =   ", RegDst)

     
#################################### EXECUTE STAGE ######################################
    if (clock >= 3):
        # alu and mult sources when there is no hazard or stall
        # mult_src1 = ID_EX[0][0]
        # mult_src2 = ID_EX[0][3] if VectorizeSource[0] else 0x0001 #if mult then ra else 1
        # mult_result = mult_src1 * mult_src2

        # alu_src1 = mult_result
        alu_src1 = ID_EX[0][0]

        alu_src2 = ID_EX[0][2] if ALUSrc[0] else ID_EX[0][1]  # if ALUsrc_current = 1 then sign Extend is alu_src2 else read_data2
        readData2= ID_EX[0][1]
        # print(VectorizeSource)
        # if VectorizeSource[0]:
        #     alu_src1 = vec_read_data1
        #     alu_src2 = vec_read_data2    
        ############## H     A     Z     A     R     D DETECTION BETWEEN WB AND EX STAGE ############################
        # hazard is present if RD of WB stage (RD[0]) == Ex stage's Rs[2] or RT[2]                                  #
        # hazard is present if RD of MEM stage (RD[1]) == Ex stage's RS[2] or RT[2]                                 #
        hazardDetected_rs =0                                                                                        #
        hazardDetected_rt =0                                                                                        #
        if (clock >5):                                                                                              #
            if ((RegWrite[0]) or (RegWrite[1])): # check if there is a write back to register
                if ((MemWrite[0]== 0) and (MemWrite[1]== 0) and (MemWrite[2]== 0)):                                 #
                    # check if intruction in WB or MEM writes back to register and WB,MEM,EX is not a sw inst       #
                                                                                                                    #
                    WB_hazard_RD_check = my_rd[0] if RegDst[0] else my_rt[0]                                        #
                    if (WB_hazard_RD_check == my_rs[2]): # with RS
                        if((ALUOp[0] == 3)): # if I instruction
                            # print("--------------------------RS forwaded from WB stage. RS = {}".format(MEM_WB[0][1]))          #
                            alu_src1_rs = MEM_WB[0][1]  # load into alu_src1 the value of ALU result                        #
                            hazardDetected_rs = 1
                        else:
                            # print("--------------------------RS forwaded from WB stage. RS = {}".format(MEM_WB[0][0]))       #
                            alu_src1_rs = MEM_WB[0][0]  # load into alu_src1 the value of the loaded data from memory   #
                            hazardDetected_rs = 1
                            
                    if ( WB_hazard_RD_check == my_rt[2]): # with RT
                        if((ALUOp[0] == 3)): # if I instruction
                            alu_src2 = alu_src2
                        else:
                            # print("--------------------------RT forwaded from WB stage. RT = {}".format(MEM_WB[0][0]))       #
                            alu_src2_rt = MEM_WB[0][0]                                                                  #
                            hazardDetected_rt = 1
                            
                    MEM_hazard_RD_check = my_rd[1] if RegDst[1] else my_rt[1]                                           #
                    if (MEM_hazard_RD_check == my_rs[2]): # with RS
                            # print("--------------------------RS forwaded from MEM stage. RS = {}".format(EX_MEM[0][0]))          #
                            alu_src1_rs = EX_MEM[0][0]  # load into alu_src1 the value of ALU result                        #
                            hazardDetected_rs = 1
                                              
                    if ( (MEM_hazard_RD_check == my_rt[2]) and (ALUSrc[0] == 0)): # with RT AND source is a reg not signext#
                            # print("--------------------------RT forwaded from MEM stage. RT = {}".format(EX_MEM[0][0]))          #
                            # print(my_rt)
                            alu_src2_rt = EX_MEM[0][0]                                                                      #
                            hazardDetected_rt = 1                                                                           #
                                                                                    #           
        #############################################################################################################
                
        ################## S     T     A     L     L DETECTION ######################################################
            # stall happens when execute sources needs a valid data which is not yet loaded from memory             #
                                                                                                                    #
            MEM_STALL_RD_check = my_rd[1] if RegDst[1] else my_rt[1]                                                #
                                                                                                                    #
            if releaseStall == 1: # if last clock cycle was a stall then release it, otherwise order one            #
                stallDetected = 0                                                                                   #
                alu_src1 = regs[my_rs[2]][1]# on the next cycle of the stall, re fetch registers.                   # 
                alu_src2 = regs[my_rt[2]][1]# in case a WB hazard happened with the stall                           #
                                                                                                                    #                      
            if ((MemRead[0] ==1)and ((MEM_STALL_RD_check == my_rs[2]) or (MEM_STALL_RD_check == my_rt[2]))):        #
                        # print("--------------------------STALL CAUSED FROM EX DUE TO MEM LOAD")                     #
                        # turn everything into zero for the next cycle to operate as a NOP                          #
                        stallDetected = 1 # the releaseStall signal is used in the fetch stage                      #
                        EX_MEM[1] = [0, 0]  # result of current execution =0                                        #
                        PC = PC -4 # ADJUST PC TO RE FETCH LAST INSTRUCTION
                        inst_executed -= 1                                         #
                        # print("/E\ Executed = NOP $zero,$zero,$zero")                                               #
                        # print("EX/MEM -----  for current MEM= ",EX_MEM[0], " result of current execute = ", EX_MEM[1]) #                                                                                                  
        #############################################################################################################
                    
        if (stallDetected == 0):
            if hazardDetected_rs == 1: # fetch the forwaded data
                alu_src1 = alu_src1_rs
            if hazardDetected_rt == 1:
                alu_src2 = alu_src2_rt

            if my_op[0] == 0b000001: # if bgez then alusrc2 = zero
                alu_src2 = 0
                
            # print("AluSrc = " ,ALUSrc)
            # print("ALUOp = " , ALUOp)
            # print("VectorizeSource = ", VectorizeSource)
            # print("funct = " , my_funct)
            # print("shamt = " , my_shamt)
            # print("ALU SOURCES =", alu_src1, alu_src2)
            # print("Mult SOURCES =", mult_src1, mult_src2)
            
            

            shift =((ALUOp[0]==2) and ((my_funct[0]== 0b000000) or (my_funct[0] == 0b000001))) # check if there is a sll or srl inst
            if shift: # if sll or srl then alu_src2 = shamt
                # alu_src1 = alu_src2 
                alu_src2 = my_shamt[0] 
                # print("SOURCES UPDATED___ALU SOURCES =", alu_src1, alu_src2)

            alu_operation = ALU_control(ALUOp[0], my_funct[0], my_op[0]) # ALUOp is the current instruction

            alu_result = None
            # print(alu_src1,alu_src2)

            if VectorizeSource[0]:
                # print(VectorizeSource)
                # print('ex vec')
                # print(inst_assembly[2])
                # print(alu_src1, alu_src2)
                alu_entries = []
                for i in range(len(alu_src1)):
                    # print(inst_assembly[2])
                    result = ALU[alu_operation](alu_src1[i], alu_src2[i])
                    alu_entries.append(result[1])
                
                alu_result = alu_entries

            else:
                # print('ex norm')
                # print(inst_assembly[2])
                # print(alu_src1, alu_src2)
                # display_mem()
                # display_regs()
                if my_op[0] == 0b001010:
                    alu_result = alu_src1[alu_src2]
                else:
                    alu_entry = ALU[alu_operation](alu_src1,alu_src2)
                    # multiplication_to_LO = ((ALUOp[0]==2) and (my_funct[0]==0b011001)) # check if there is a multu inst
                    # alu_result = 0 if multiplication_to_LO else alu_entry[1]
                    alu_result = alu_entry[1]
                    # if multiplication_to_LO:
                    #     LO_REG = alu_entry[1] &  0xffffffff
                    #     HI_REG = (alu_entry[1] >> 32) & 0xffffffff
            
            #Branch Target
            branch_target = (ID_EX[0][2])
            # print(inst_assembly[2], alu_result)
            pc_mux1 = 0
            if Branch[0]:
                # print(alu_result)
                # print(alu_src1, alu_src2)
                # print(inst_assembly[2])
                Zero = 1 if (alu_result == 0) else 0
                greaterThanZero = 1 if(alu_result >0) else 0 ;
                # ---- Next PC Calculation ----
                #pc_mux1
                pc_mux1 = BranchAddress[my_op[0]](Zero, greaterThanZero)
                if pc_mux1 != PC_plus_4: # i.e branch Taken
                    # print("Branch Taken")
                    update_branch_predictor(PC, True)
                else:
                    # print("Branch Not Taken")   
                    update_branch_predictor(PC, False)

                #Jump = 0
                #pc_mux2 = 0 if (Jump) else pc_mux1
                PC = pc_mux1  #Next Instruction
            else:
                PC = PC_plus_4

            #Latch results of that stage into its pipeline reg
            EX_MEM[1] = [alu_result, readData2]
            # print("/E\ Executed = "+ str(inst_assembly[2]))
            # print(regs[2][1], regs[3][1], regs[5][1])
            # print(alu_result)
            # print(alu_src1, alu_src2)
            # print("EX/MEM -----  for current MEM= ",EX_MEM[0], " result of current execute = ", EX_MEM[1])
            # print("stall Detected= " + str(stallDetected))
            # print("Zero = " + str(Zero) +  " greaterThanZero = " + str(greaterThanZero)+ "  Next_PC = " + str(PC) +"  Branch = "+str(Branch[0]))
            # print("PC_MUX1= " +str(pc_mux1)+ " PC+4 = "+str(PC_plus_4)+ "  Branch_Target=", branch_target)
            
################################## MEM STAGE ######################################
    if (clock >= 4):
        memory_read_data = 0
        if MemWrite[1]: # current Control
            # print(inst_assembly)
            mem_accesses += 1
            if VectorizeDest[1]:
                # print(my_rd)
                data_to_w = regs[my_rd[1]][1]
                # print(data_to_w)
                i = 0
                for data in data_to_w:
                    index = EX_MEM[0][0]>>2 + i
                    data_mem[index] = data
            else:
                data_to_w = 0
                # print(my_op)
                if RegDst[1]: #if rsw
                    data_to_w = regs[my_rd[1]][1]
                else:
                    data_to_w = EX_MEM[0][1] 
                # print(data_to_w)
                data_mem[EX_MEM[0][0]>>2] = data_to_w


        if MemRead[0]:
            # print(inst_assembly, VectorizeDest)
            mem_accesses += 1
            if VectorizeDest[1]:
                memory_read_data = []
                
                for pos in range(8):
                    index = (EX_MEM[0][0] >> 2) + pos
                    memory_read_data.append(data_mem[index]) 
                # print (inst_assembly)
                # print(MemWrite,MemRead,memory_read_data)
            else:
                memory_read_data = data_mem[EX_MEM[0][0]>>2] 

            
        #Latch results of that stage into its pipeline reg
        MEM_WB[1] = [memory_read_data, EX_MEM[0][0]]  # alu result
        # print("/M\ Memory = " + str(inst_assembly[1]))
        # print("MEM/WB -----  for current WB= ",MEM_WB[0], " result of current MEM load = ", MEM_WB[1])
     
        
################################## Write Back STAGE ######################################

    # if (clock >= 5):
    #     print("/W\ WriteBack = "+str(inst_assembly[0]))
        # print(VectorizeDest)
        # display_regs()
        # display_mem()
        
################################ UPDATE PIPELINE REGISTERS ##############################
    #update pipseline registers
    
          
    my_rd[0] = my_rd[1]
    my_rd[1] = my_rd[2]
    my_rt[0] = my_rt[1]
    my_rt[1] = my_rt[2]
    my_rs[0] = my_rs[1]
    my_rs[1] = my_rs[2]
       
    EX_MEM[0] = EX_MEM[1]
    MEM_WB[0] = MEM_WB[1]

    #update Memory control lists
    MemWrite[0] = MemWrite[1]
    MemWrite[1] = MemWrite[2]
    MemRead[0] = MemRead[1]

  #update WB control lists
    MemtoReg[0] = MemtoReg[1]
    MemtoReg[1] = MemtoReg[2]
    RegWrite[0] = RegWrite[1]
    RegWrite[1] = RegWrite[2]
    RegDst[0] = RegDst[1]
    RegDst[1] = RegDst[2]
    VectorizeDest[0] = VectorizeDest[1]
    VectorizeDest[1] = VectorizeDest[2]

    inst_assembly[0] = inst_assembly[1]
    inst_assembly[1] = inst_assembly[2]
  
    if stallDetected == 0:
        # if there is a stall, stall these controls and registers
        IF_ID[0] = IF_ID[1]
        ID_EX[0] = ID_EX[1]
        my_rd[2] = my_rd[3]
        my_rt[2] = my_rt[3]
        my_rs[2] = my_rs[3]
        my_ra[0] = my_ra[1]
        
        ALUSrc[0] = ALUSrc[1] # update next instruction to current instruction for next clock cycle
        ALUOp[0]  = ALUOp[1]
        MemWrite[2] = MemWrite[3]
        MemRead[1] = MemRead[2]
        RegWrite[2] = RegWrite[3]
        RegDst[2] = RegDst[3]
        MemtoReg[2] = MemtoReg[3]
        VectorizeSource[0] = VectorizeSource[1]
        VectorizeDest[2] = VectorizeDest[3]
        
        my_funct[0] = my_funct[1]
        my_shamt[0] = my_shamt[1]
        my_op[0] = my_op[1]
        Branch[0] = Branch[1]
        
        
        inst_assembly[2] = inst_assembly[3]
        inst_assembly[3] = inst_assembly[4]
    else:
        # Turn all signals and registers to zero to form a NOP
        my_rs[1] = 0
        my_rt[1] = 0
        my_rd[1] = 0
        RegDst[1]  = 0
        MemtoReg[1]= 0
        RegWrite[1]= 0
        MemRead[0] = 0
        MemWrite[1]= 0
        # VectorizeSource[1] = 0
        VectorizeDest[1] = 0
        inst_assembly[1] = "NOP $zero,$zer0,%zero"

# -- End of Main Loop
frequency = 2*10**9
cycle_time = 1/frequency
cache_miss_ratio = 0.05
dram_latency = 33
miss_penalty = dram_latency + 1
mem_time = (cache_latency + cache_miss_ratio * miss_penalty)
real_clock_count = clock + mem_accesses * mem_time
seconds = real_clock_count * cycle_time
watts = power_sum/(10**9)
most_powered_instruction = max(power_array.values())
print("""##########################
REAL CLOCK COUNT: """, real_clock_count)
print('TOTAL INSTRUCTIONS: ', inst_executed)
print('TOTAL MEMORY ACCESSES', mem_accesses)
print("""EXPECTED CPI: """, clock/inst_executed)
print("""REAL CPI: """, real_clock_count/inst_executed)
print("TIME: ", seconds)
print("############################\n\n")
print("############################")
print("POWER COMSUMED = " + str(watts) + ' W')
print("MOST POWERED INSTRUCTION: ", most_powered_instruction)
print("ENERGY: " + str(watts * seconds) + ' J')
print("EDP: ", watts * seconds ** 2)
print("############################\n\n")

# display_mem()
# display_regs()