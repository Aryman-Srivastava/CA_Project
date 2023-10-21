import random

class Core:
    def __init__(self, core, InterConnectNetwork):
        self.cacheController = CacheController(core, InterConnectNetwork)
        self.core = core

    def Execute(self, command, address, immediate=None):
        print("\n")
        print(command, address)
        print("\n")

        address = int(address, 2)
        if(command == "LS"):
            transaction = "GetShared"
            print("GetShread Transaction Issued to the CacheController of Core = "+str(self.core))
            self.cacheController.GetShared(self.core, address, transaction)
            
        elif command == "LM":
            # random_index = random.randint(0, len(self.cacheController.cache) - 1)
            transaction = "GetModified"
            self.cacheController.GetModified(self.core, address, transaction)
            
        elif(command == "ADD"):
            transaction = "GetModified"
            self.cacheController.GetModified(self.core, address, transaction)
            for i in range(4):
                if(self.cacheController.cache[i].tag == address):
                    Data = self.cacheController.cache[i].data
                    Data = Data+immediate
                    self.cacheController.random_index = i
                    self.cacheController.WriteBack(address, Data)
                    break
        
        else:
            transaction = "PUT"
            self.cacheController.Put(transaction, address)


class CacheLine:
    
    def __init__(self):
        self.tag = "00000" # Binary Number as 32 address we need 5 bits
        self.data = int("0"*32,2) # 32 bit 
        self.state = "" # Binary Number as we have 3 states (M, S, I)
        

class DirectoryLine:
    def __init__(self):
        self.state = "I" # Binary Number as we have 3 states (M, S, I)
        self.sharer = "00" # Hot encoded for 2 cores
        self.arr = [self.state, self.sharer]

class CacheController:
    def __init__(self, core, InterConnectNetworkObject):
        self.cache = [CacheLine() for i in range(4)] 
        self.InterConnectNetwork = InterConnectNetworkObject
        self.core = core
        self.random_index = None
        
    def WriteBack(self, address, data):
        random_index = self.random_index
        if self.cache[random_index].state == "M" or self.cache[random_index].state == "I":
            self.cache[random_index].data = data
            self.cache[random_index].state = "M"
            dataWriteBack = True
            stateWriteBack = False
            self.InterConnectNetwork.WriteBackRequestToDirectoryController(self.core, data, address, dataWriteBack, stateWriteBack)
            self.random_index = None

    def DataResponse(self, data, address, transaction):
        print("Cache Controller got Data Response got from Interconnect")
        dataWriteBack = False
        stateWriteBack = False

        if self.random_index == None:
            random_index = random.randint(0, 3)
        else:
            random_index = self.random_index

        if(self.cache[random_index].data == 0): # writing the data in cache's empty location
            print("Writing data into emply space of cache -- Location = "+ str(random_index))
            if(transaction=="GetShared"):
                self.cache[random_index].data = data
                self.cache[random_index].state = "S"
                self.cache[random_index].tag = address
                print("Data Received in S State")
                print("Updated Cache Line - "+str(self.cache[random_index].tag)+" "+str(self.cache[random_index].state)+" "+str(self.cache[random_index].data))
            elif(transaction=="GetModified"):
                self.cache[random_index].data = data
                self.cache[random_index].state = "M"
                self.cache[random_index].tag = address
        else:
            if((self.cache[random_index].state == "S" or self.cache[random_index].state == "M") and self.cache[random_index].tag != address): # Eviction of data incase the location in cache is occupied
                old_state = self.cache[random_index].state
                old_data = self.cache[random_index].data
                old_address = self.cache[random_index].tag
                print("Cache Line needs to be Evaculated to Put new data at index = "+str(random_index))
                if(transaction=="GetShared"):
                    self.cache[random_index].data = data
                    self.cache[random_index].state = "S"
                    self.cache[random_index].tag = address
                elif(transaction=="GetModified"):
                    self.cache[random_index].data = data
                    self.cache[random_index].state = "M"
                    self.cache[random_index].tag = address
                print("Write Back Request --> InterConnect Network --> Directory Controller")
                if(old_state == "M" or old_state == "S"):
                    dataWriteBack = False
                    stateWriteBack = True
                    self.InterConnectNetwork.WriteBackRequestToDirectoryController(self.core, old_data, old_address, dataWriteBack, stateWriteBack) # Write back the old data to directory controller incase of eviction
            else:
                if(transaction=="GetShared"):
                    print("Latest Data received in shared state")
                    self.cache[random_index].data = data
                    self.cache[random_index].state = "S"
                    self.cache[random_index].tag = address
                elif(transaction=="GetModified"):
                    print("Latest Data received in modified state")
                    self.cache[random_index].data = data
                    self.cache[random_index].state = "M"
                    self.cache[random_index].tag = address

    def Response(self, address, transaction):
        if(transaction=="GetModified"): ## If this core1 has issued GetModified tran then it will get dataResponse and other core will get Response from Directory Controller
            for line in self.cache:
                if(line.tag == address):
                    line.state = "I"
                    print("Data Invalidated for address = "+str(address)+" at core = "+str(self.core))
                    return
            

    def GetShared(self, core, address, transaction):
        print(address)
        for line in self.cache:
            if(line.tag == address and (line.state == "M" or line.state == "S")):
                print("Data Hit in Cache of Core = "+str(core))
                return line.data
        self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction)
        return 
    
    def GetModified(self, core, address, transaction):
        flag=True
        for line in range(4):
            if(self.cache[line].tag == address):
                flag=False
                if(self.cache[line].state == "M"):
                    print("Data hit in cache and state match as M")
                    return self.cache[line].data # In case of hit
                else:
                    print("Data hit in cache but non-functional state = "+str(self.cache[line].state))
                    self.random_index = line
                    self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction)
        if flag:
            self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction)
        return
            

    def Put(self, transaction, address):
        if transaction == "PUT":
            for line in range(4):
                if(self.cache[line].tag == address ):
                    self.cache[line].state = "I"                    
                    print("Data Invalidated for address = "+str(address)+" at core = "+str(self.core))
                    self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction, lm=True)
                    break
        

