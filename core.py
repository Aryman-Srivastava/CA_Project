from cache import CacheController

class Core:
    def __init__(self, core, InterConnectNetwork):
        self.cacheController = CacheController(core, InterConnectNetwork)
        self.core = core

    # Execute Command to run core operations    
    def Execute(self, command, address, immediate=None):
        print("\n")
        print(command, address)
        print("\n")

        # LS Instruction
        address = int(address, 2)
        if(command == "LS"):
            transaction = "GetShared"
            print("GetShread Transaction Issued to CacheController-Core = "+str(self.core))
            for set in range(2):
                for line in range(2):
                    if(self.cacheController.cache[set].lines[line].tag == address):
                        self.cacheController.random_index = line
                        self.cacheController.random_set = set
                        break
            self.cacheController.GetShared(self.core, address, transaction)
        
        # LM Instruction
        elif command == "LM":
            # random_index = random.randint(0, len(self.cacheController.cache) - 1)
            transaction = "GetModified"
            self.cacheController.GetModified(self.core, address, transaction)
        
        # ADD Instruction
        elif(command == "ADD"):
            transaction = "GetModified"
            self.cacheController.GetModified(self.core, address, transaction)
            for set in range(2):
                for line in range(2):
                    if(self.cacheController.cache[set].lines[line].tag == address):
                        Data = self.cacheController.cache[set].lines[line].data
                        Data = Data+immediate
                        self.cacheController.random_index = line
                        self.cacheController.random_set = set
                        self.cacheController.WriteBack(address, Data)
                        break
        
        # IN Instruction
        else:
            transaction = "PUT"
            self.cacheController.Put(transaction, address)