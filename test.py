class Main:
    a = 'a' #Attribute
    _b = 'b' #Hideen but can use
    __c = 'c' #Hidden but can't use
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def show(self):
        print("GREETINGS FROM MAIN")

class Sub(Main):
    def __init__(self, x, y, z):
        self.z = z
        super().__init__(x, y)
    def test(self):
        super().show()
    def only_sub(self):
        print("Greetings from sub:", self.z)

##print(Main(1,2).__class__ == type(Main(1,2)))
##Sub(1, 2, 3).show()
##Sub(1, 2, 3).only_sub()
##Sub(1, 2, 3).test()
