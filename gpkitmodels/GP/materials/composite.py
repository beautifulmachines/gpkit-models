from gpkit import Model, Var


class CFRPFabric(Model):
    "Carbon Fiber Reinforced Plastic Fabric Material Properties"

    rho = Var("g/cm^3", "density of CFRP", value=1.6)
    tmin = Var("mm", "minimum gauge thickness", value=0.3048)
    tau = Var("MPa", "torsional stress limit", value=570)
    E = Var("GPa", "Youngs modulus", value=150)
    sigma = Var("MPa", "max stress", value=400)
    G = Var("GPa", "shear modulus", value=2)

    def setup(self):
        pass


class CFRPUD(Model):
    "Carbon Fiber Reinforced Plastic Unidirectional Material Properties"

    rho = Var("g/cm^3", "density of CFRP", value=1.6)
    E = Var("GPa", "Youngs Modulus of CFRP", value=137)
    sigma = Var("MPa", "maximum stress limit of CFRP", value=1700)
    tmin = Var("mm", "minimum gauge thickness", value=0.1)

    def setup(self):
        pass


class Kevlar(Model):
    "Kevlar Material Properties"

    rho = Var("g/cm^3", "density of Kevlar", value=0.049)
    tmin = Var("in", "minimum gauge thickness", value=0.012)
    tau = Var("MPa", "torsional stress limit", value=200)

    def setup(self):
        pass