# For every directory controller i have defined a main memory and a directory corresponding to every memory address
class DirectoryControllerClass: 
        def __init__(self, InterConnectNetwork):
            self.memory = [int("0"*32, 2) for _ in range(32)] # Initial Memory of 32bit X 32 Address
            self.directory = [DirectoryLine() for i in range(32)] # Initial Directory  same size as main memory
            self.InterConnectNetwork = InterConnectNetwork

        def Execute(self, core, address, transaction, lm=False):
            print("Directory Controller got request from Cache Controller "+str(transaction))
            state = self.directory[address].state
            sharer = self.directory[address].sharer
            if(transaction == "PUT"):
                if (core == 1):
                    self.directory[address].sharer = "0" + self.directory[address].sharer[1]
                else:
                    self.directory[address].sharer = self.directory[address].sharer[0] + "0"

                if self.directory[address].state == "M":
                    if self.directory[address].sharer == "00":
                        self.directory[address].state = "I"
                    elif lm:
                        self.directory[address].state = "S"
            
             # incase of non evacuation of data from cache
            elif(transaction == "GetShared"):
                # As this is write through i have the updated data at the memory and the non-requestor core will be the modifier
                if(state == "M" or state == "S"):
                    self.directory[address].sharer = "11" # Including both core in sharer
                if(state == "I"):
                    if(core == 1):
                        self.directory[address].sharer = "10" # Including both core in sharer
                    else:
                        self.directory[address].sharer = "01" # Including both core in sharer
                    print("Sharer List Updated to "+self.directory[address].sharer)
                    self.directory[address].state = "S"
                    print("Directory State Changed from I to S")
                self.InterConnectNetwork.DataResponseToCacheController(core, self.memory[address], address, transaction)
        
            elif(transaction == "GetModified"):
                if(state == "M"):
                    print("Modified access to core is switched from core = "+str(core)+ " to core = "+str(3-core))
                    self.InterConnectNetwork.ResponseToCacheController(3-core, address, transaction)
                    if(core == 1):
                        self.directory[address].sharer = "10" # Including both core in sharer
                        print("Sharer list updated to 10")
                    else:
                        self.directory[address].sharer = "01" # Including both core in sharer
                        print("Sharer list updated to 01")

                elif(state == "S"):
                    self.directory[address].state = "M"
                    if(int(self.directory[address].sharer,2) == 3):                   
                        self.InterConnectNetwork.ResponseToCacheController(3-core, address, transaction)
                elif(state == "I"):
                    if(core == 1):
                        self.directory[address].sharer = "10" # Including both core in sharer
                    else:
                        self.directory[address].sharer = "01" # Including both core in sharer
                    self.directory[address].state = "M"
                self.InterConnectNetwork.DataResponseToCacheController(core, self.memory[address], address, transaction)

            # Incorrect as old address is not passed which has been evacuated       
                         
            # # incase of evacuation of data from cache
            # if self.directory[address].state != 'S':
            #     if core == 1:
            #         self.directory[address].sharer = "0"+self.directory[address].sharer[1]
            #     else:
            #         self.directory[address].sharer = self.directory[address].sharer[0]+"0"
        
        def WriteBack(self, address, data, core, dataWriteBack, stateWriteBack):
            # if(dataWriteBack and stateWriteBack): # Modified data in cache is now being overwritten so we need to change the state in memory from M to S
            #     if(self.directory[address].state == "M"):
            #         print("Directory Controller has re-written memory address with updated data")
            #         if(core == 1):
            #             if(self.directory[address].sharer == "10"):
            #                 print("Memory Address Not shared with complmentary core = "+str(3-core))
            #             elif(self.directory[address].sharer == "11"):
            #                 print("Directory Controller --> InterConnect Network --> Complementary Core = "+str(3-core))
            #                 self.InterConnectNetwork.ResponseToCacheController(3-core, address, "GetModified")               
            #         else:
            #             if(self.directory[address].sharer == "01"):
            #                 print("Memory Address Not shared with complmentary core = "+str(3-core))
            #             elif(self.directory[address].sharer == "11"):
            #                 print("Directory Controller --> InterConnect Network --> Complementary Core = "+str(3-core))
            #         print("Directory State Change from"+str(self.directory[address].state)+" to "+ "S")
            #         self.directory[address].state = "S"
            #     elif(dataWriteBack and not stateWriteBack):
            #         print("Data in complementary core is invalidated")
            #         self.InterConnectNetwork.ResponseToCacheController(3-core, address, "GetModified") 
            #     elif(not dataWriteBack and stateWriteBack):
                    
            print("dataWriteBack = "+str(dataWriteBack)+" stateWriteBack = "+str(stateWriteBack))
            if(dataWriteBack and not stateWriteBack):
                self.memory[address] = data
                if(self.directory[address].sharer=="11"):
                    self.InterConnectNetwork.ResponseToCacheController(core, address, "GetModified")
            elif(not dataWriteBack and stateWriteBack):
                if(int(self.directory[address].sharer,2)==3-core):
                    self.directory[address].state = "I"
                    self.directory[address].sharer = "00"
                elif(int(self.directory[address].sharer,2)==3):
                    self.directory[address].state = "S"
                    if(core == 1):
                        self.directory[address].sharer = "01"
                    else:
                        self.directory[address].sharer = "10"
            else:
                print("Invaid Call to Write Back of Directory Controller")


