class InterConnectClass:
    def __init__(self):
        self.CacheController1 = None
        self.CacheController2 = None
        self.CacheController3 = None
        self.CacheController4 = None
        self.DirectoryController = None
        
    # Write Back Request to Directory Controller
    def WriteBackRequestToDirectoryController(self, core, data, address, dataWriteBack, stateWriteBack):
        
        print("Write Back request forwaded to Directory Controller")
        self.DirectoryController.WriteBack(address, data, core, dataWriteBack, stateWriteBack)

    # Request to Directory Controller for data
    def RequestToDirectoryController(self, core, address, transaction, lm=False):
        print("Interconnect called")
        self.DirectoryController.Execute(core, address, transaction, lm)

    # Data response to Cache Controller
    def DataResponseToCacheController(self, core, data, address, transaction):
        print("Returning Data to the Cache Controller")
        if(core==1):
            self.CacheController1.DataResponse(data, address, transaction)
        elif(core==2):
            self.CacheController2.DataResponse(data, address, transaction)
        elif(core==3):
            self.CacheController3.DataResponse(data, address, transaction)
        else:
            self.CacheController4.DataResponse(data, address, transaction)

    # Response of Cache Controller for state update
    def ResponseToCacheController(self, core, address, transaction, lm):
        print("Interconnect Network called from Direcory Controller to Cache Controller")
        if(core==1):
            self.CacheController1.Response(address, transaction, lm)
        elif(core==2):
            self.CacheController2.Response(address, transaction, lm)
        elif(core==3):
            self.CacheController3.Response(address, transaction, lm)
        else:
            self.CacheController4.Response(address, transaction, lm)
            
    def DataResponseToDirectoryController(self, core, data, address, transaction):
        print("Returning Data to the to the Directory Controller from Cache Controleller")
        self.DirectoryController.DataResponse(core, data, address, transaction)
        
    def DataRequestFromCacheController(self, ownerCore, address, transaction, requestingCore):
        print("Data Request from Cache Controller to Interconnect Network")
        if(ownerCore == 1):
            self.CacheController1.dataReturn(address, transaction, requestingCore)
        elif(ownerCore ==2):
            self.CacheController2.dataReturn(address, transaction, requestingCore)
        elif(ownerCore ==3):
            self.CacheController3.dataReturn(address, transaction, requestingCore)
        else:
            self.CacheController4.dataReturn(address, transaction, requestingCore)

def int_to_5_bit_binary(num):
    binary_str = bin(num)[2:]  # Convert to binary and remove the '0b' prefix
    binary_str = binary_str.zfill(6)  # Pad with zeros to ensure a 5-bit representation
    return binary_str
