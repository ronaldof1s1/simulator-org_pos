from sys import argv

Rtype = ['and', 'or', 'add', 'sll', 'slr', 'nor', 'sub', 
        'mult', 'mul', 'slt', 'mflo', 'rlw', 'rsw']

Itype = ['sw', 'lw', 'beq', 'addi', 'bne']

funct_to_numb = {'and' : 0b100100, 'or' : 0b100101, 'add' : 0b100000, 'sll': 0b000000, 'slr': 0b000001, 'sub' : 0b100010,
         'slt' : 0b101010, 'nor' : 0b011011, 'mult' : 0b011001, 'mflo' : 0b010010}

class parser:

    def __init__(self, path):
        self.path = path

    def parse_instruction(self,words):
        op = words[0]


        if op == 'nop':
            return'{:032b}'.format(0)

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

        opcode = '{:06b}'.format(opcode)
        
        rd = ''.join(s for s in words[1] if s.isdigit())
        rd = "{:05b}".format(int(rd))
        rs = ''
        rt = ''
        ra = ''
        shamt = ''
        funct = ''
        imm = ''

        instruction = ''

        if op in Rtype:
            rs = ''.join(s for s in words[2] if s.isdigit())
            rs = "{:05b}".format(int(rs))

            if op == 'sll' or op == 'srl':
                shamt = ''.join(s for s in words[3] if s.isdigit())
                shamt = "{:05b}".format(int(shamt))
            else:
                shamt = "{:05b}".format(0)
            
            if op != 'mult':
                rt = ''.join(s for s in words[3] if s.isdigit())
                rt = "{:05b}".format(int(rt))
            else:
                rt = shamt


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
            rs = ''.join(s for s in words[2] if s.isdigit())
            rs = "{:05b}".format(int(rs))

            bin_word = bin(int(words[3]))
            imm = '{:016b}'.format(int(bin_word,2) & 0xffff, 'b')
            # print(imm + 'imm')

            instruction = opcode + rs + rd + imm


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
            
            words = line.strip().split()

            if len(words) == 1 and words[0] != 'nop':
                continue
    
            if len(words) > 3 and words[3] in labels:
                words[3] = labels[words[3]]
                # print(words[3])

            line_addr = '{:032b}'.format(i)


            instruction = self.parse_instruction(words)


            assembly = '_'.join(words)

            
            string += line_addr + ' ' + instruction + ' ' + assembly + '\n'
            
            i+=4
        file.close()
        print (string)
        return string

