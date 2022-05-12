from Utils_Benoit import *
import matplotlib.colors as colors

class MidpointNormalize(colors.Normalize):
    """
    For normalazing the color bar in heatmap (and find a better balance for showing)
    lowest values
    """
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))
