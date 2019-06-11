from sys import argv

Rtype = ['and', 'or', 'add', 'sll', 'srl', 'nor', 'sub', 
        'mult', 'mul', 'slt', 'mflo', 'rlw', 'rsw', 'not']

Vectorized_mem_acc = ['vrlw', 'vrsw']

VRtype =['vadd', 'vmul', 'vnot', 'vand', 'vor']

Itype = ['sw', 'lw', 'beq', 'addi', 'bne']

funct_to_numb = {'and' : 0b100100, 'or' : 0b100101, 'add' : 0b100000, 'sll': 0b000000, 'srl': 0b000001, 'sub' : 0b100010,
         'slt' : 0b101010, 'nor' : 0b011011, 'mult' : 0b011001, 'mflo' : 0b010010, 'mul' : 0b011001, 'not' : 0b000010}

vec_reg_to_num = {'xmm': 29, 'ymm': 30, 'rmm': 31}

class parser:

    def __init__(self, path):
        self.path = path

    def parse_instruction(self,words):
        op = words[0]

        # print(op)
        if op == 'nop':
            return'{:032b}'.format(0)
        # print(op)
        opcode = 0
        if op in Rtype and op != 'rlw' and op != 'rsw':
            opcode = 0
        elif op == 'lw':
            opcode = 0b100011
        elif op == 'sw':
            opcode = 0b101011
        elif op == 'beq':
            opcode = 0b000100
        elif op == 'addi':
            opcode = 0b001000
        elif op == 'rlw' :
            opcode = 0b000010
        elif op == 'rsw'  :
            opcode = 0b000011
        elif op == 'bne':
            opcode = 0b001001
        elif op == 'vrlw':
            opcode = 0b000101
        elif op == 'vrsw':
            opcode = 0b000110
        elif op in VRtype:
            opcode = 0b000111
        elif op == 'get':
            opcode = 0b001010
        else:
            raise Exception

        opcode = '{:06b}'.format(opcode)
        rd = ''
        rs = ''
        rt = ''
        ra = ''
        shamt = ''
        funct = ''
        imm = ''

        instruction = ''

        if op in Rtype:
            rd = ''.join(s for s in words[1] if s.isdigit())
            rd = "{:05b}".format(int(rd))
        
        
            rs = ''.join(s for s in words[2] if s.isdigit())
            rs = "{:05b}".format(int(rs))

            if op == 'sll' or op == 'srl':
                shamt = ''.join(s for s in words[3] if s.isdigit())
                shamt = "{:05b}".format(int(shamt))
            else:
                shamt = "{:05b}".format(0)
            
            if op != 'mult' and op != 'not':
                rt = ''.join(s for s in words[3] if s.isdigit())
                rt = "{:05b}".format(int(rt))
            else:
                rt = "{:05b}".format(0)


            if op in funct_to_numb:
                funct = funct_to_numb[op]

            if op == 'mul':
                funct = funct_to_numb['mult']
            if op == 'rlw' or op == 'rsw':
                funct = funct_to_numb['add']
            
            funct = "{:06b}".format(int(funct))

            if op == 'mflo':
                rs = shamt
                rt = shamt  
        
            instruction = opcode + rs + rt + rd + shamt + funct


        if op in Itype:
            rd = ''.join(s for s in words[1] if s.isdigit())
            rd = "{:05b}".format(int(rd))
        
        
            rs = ''.join(s for s in words[2] if s.isdigit())
            rs = "{:05b}".format(int(rs))

            bin_word = bin(int(words[3]))
            imm = '{:016b}'.format(int(bin_word,2) & 0xffff)
            # print(imm + 'imm')

            instruction = opcode + rs + rd + imm

        if op in Vectorized_mem_acc:
            rd = vec_reg_to_num[words[1]]
            rd = '{:05b}'.format(rd)
            
            rs = ''.join(s for s in words[2] if s.isdigit())
            rs = "{:05b}".format(int(rs))

            if op == 'vsll' or op == 'vsrl':
                shamt = ''.join(s for s in words[3] if s.isdigit())
                shamt = "{:05b}".format(int(shamt))
            else:
                shamt = "{:05b}".format(0)
            
            if op != 'vmult':
                rt = ''.join(s for s in words[3] if s.isdigit())
                rt = "{:05b}".format(int(rt))
            else:
                rt = shamt


            if op[1:] in funct_to_numb:
                funct = funct_to_numb[op]
            

            if op == 'vmul':
                funct = funct_to_numb['mult']
            if op == 'vrlw' or op == 'vrsw':
                funct = funct_to_numb['add']
            
            funct = "{:06b}".format(int(funct))

            if op == 'mflo':
                rs = shamt
                rt = shamt  
        
            instruction = opcode + rs + rt + rd + shamt + funct

        if op in VRtype:
            rd = vec_reg_to_num[words[1]]
            rd = '{:05b}'.format(rd)
            
            rs = vec_reg_to_num[words[2]]
            rs = "{:05b}".format(int(rs))

            if op == 'vnot':
                rt = 31
            else:
                rt = vec_reg_to_num[words[3]]
            
            rt = "{:05b}".format(int(rt))

            shamt = 0
            shamt = "{:05b}".format(shamt)

            funct = funct_to_numb[op[1:]]
            funct = "{:06b}".format(funct)

            instruction = opcode + rs + rt + rd + shamt + funct


        if op == 'get':
            rd = ''.join(s for s in words[1] if s.isdigit())
            rd = '{:05b}'.format(int(rd))

            rs = rs = vec_reg_to_num[words[2]]
            rs = "{:05b}".format(int(rs))

            rt = ''.join(s for s in words[3] if s.isdigit())
            rt = "{:05b}".format(int(rt))

            shamt = 0
            shamt = "{:05b}".format(shamt)

            funct = 2
            funct = "{:06b}".format(funct)

            instruction = opcode + rs + rt + rd + shamt + funct
            

        return instruction

    def get_labels(self, lines):
        i = 0
        labels = {}
            
        for line in lines:
            line = line.strip().split('#')[0]
            
            if line == '':
                continue
            
            words = line.split()
            
            line_addr = str(i)

            if len(words) == 1 and words[0] != 'nop':
                labels[words[0].strip(':')] = line_addr
                #print(labels)
                continue

            i += 4  

        return labels

    def parse(self):
        file = open(self.path, 'r')
        lines = file.readlines()

        labels = self.get_labels(lines)
        i = 0 

        string = ''
        
        for line in lines:
            
            line = line.strip().split('#')[0]
            
            if line == '':
                continue
            
            line = line.strip().replace(',', '')
            words = line.split()

            if len(words) == 1 and words[0] != 'nop':
                continue
    
            if len(words) > 3 and words[3] in labels:
                words[3] = labels[words[3]]
                # print(words[3])

            line_addr = '{:032b}'.format(i)
            words[0] = words[0].lower()

            instruction = self.parse_instruction(words)


            assembly = '_'.join(words)

            
            string += line_addr + ' ' + instruction + ' ' + assembly + '\n'
            
            i+=4
        file.close()
        # print (string)
        return string

