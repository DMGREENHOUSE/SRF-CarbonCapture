from srf_carboncapture.models.trees import QuercusRobur, AlnusGlutinosa, PopulusTremula, AcerPseudoplatanus
from srf_carboncapture.models.woodland import Woodland
from srf_carboncapture.models.cost_conversion import BiocharProcesssing
import numpy as np
import matplotlib.pyplot as plt


def srf_net_income(wood_area=1.,
                tree_percentages = {
                    QuercusRobur: 0.25,
                    AcerPseudoplatanus: 0.25, # Sycamore
                    AlnusGlutinosa: 0.25, # Alder
                    PopulusTremula: 0.25, # Aspen   
                },
                tree_area=0.000225,  # in hectares (1.5m x 1.5m)
                yearly_rotation=20,
                carbon_credit_per_co2_tonne=30.,
                pyroloysis_processing_cost_per_biochar_tonne=50.,
                carbon_resale_per_biochar_tonne=800.,
                land_per_biochar_tonne=0.,
                land_value_per_ha=0.,):
    
    # Define the time
    years = np.linspace(0, 150, 151)

    # create the forest
    wood = Woodland(tree_percentages=tree_percentages,
                    tree_area=tree_area,
                    wood_area=wood_area,
                    yearly_rotation=yearly_rotation)
    
    # Find captured biomass
    captured_biomass = [wood() for i in years]

    # convert to gbp
    cost_converter = BiocharProcesssing(
        carbon_credit_per_co2_tonne=carbon_credit_per_co2_tonne,
        pyroloysis_processing_cost_per_biochar_tonne=pyroloysis_processing_cost_per_biochar_tonne,
        carbon_resale_per_biochar_tonne=carbon_resale_per_biochar_tonne,
        land_per_biochar_tonne=land_per_biochar_tonne,
        land_value_per_ha=land_value_per_ha
    )
    costs = [cost_converter(cb) for cb in captured_biomass]

    return costs, years

if __name__ == "__main__":
    costs, years = srf_model()
    plt.plot(years, costs)
    plt.xlabel('Years')
    plt.ylabel('Net Revenue (GBP)')
    plt.title('Net Revenue from Woodland Carbon Capture')
    plt.show()