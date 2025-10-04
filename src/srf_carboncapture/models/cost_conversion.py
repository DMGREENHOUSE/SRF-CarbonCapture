class BiocharProcesssing:
    def __init__(self,
                 carbon_credit_per_co2_tonne=1.,
                 pyroloysis_processing_cost_per_biochar_tonne=1.,
                 carbon_resale_per_biochar_tonne=1.,
                 land_per_biochar_tonne=0.,
                 land_value_per_ha=0.
                 ):
        self.carbon_credit_per_co2_tonne = carbon_credit_per_co2_tonne
        self.pyroloysis_processing_cost_per_biochar_tonne = pyroloysis_processing_cost_per_biochar_tonne
        self.carbon_resale_per_biochar_tonne = carbon_resale_per_biochar_tonne
        self.land_per_biochar_tonne = land_per_biochar_tonne
        self.land_value_per_ha = land_value_per_ha

    def __call__(self, biochar):
        return self.carbon_credits(biochar=biochar) + self.carbon_resale(biochar=biochar) + self.land_use(biochar=biochar) - self.pyroloysis_processing(biochar=biochar)

    def carbon_credits(self, biochar):
        """
        Convert biochar mass (tonne) into carbon credit (usd)
        """
        carbon_to_co2_conversion = ((16+16) / 12)
        return biochar * carbon_to_co2_conversion * self.carbon_credit_per_co2_tonne

    def pyroloysis_processing(self, biochar):
        """
        Convert biochar mass (tonne) into pyroloysis processing cost (usd)
        """
        return biochar * self.pyroloysis_processing_cost_per_biochar_tonne

    def carbon_resale(self, biochar):
        return biochar * self.carbon_resale_per_biochar_tonne 

    def land_use(self, biochar):
        return biochar * self.land_per_biochar_tonne * self.land_value_per_ha 
    