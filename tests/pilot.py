"""Пилот передаёт команды реальному аппарату без собственной логики полёта."""

class Pilot:
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def take_off(self):
        return self.vehicle.take_off()

    def land(self):
        return self.vehicle.land()

    def move(self, distance_km):
        return self.vehicle.move(distance_km)

    def add_sins(self, amount):
        return self.vehicle.add_sins(amount)

    def absolve_sins(self):
        return self.vehicle.absolve_sins()
