import consts

import gerberAperture

TOKEN_SPACES = (' ', '\t', '\n')

GERBER_INITIAL = 0
GERBER_STMT_END = 1
GERBER_ADDR_X = 2
GERBER_ADDR_Y = 3
GERBER_ADDR_D = 4
GERBER_ADDR_I = 5
GERBER_ADDR_J = 6
GERBER_FS_N = 7
GERBER_FS_G = 8
GERBER_FS_D = 9
GERBER_FS_M = 10
GERBER_FS_X = 11
GERBER_FS_Y = 12
GERBER_AD_D = 13
GERBER_AD_T = 14
GERBER_AD_MODIFIER = 15
GERBER_AD_MODIFIER_X = 16

PLOT_INITIAL = 0
PLOT_OUTLINE = 1

MODE_mm = 0
MODE_in = 1

class GerberParser:
    def __init__(self, plot_outline, plot_aperture):
        '''
            @brief Set up gerber parser.
            @param plot_outline     Fill Outline callback. plot_outline(addr_x, addr_y)
            @param plot_aperture    Fill aperture callback. plot_aperture(atype, modifier, modifier_x, addr_x, addr_y)
        '''
        self.state = GERBER_INITIAL
        self.plotstate = PLOT_INITIAL
        self.stmt = str()
        self.proc = self.procNULL
        self.addr_x = 0.0
        self.addr_y = 0.0
        self.addr_d = 0
        self.addr_i = 0.0
        self.addr_j = 0.0
        self.offset = 0
        self.end = 0
        self.fs_omit_leading_zeros = True
        self.fs_abs_coordinate = True
        self.fs_Nn = 2
        self.fs_Gn = 2
        self.fs_Dn = 2
        self.fs_Mn = 2
        self.fs_Xn_int = 2
        self.fs_Xn_pot = 3
        self.fs_Yn_int = 2
        self.fs_Yn_pot = 3
        self.mo = MODE_mm
        self.lp_dark = True
        self.plot_outline = plot_outline
        self.plot_aperture = plot_aperture
        self.outline_vertex = []
        self.d_apertures = []
        self.aperture = gerberAperture.GerberAperture()
        pass

    def parse(self, stream):
        ''' @brief Parse a gerber file
            @param stream I/O stream object
            @return status code
        '''
        stmts = stream.readlines()
        
        self.state = GERBER_INITIAL
        self.plotstate = PLOT_INITIAL
        self.outline_vertex = []
        self.d_apertures = {}
        
        for stmt in stmts:
            op_end = -1
            for i, ch in enumerate(stmt):
                if ch in TOKEN_SPACES or ch == '*':
                    op_end = i; break
            if op_end == -1: return consts.E_FAILED
    
            block_end = stmt.find('*', op_end)
            if block_end == -1: return consts.E_FAILED
            
            self.stmt = stmt
            
            if(stmt[0] == 'G'): # G-code Function
                self.gcode(stmt[:op_end], stmt, op_end, block_end)
            elif(stmt[0] == 'D'): # D-code Function
                self.dcode(stmt[:op_end], op_end, block_end)
            elif(stmt[0] == '%'): # Parameter
                self.param(stmt)
            elif(stmt[0] == 'X' or stmt[0] == 'Y' or stmt[0] == 'D'): # Address X first
                self.addr(stmt)
    
    def dcode(self, op, op_end, data_block_end):
        d_code = int(op[1:])
        aperture = self.d_apertures[d_code]
        self.plot_aperture(aperture.type, aperture.modifier, aperture.modifierX, self.addr_x, self.addr_y)
    
    def gcode(self, op, stmt, op_end, data_block_end):
        if op == 'G36':         # Outline On
            self.plotstate = PLOT_OUTLINE
            self.outline_vertex = []
            
        elif op == 'G37':       # Outline Off
            if self.plotstate == PLOT_OUTLINE:
                self.plot_outline(self.outline_vertex)
                self.outline_vertex = []
            self.plotstate = PLOT_INITIAL
            
        elif op == 'G04':       # Ignore
            if consts.PRINT_G04:
                print(stmt[:data_block_end])

        if consts.DEBUG and op != 'G04':
            print('GCODE', op)
        
        
    def param(self, stmt):
        op = stmt[1:3]
        offset = 3
        rc = 0
        if op == 'FS':
            rc = self.__resetState()
            
            for i, ch in enumerate(stmt[offset:], offset):
                if ch == 'L':
                    self.fs_omit_leading_zeros = True
                    self.offset = i
                elif ch == 'T':
                    self.fs_omit_leading_zeros = False
                    self.offset = i
                elif ch == 'A':
                    self.fs_abs_coordinate = True
                    self.offset = i
                elif ch == 'I':
                    self.fs_abs_coordinate = False
                    self.offset = i
                elif ch == 'N':
                    self.__transState(self.procFS_N, i, GERBER_FS_N)
                elif ch == 'G':
                    self.__transState(self.procFS_G, i, GERBER_FS_G)
                elif ch == 'D':
                    self.__transState(self.procFS_D, i, GERBER_FS_D)
                elif ch == 'M':
                    self.__transState(self.procFS_M, i, GERBER_FS_M)
                elif ch == 'X':
                    self.__transState(self.procFS_X, i, GERBER_FS_X)
                elif ch == 'Y':
                    self.__transState(self.procFS_Y, i, GERBER_FS_Y)
                if ch == '*':
                    self.__transState(self.procFS_comp, i, GERBER_STMT_END)
                    
            rc = self.__transState(self.procNULL, i, GERBER_INITIAL)
            
        elif op == 'MO':
            if stmt[offset:offset+3] == 'MM':
                self.mo = MODE_mm
            elif stmt[offset:offset+3] == 'IM':
                self.mo = MODE_in
            else:
                rc = consts.E_INVALID_MODE
            
        elif op == 'LP':
            if stmt[offset] == 'D':
                self.lp_dark = True
            elif stmt[offset] == 'C':
                self.lp_dark = False
            else:
                rc = consts.E_INVALID_MODE
                
        elif op == 'AD':
            if stmt[offset] == 'D':
                rc = self.__resetState()
                
                self.__transState(self.procAD_D, offset, GERBER_AD_D)
                
                for i, ch in enumerate(stmt[offset:], offset):
                    if ch == 'C':
                        self.__transState(self.procAD_C, i, GERBER_AD_T)
                    elif ch == 'R':
                        self.__transState(self.procAD_R, i, GERBER_AD_T)
                    elif ch == 'O':
                        self.__transState(self.procAD_O, i, GERBER_AD_T)
                    elif ch == 'P':
                        self.__transState(self.procAD_P, i, GERBER_AD_T)
                    elif ch == ',':
                        self.__transState(self.procAD_modifier, i, GERBER_AD_MODIFIER)
                    elif ch == 'X':
                        self.__transState(self.procAD_modifierX, i, GERBER_AD_MODIFIER_X)
                    if ch == '*':
                        self.__transState(self.procAD_comp, i, GERBER_STMT_END)
                
                rc = self.__transState(self.procNULL, i, GERBER_INITIAL)
                
        if rc: return rc
            
    def addr(self, stmt):
        data_block_end = stmt.find('*')
        if data_block_end == -1:
            return consts.E_FAILED
        
        self.__resetState()
        for i, ch in enumerate(stmt):
            if ch == '*':
                self.__transState(self.procADDR_comp, i, GERBER_STMT_END)
            elif ch == 'X':
                self.__transState(self.procADDR_X, i, GERBER_ADDR_X)
            elif ch == 'Y':
                self.__transState(self.procADDR_Y, i, GERBER_ADDR_Y)
            elif ch == 'D':
                self.__transState(self.procADDR_D, i, GERBER_ADDR_D)
                
        self.__transState(self.procADDR_comp, i, GERBER_INITIAL)
        
        return consts.E_SUCCEEDED
    
    def procNULL(self):
        pass
    def procADDR_comp(self):
        if consts.DEBUG > 1:
            print('X=', self.addr_x, 'Y=', self.addr_y, 'D=', self.addr_d)
        if self.plotstate == PLOT_OUTLINE and self.addr_d == 1:
            self.outline_vertex.append([self.addr_x, self.addr_y])
    def procADDR_X(self):
        self.addr_x = self.__conv_real(self.stmt[self.offset+1:self.end])
    def procADDR_Y(self):
        self.addr_y = self.__conv_real(self.stmt[self.offset+1:self.end])
    def procADDR_D(self):
        self.addr_d = int(self.stmt[self.offset+1:self.end])
    def procFS_N(self):
        self.fs_Nn = int(self.stmt[self.offset+1:self.end])
    def procFS_G(self):
        self.fs_Gn = int(self.stmt[self.offset+1:self.end])
    def procFS_D(self):
        self.fs_Dn = int(self.stmt[self.offset+1:self.end])
    def procFS_M(self):
        self.fs_Mn = int(self.stmt[self.offset+1:self.end])
    def procFS_X(self):
        n = int(self.stmt[self.offset+1:self.end])
        self.fs_Xn_int = n // 10
        self.fs_Xn_pot = n % 10
    def procFS_Y(self):
        n = int(self.stmt[self.offset+1:self.end])
        self.fs_Yn_int = n // 10
        self.fs_Yn_pot = n % 10
    def procFS_comp(self):
        if self.fs_abs_coordinate == False or self.fs_omit_leading_zeros == False:
            return consts.E_UNSUPPORTED
        if consts.DEBUG:
            print('FS: X=%d.%d Y=%d.%d' % (self.fs_Xn_int, self.fs_Xn_pot, self.fs_Yn_int, self.fs_Yn_pot))
        return 0
    def procAD_D(self):
        self.aperture.d_code = int(self.stmt[self.offset+1:self.end])
    def procAD_C(self):
        self.aperture.atype = gerberAperture.GERBER_APERT_C
    def procAD_R(self):
        self.aperture.atype = gerberAperture.GERBER_APERT_R
    def procAD_O(self):
        self.aperture.atype = gerberAperture.GERBER_APERT_O
    def procAD_P(self):
        self.aperture.atype = gerberAperture.GERBER_APERT_P
    def procAD_modifier(self):
        self.aperture.modifier = float(self.stmt[self.offset+1:self.end])
    def procAD_modifierX(self):
        self.aperture.modifierX = float(self.stmt[self.offset+1:self.end])
    def procAD_comp(self):
        self.d_apertures[self.aperture.d_code] = gerberAperture.GerberAperture(self.aperture.d_code, self.aperture.atype, self.aperture.modifier, self.aperture.modifierX)
        
    def __conv_real(self, numstr):
        int_left = len(numstr) - self.fs_Xn_pot
        int_left = min(self.fs_Xn_int, int_left)
        numint = numstr[:int_left]
        numdec = numstr[int_left:int_left + self.fs_Xn_pot]
        return float(numint + '.' + numdec)
    
    def __resetState(self):
        self.proc = self.procNULL
        self.offset = 0
        self.end = 0
    
    def __transState(self, proc, end, state):
        rc = 0
        if self.state != state:
            self.end = end
            rc = self.proc()
        self.proc = proc
        self.state = state
        self.offset = end
        return rc
        
#       
# testcase
#
def __testcase_plot(vexts):
    for point in vexts:
        #print('PLOT:', point[0], point[1])
        pass
        
def __testcase_plotAperture(atype, modifier, modifier_x):
    print('==========', atype, modifier, modifier_x)
    
if __name__ == '__main__':
    parser = GerberParser(__testcase_plot, __testcase_plotAperture)
    
    fp = open('./tests/pico86.gbr', 'r')
    parser.parse(fp)
    fp.close()
    