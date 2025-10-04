from srf_carboncapture.models.trees import QuercusRobur, AlnusGlutinosa, PopulusTremula, AcerPseudoplatanus

import numpy as np
import matplotlib.pyplot as plt

def convert_m2_to_ha(area_m2):
    return area_m2 / 10000.0

class Woodland:
    def __init__(self,
                 tree_percentages, 
                 wood_area=1,
                 tree_area=convert_m2_to_ha(1.5**2),
                 yearly_rotation=20):
        trees = []
        num_trees = int(wood_area / tree_area)
        for tree_class, percentage in tree_percentages.items():
            n_trees = int(num_trees * percentage)
            trees.extend([tree_class(tree_area=tree_area) for _ in range(n_trees)])
        self.trees = trees  # List of Tree instances
        print(len(self.trees), "trees in the woodland")
        self.coppice_rate = self.find_coppice_rate(yearly_rotation)

    def __call__(self):
        # A year of the wood's life
        captured_biomass = 0.
        for tree in self.trees:
            is_coppice = (np.random.rand() < self.coppice_rate)
            captured_biomass += tree(is_coppice=is_coppice)
        # print("Captured biomass this year (tonne):", captured_biomass)
        return captured_biomass

    def find_coppice_rate(self, yearly_rotation):
        # Example: 0.2 means 20% of trees are coppiced annually
        return 1. / yearly_rotation
    
if __name__ == "__main__":
    tree_percentages = {
        QuercusRobur: 0.25,
        AcerPseudoplatanus: 0.25, # Sycamore
        AlnusGlutinosa: 0.25, # Alder
        PopulusTremula: 0.25, # Aspen
    }
    wood = Woodland(tree_percentages)
    
    years = np.linspace(0, 150, 151)
    captured_biomass = [wood() for i in years]
    plt.plot(years, captured_biomass)
    plt.xlabel('Years')
    plt.ylabel('Captured Biomass (tonne)')
    plt.title('Yearly Captured Biomass in Woodland')
    plt.show()