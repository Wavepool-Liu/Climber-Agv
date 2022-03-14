class ControlArray:
    def __init__(self):
        pass
    def inArray(self,Tnumber, hello):
        for i in range(0,len(hello)):
            if Tnumber == hello[i]:
                return True
        return False

if __name__ == "__main__":
    a = ControlArray()
    clock = 0
    if a.inArray(clock,[10,11,12,1,2]):
        print("True")
    else:
        print("False")