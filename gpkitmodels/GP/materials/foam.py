from gpkit import Model, Var


class FoamHD(Model):
    "Foam high density material properties"

    rho = Var("g/cm^3", "foam density", value=0.036)

    def setup(self):
        pass


class FoamLD(Model):
    "Foam low density material properties"

    rho = Var("g/cm^3", "foam density", value=0.024)

    def setup(self):
        pass
