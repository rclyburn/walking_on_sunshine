from abc import ABC, abstractmethod


class BirdInterface(ABC):
    @abstractmethod
    def make_sound(self):
        pass

    @abstractmethod
    def fly(self):
        pass


class FlyEngine:
    def __init__(self):
        pass

    def make_me_fly(self):
        print("fly")


class Duck(BirdInterface):
    def __init__(self):
        self.fly_engine = FlyEngine()
        pass

    def duck_stuff(self):
        print("duck stuff")

    def make_sound(self):
        pass

    def fly(self):
        self.fly_engine.make_me_fly()


class Goose:
    def __init__(self):
        pass

    def goose_stuff(self):
        print("goose stuff")


def fly_with_bird(bird: BirdInterface):
    bird.fly()


duck = Duck()
goose = Goose()

fly_with_bird(duck)

# duck.bird.fly()
