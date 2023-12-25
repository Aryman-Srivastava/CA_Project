class DirectoryLine:
    def __init__(self):
        self.state = "I" # Binary Number as we have 3 states (M, S, I)
        self.sharer = "0000" # Hot encoded for 4 cores
        self.arr = [self.state, self.sharer]
        self.owner = None
        

class DirectoryControllerClass: 
        def __init__(self, InterConnectNetwork):
            self.memory = [int("0"*32, 2) for _ in range(64)] # Initial Memory of 32bit X 64 Address
            self.directory = [DirectoryLine() for i in range(64)] # Initial Directory same size as main memory
            self.InterConnectNetwork = InterConnectNetwork
            
        def DataResponse(self, core, data, address, transaction):
            self.memory[address] = data

        def Execute(self, core, address, transaction, lm=False):
            print("Directory Controller got request from Cache Controller "+str(transaction))
            state = self.directory[address].state
            sharer = self.directory[address].sharer

            # Put Transcation for Data Invalidation
            if(transaction == "PUT"):
                if(sharer[0] == "1"):                
                    self.InterConnectNetwork.ResponseToCacheController(1, address, transaction, lm)
                if(sharer[1] == "1"):
                    self.InterConnectNetwork.ResponseToCacheController(2, address, transaction, lm)
                if(sharer[2] == "1"):            
                    self.InterConnectNetwork.ResponseToCacheController(3, address, transaction, lm)
                if(sharer[3] == "1"):
                    self.InterConnectNetwork.ResponseToCacheController(4, address, transaction, lm)                  
                
                self.directory[address].sharer = "0000"
                self.directory[address].state = "I"

            # Get Shared Transcation for data request in Shared State
            elif(transaction == "GetShared"):
                
                # If state is Modified or Shared
                if(state == "S"):
                    if(core==1):
                        self.directory[address].sharer = "1" + sharer[1:]
                    elif(core==2 or core==3):
                        self.directory[address].sharer = sharer[:core-1] + "1" + sharer[core:]
                    else:
                        self.directory[address].sharer = sharer[:core-1] + "1"
                    self.directory[address].state = "S"
                    
                    # Requesting to change State to shared for other cores
                    for i in range(1, 5):
                        if i != core and sharer[i-1] == "1":
                            self.InterConnectNetwork.ResponseToCacheController(i, address, "ChangeStateToShared", False)
                
                    # Sending Data in Shared State
                    self.InterConnectNetwork.DataResponseToCacheController(core, self.memory[address], address, transaction)
                
                elif(state == "M"):
                    print("Changing Modified State to Owned State")
                    if(core==1):
                        self.directory[address].sharer = "1" + sharer[1:]
                    elif(core==2 or core==3):
                        self.directory[address].sharer = sharer[:core-1] + "1" + sharer[core:]
                    else:
                        self.directory[address].sharer = sharer[:core-1] + "1"
                    
                    self.directory[address].state = "O"
                    for i in range(len(sharer)):
                        if sharer[i] == "1":
                            self.directory[address].owner = i+1
                    self.InterConnectNetwork.DataRequestFromCacheController(self.directory[address].owner, address, transaction, core)
                
                # If state is Invalid
                elif(state == "I"):
                    if(core == 1):
                        self.directory[address].sharer =  "1" + sharer[1:]
                    elif(core==2 or core==3):
                        self.directory[address].sharer =  sharer[:core-1] +"1" + sharer[core:]
                    else:
                        self.directory[address].sharer = sharer[:core-1] + "1"
                        
                    print("Sharer List Updated to "+self.directory[address].sharer)
                    self.directory[address].state = "S"
                    print("Directory State Changed from I to S")
                        
                    # Sending Data in Shared State
                    self.InterConnectNetwork.DataResponseToCacheController(core, self.memory[address], address, transaction)
                
            # Get Modified Transcation for data request in Modified State
            elif(transaction == "GetModified"):
                
                if(state == "M"):
                    print("Modified access to core is switched from core = "+str(core)+ " to core = "+str(3-core))
                    
                    if(core == 1):
                        self.directory[address].sharer = "1000"
                    elif(core ==2):
                        self.directory[address].sharer = "0100"
                    elif(core ==3):
                        self.directory[address].sharer = "0010"
                    else:
                        self.directory[address].sharer = "0001"
                    print(f"Sharer list updated to {self.directory[address].sharer}")
                    
                    # Sending Request to invalidate data for other cores
                    # for i in range(1, 5):
                    #     if i != core and sharer[i-1] == "1":
                    #         self.InterConnectNetwork.ResponseToCacheController(i, address, transaction, False)
                    self.InterConnectNetwork.ResponseToCacheController(self.directory[address].owner, address, transaction, False)

                elif(state == "S"):
                    
                    if(core == 1):
                        self.directory[address].sharer = "1000"
                    elif(core ==2):
                        self.directory[address].sharer = "0100"
                    elif(core ==3):
                        self.directory[address].sharer = "0010"
                    else:
                        self.directory[address].sharer = "0001"
                    
                    # Sending Request to invalidate data for other cores
                    self.directory[address].state = "M"
                    for i in range(1, 5):
                        if i != core and sharer[i-1] == "1":
                            self.InterConnectNetwork.ResponseToCacheController(i, address, transaction, False)
                            
                elif(state == "O"):
                    self.directory[address].state = "M"
                    
                    # Sending Request to invalidate data for other cores including owner
                    for i in range(1, 5):
                        if i != core and sharer[i-1] == "1":
                            self.InterConnectNetwork.ResponseToCacheController(i, address, transaction, False)

                elif(state == "I"):
                    print("Directory Line in Invalid State called by core = "+str(core))
                    if(core == 1):
                        self.directory[address].sharer = "1000"
                    elif(core==2):
                        self.directory[address].sharer = "0100"
                    elif(core==3):
                        self.directory[address].sharer = "0010"
                    else:
                        self.directory[address].sharer = "0001"
                    
                    self.directory[address].state = "M"
                    
                    # Sending Request to invalidate data for other cores
                    # for i in range(1, 5):
                    #     if i != core and sharer[i-1] == "1":
                    #         self.InterConnectNetwork.ResponseToCacheController(i, address, transaction, False)
                
                # Sending Data in modified State
                self.InterConnectNetwork.DataResponseToCacheController(core, self.memory[address], address, transaction)

        def WriteBack(self, address, data, core, dataWriteBack, stateWriteBack):
            print("dataWriteBack = " + str(dataWriteBack) + " stateWriteBack = " + str(stateWriteBack))
            
            if(dataWriteBack and not stateWriteBack):
                print("Data Written in Memory")
                self.memory[address] = data
                if(self.directory[address].sharer == "1111"):
                    self.InterConnectNetwork.ResponseToCacheController(core, address, "GetModified", False)
                    
            elif(not dataWriteBack and stateWriteBack):
                
                if((self.directory[address].sharer.count("1")) == 1 and self.directory[address].sharer.index("1") == core-1):
                    self.directory[address].state = "I"
                    self.directory[address].sharer = "0000"
                    
                else:
                    self.directory[address].state = "S"
                    if(core == 1):
                        self.directory[address].sharer = "0" + self.directory[address].sharer[1:]
                    elif(core==2 or core == 3):
                        self.directory[address].sharer = self.directory[address][:core-1] + "0" + self.directory[address][core:]
                    elif(core==4):
                        self.directory[address].sharer = self.directory[address][:core-1] + "0"
                            
            else:
                print("Invaid Call to Write Back of Directory Controller")