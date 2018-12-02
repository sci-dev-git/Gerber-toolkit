
GERBER_APERT_C = 0
GERBER_APERT_R = 1
GERBER_APERT_O = 2
GERBER_APERT_P = 3

class GerberAperture:
    def __init__(self, d_code = 0, atype = GERBER_APERT_C, modifier = 0.0, modifierX = 0.0):
        self.d_code = d_code
        self.type = atype
        self.modifier = modifier
        self.modifierX = modifierX
        