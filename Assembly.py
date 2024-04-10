class Assembly():
    """represents a fuel assembly including position in core and history of the fuel"""
    label = "**"
    moved = False
    fourColor = False
    quadColor = (  0, 204,   0)
    Burnup = [0,0,0,0]
    UO2WT = 3
    UO2_scaler = 51
    MOX = 0
    BurnablePoisons = 0
    SUSPECTED_FOR_LEAK = False

    def __init__(self, label, UO2WT=3.2, Burnup=[0,0,0,0], BurnablePoisons=10 ):
        self.label = label
        self.moved = False
        self.U02WT = UO2WT
        self.Burnup = Burnup
        # initially the color is uniform. (?)
        c1 = (Burnup[0], UO2WT *self.UO2_scaler, BurnablePoisons)
        c2 = (Burnup[1], UO2WT *self.UO2_scaler, BurnablePoisons)
        c3 = (Burnup[2], UO2WT *self.UO2_scaler, BurnablePoisons)
        c4 = (Burnup[3], UO2WT *self.UO2_scaler, BurnablePoisons)
        self.quadColor = [c1,c2,c3,c4]

    def isSame(self, a):
        """Compares two Assemblies:
         If the fuel should go back in the same bin. For example if it is loaded
         and removes wihtout being burned up."""
         #TODO: FIXME:  this function needs work and thought - what variables are
         # relevant?  Should fuel that has been burned once be lumped togeher?
         #  should 'moved' be a difference?? no?? -> # self.moved == a.moved and \
        if  self.label == a.label and \
                self.fourColor == a.fourColor and \
                self.quadColor == a.quadColor and \
                self.Burnup == a.Burnup and \
                self.UO2WT == a.UO2WT and \
                self.UO2_scaler == a.UO2_scaler and \
                self.MOX == a.MOX and \
                self.BurnablePoisons == a.BurnablePoisons and \
                self.SUSPECTED_FOR_LEAK == a.SUSPECTED_FOR_LEAK:
            return True
        else:
            i =0
            for item1, item2 in zip([self.label, \
                    self.moved, \
                    self.fourColor, \
                    self.quadColor, \
                    self.Burnup, \
                    self.UO2WT, \
                    self.UO2_scaler,\
                    self.MOX,\
                    self.BurnablePoisons,\
                    self.SUSPECTED_FOR_LEAK, ], [a.label, \
                    a.moved, \
                    a.fourColor, \
                    a.quadColor, \
                    a.Burnup, \
                    a.UO2WT, \
                    a.UO2_scaler, \
                    a.MOX,\
                    a.BurnablePoisons,\
                    a.SUSPECTED_FOR_LEAK]):
                if item1 != item2:
                    i+=1
                    print ("diff: "+str(item1)+ "  " +str(item2) + " "+str(i))
            return False


def main():
    print("This is the assembly class file, it is should not be run")

if __name__ == '__main__':
    main()
