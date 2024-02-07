class Class1:
    def __init__(self, alex):
        self.alex = alex

    def printAlex(self):
        print(self.alex)

class Class2(Class1):
    def __init__(self, alex):
        super().__init__(alex)

    def printAlex(self):
        super().printAlex()
        print(self.alex)

class1_instance = Class1(8)
class1_instance.printAlex()

class2_instance = Class2(8)
class2_instance.printAlex()