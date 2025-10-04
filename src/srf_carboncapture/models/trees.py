import numpy as np
import matplotlib.pyplot as plt

import numpy as np
from scipy.optimize import curve_fit

def fit_log_function(x, y):
    """
    Fit y = a * log(b*x + c) + d to provided data.
    
    Parameters
    ----------
    x : array-like
        Independent variable values (≥4 points recommended).
    y : array-like
        Dependent variable values.
    
    Returns
    -------
    params : dict
        Fitted parameters {'a': a, 'b': b, 'c': c, 'd': d}
    fit_fn : callable
        Function that evaluates the fitted curve at arbitrary x.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    def model(x, a, b, c, d):
        return a * np.log(b*x + c) + d
    
    # initial guesses (heuristics)
    a0 = (max(y) - min(y))
    b0 = 1 / (max(x) - min(x))
    c0 = 1
    d0 = min(y)
    
    popt, _ = curve_fit(model, x, y, p0=[a0, b0, c0, d0], maxfev=10000)
    a, b, c, d = popt
    
    def fit_fn(x_new):
        return model(np.asarray(x_new), a, b, c, d)
    
    return {'a': a, 'b': b, 'c': c, 'd': d}, fit_fn


def plot_carbon_capture(years, cc):
    plt.plot(years, cc)
    plt.xlabel('Years')
    plt.ylabel('Total Carbon Capture (kg / hectare)')
    plt.title('Carbon Capture Over Time')
    plt.show()

def biochar_conversion(volume_m3):
    # volume converts to biochar mass
    biochar_factor = 1/3  # tonne per m^3
    biochar_mass = volume_m3 * biochar_factor
    return biochar_mass

def yield_class_conversion(yield_class):
    # m^3 per hectare per year
    return yield_class * 2


class Tree:
    mai_coordinates = None  # To be defined in subclasses
    mai_parameters = None  # To be defined in subclasses

    def __init__(self, tree_area):
        # todo: change tree area to trees per hectare (planting_density)
        if self.mai_parameters is None:
            self.calc_mai_parameters()
        self.year_since_coppice = 0
        self.tree_area = tree_area  # in hectares
    
    def __call__(self, is_coppice=False):
        # A year of the tree's life
        if is_coppice:
            biomass = self.total_biomass(self.year_since_coppice)
            self.year_since_coppice = 0
            return biomass
        else:
            self.year_since_coppice += 1
            return 0.
        

    def calc_mai_parameters(self):
        assert self.mai_coordinates is not None, "Either mai_coordinates or mai_parameters must be provided"
        # Fit parameters if not predefined
        self.mai_parameters = fit_log_function(
            [x for x, y in self.mai_coordinates],
            [y for x, y in self.mai_coordinates]
        )[0]
        print("Fitted MAI parameters:", self.mai_parameters)

    def mean_annual_increment(self, time_years):
        return self.mai_parameters['a'] * np.log(self.mai_parameters['b'] * time_years + self.mai_parameters['c']) + self.mai_parameters['d']
    

    def plot_mai(self, time_years):
        mai = self.mean_annual_increment(time_years)
        plt.plot(time_years, mai)
        plt.xlabel('Years')
        plt.ylabel('Mean Annual Increment (m^3/ha/yr)')
        plt.title('MAI Over Time')
        plt.show()


    def total_biomass(self, time_years, is_plot=False):
        mai = self.mean_annual_increment(time_years)
        # mai is in m^3 per hectare per year
        # Convert to tonne of carbon captured
        cc_per_ha_per_yr = biochar_conversion(mai)  # tonne per hectare per year
        # Total carbon capture over the years per hectare
        cc_per_ha = cc_per_ha_per_yr * time_years  # tonne 
        if is_plot:
            plot_carbon_capture(time_years, cc_per_ha)
        cc = cc_per_ha * self.tree_area  # tonne for this tree
        return cc
       

    
class QuercusRobur(Tree):
    # Oak
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (10, 1.0),
        (20, 2.5),
        (40, 4.0),
        (60, 5.0),
        (80, 5.2),
        (100, 5.0),
        (120, 4.5)
    ]
    mai_parameters = {
        'a': 1.78,
        'b': 0.0376,
        'c': 0.204,
        'd': 2.66
    }

class AlnusGlutinosa(Tree):
    # Alder
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (5, 3.0),
        (10, 8.0),
        (20, 11.0),
        (30, 12.0),
        (40, 11.5),
        (50, 10.),
    ]
    mai_parameters = {
        'a': 3.39,
        'b': 0.0802,
        'c': 0.104,
        'd': 7.43
    }

class PopulusTremula(Tree):
    # Aspen
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (5, 3.0),
        (10, 8.0),
        (15, 11.0),
        (20, 12.0),
        (25, 12.5),
        (30, 12.),
    ]
    mai_parameters = {
        'a': 6.69,
        'b': 0.118,
        'c': 0.512,
        'd': 4.09
    }

class AcerPseudoplatanus(Tree):
    # Sycamore
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (10, 3.0),
        (20, 7.0),
        (30, 10.0),
        (40, 12.0),
        (50, 12.5),
        (60, 12.),
        (70, 11.),
        (80, 10.),
    ]
    mai_parameters = {
        'a': 4.09,
        'b': 0.0457,
        'c': 0.165,
        'd': 7.06
    }

class PinusSylvestris(Tree):
    # Scots Pine
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (10, 2.0),
        (20, 5.0),
        (30, 8.0),
        (40, 10.0),
        (50, 10.5),
        (60, 10.2),
        (70, 9.8),
    ]
    mai_parameters = {
        'a': 5.96,
        'b': 0.0461,
        'c': 0.528,
        'd': 3.37
    }

class FraxinusExcelsior(Tree):
    # Ash
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (10, 3.0),
        (20, 7.0),
        (30, 10.5),
        (40, 12.0),
        (50, 11.8),
        (60, 10.5),
        (70, 9.8),
    ]
    mai_parameters = {
        'a': 4.22,
        'b': 0.0677,
        'c': 0.271,
        'd': 5.21
    }

class BetulaPendula(Tree):
    # Birch
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (5, 4.0),
        (10, 8.0),
        (30, 9.),
        (40, 7.0),
        (50, 5.),
    ]
    mai_parameters = {
        'a': 0.622,
        'b': 0.088,
        'c': 4.31,
        'd': 6.25
    }

class FagusSylvatica(Tree):
    # Beech
    mai_coordinates = [
        # years, height
        # | Age (years) | MAI (m³/ha/yr) |
        (0, 0),
        (10, 1.0),
        (20, 3.0),
        (40, 6.),
        (60, 8.0),
        (80, 9.),
        (100, 9.),
        (120, 8.5),
    ]
    mai_parameters = {
        'a': 4.57,
        'b': 0.0318,
        'c': 0.456,
        'd': 3.11
    }





if __name__ == "__main__":
    tree = FagusSylvatica(tree_area=0.1)
    time = np.arange(0, 150, 1)
    tree.plot_mai(time)
    tree.carbon_capture(time)
    # years = np.arange(0, 100, 1)
    # tree.carbon_capture(years)