class InterConnectClass:
    def __init__(self):
        self.CacheController1 = None
        self.CacheController2 = None
        self.DirectoryController = None
        

    def WriteBackRequestToDirectoryController(self, core, data, address, dataWriteBack, stateWriteBack):
        print("Write Back request forwaded to Directory Controller")
        self.DirectoryController.WriteBack(address, data, core, dataWriteBack, stateWriteBack)

    def RequestToDirectoryController(self, core, address, transaction, lm=False):
        print("Interconnect called")
        self.DirectoryController.Execute(core, address, transaction, lm)

    def DataResponseToCacheController(self, core, data, address, transaction): # If the core asks asks for data then forward using this
        print("Directory COntroller (Data)--> InterConnect Network --> Cache Controller")
        if(core==1):
            self.CacheController1.DataResponse(data, address, transaction)
        else:
            self.CacheController2.DataResponse(data, address, transaction)


    def ResponseToCacheController(self, core, address, transaction): # RequestToDirectoryControllerIf only state updating needs to be done
        print("Interconnect Network called from Direcory Controller to Cache Controller")
        if(core==1):
            self.CacheController1.Response(address, transaction)
        else:
            self.CacheController2.Response(address, transaction)



InterConnectNetwork = InterConnectClass()
Core1 = Core(1,InterConnectNetwork)
Core2 = Core(2,InterConnectNetwork)
DirectoryController = DirectoryControllerClass(InterConnectNetwork)

InterConnectNetwork.CacheController1 = Core1.cacheController
InterConnectNetwork.CacheController2 = Core2.cacheController
InterConnectNetwork.DirectoryController = DirectoryController
DirectoryController.memory = [1]*32

with open("dump.txt","w") as dump, open("log.txt","w") as log:
    with open("instFile.txt","r") as file:
        for instruction in file:
            instruction = instruction.split(" ")
            if len(instruction) == 3:
                [core, command, address] = instruction
                core = int(core)
                if(core == 1):
                    Core1.Execute(command, address)
                else:
                    Core2.Execute(command, address)
            else:
                [core, command, address, immediate] = instruction
                core = int(core)
                if(core == 1):
                    Core1.Execute(command, address, int(immediate[1:],2))
                else:
                    Core2.Execute(command, address, int(immediate[1:],2))


            log.write(str(instruction)+"\n")
            log.write("Core1\n")
            for cacheIndex in range(4):
                log.write("{"+str(Core1.cacheController.cache[cacheIndex].tag)+" {"+str(Core1.cacheController.cache[cacheIndex].state)+"} "+str(Core1.cacheController.cache[cacheIndex].data)+"}\n")
            log.write("\n")
            log.write("\nCore2\n")
            for cacheIndex in range(4):
                log.write("{"+str(Core2.cacheController.cache[cacheIndex].tag)+" {"+str(Core2.cacheController.cache[cacheIndex].state)+"} "+str(Core2.cacheController.cache[cacheIndex].data)+"}\n")
            log.write("\n")         
            dump.write(str(instruction))
            dump.write("\n[")
            for lineIndex in range(len(DirectoryController.memory)):
                dump.write(str(format(lineIndex,'06b'))+" "+str(DirectoryController.memory[lineIndex])+", Directory Entry = "+str(DirectoryController.directory[lineIndex].state)+" {"+str(DirectoryController.directory[lineIndex].sharer)+"}\n")
            dump.write("]\n")
