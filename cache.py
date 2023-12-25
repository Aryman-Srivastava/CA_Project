import random

class CacheLine:
    
    def __init__(self):
        self.tag = "000000" # Binary Number as 64 address we need 6 bits
        self.data = int("0"*32, 2) # 32 bit 
        self.state = "" # Binary Number as we have 4 states (M, S, I, O)
        self.lru_bits = "0"
        
class CacheSet:
    def __init__(self):
        self.lines = [CacheLine() for _ in range(2)]

class CacheController:
    def __init__(self, core, InterConnectNetworkObject):
        self.cache = [CacheSet() for _ in range(2)]
        self.InterConnectNetwork = InterConnectNetworkObject
        self.core = core
        self.random_index = None
        self.random_set = None
        
    def update_lru_bits(self, set, line):
        self.cache[set].lines[line].lru_bits = "1"
        self.cache[set].lines[1-line].lru_bits = "0"
    
    def get_set(self,address):
        if(address%2 == 0):
            return 0
        else:
            return 1
        
    def dataReturn(self, address, transaction, requestingCore):
        print("Returning Data to Cache Controller from Interconnect Network to core = " + str(requestingCore))
        for set in range(2):
            for line in range(2):
                if(self.cache[set].lines[line].tag == address):
                    self.cache[set].lines[line].state = "O"
                    self.InterConnectNetwork.DataResponseToCacheController(requestingCore, self.cache[set].lines[line].data, address, transaction)
        
    def WriteBack(self, address, data):
        random_index = self.random_index
        random_set = self.random_set
        
        if self.cache[random_set].lines[random_index].state == "M" or self.cache[random_set].lines[random_index].state == "I":
            
            self.cache[random_set].lines[random_index].data = data
            self.cache[random_set].lines[random_index].state = "M"
            dataWriteBack = True
            stateWriteBack = False
            
            # Write Through Request to Directory Controller
            self.InterConnectNetwork.WriteBackRequestToDirectoryController(self.core, data, address, dataWriteBack, stateWriteBack)
            self.random_index = None
            self.random_set = None

    def DataResponse(self, data, address, transaction):
        print("Cache Controller got Data Response got from Interconnect")
        dataWriteBack = False
        stateWriteBack = False
  
        if self.random_index == None :
            random_index = random.randint(0,1)
            random_set = self.get_set(address)
            for i in range(2):
                if self.cache[random_set].lines[i].lru_bits == "0":
                    random_index = i
                    break
        else:
            random_index = self.random_index
            random_set = self.random_set
        
        # Writing the data in cache's empty location
        if(self.cache[random_set].lines[random_index].data == 0 and self.cache[random_set].lines[random_index].tag == "00000"):
            print("Writing data into cache, Location = "+ str(random_index))
            
            if(transaction=="GetShared"):
                self.cache[random_set].lines[random_index].data = data
                self.cache[random_set].lines[random_index].state = "S"
                self.cache[random_set].lines[random_index].tag = address
                
                print("Data Received in S State")
                print("Updated Cache Line -- "+str(self.cache[random_set].lines[random_index].tag)+" "+str(self.cache[random_set].lines[random_index].state)+" "+str(self.cache[random_set].lines[random_index].data))
            
            elif(transaction=="GetModified"):
                self.cache[random_set].lines[random_index].data = data
                self.cache[random_set].lines[random_index].state = "M"
                self.cache[random_set].lines[random_index].tag = address
                print("Data Recieved in Modified State")
            self.update_lru_bits(random_set, random_index)
        
        # Eviction of data incase the location in cache is occupied
        else:
            if((self.cache[random_set].lines[random_index].state == "S" or self.cache[random_set].lines[random_index].state == "M") and self.cache[random_set].lines[random_index].tag != address): # Eviction of data incase the location in cache is occupied
                
                # Old Data
                old_state = self.cache[random_set].lines[random_index].state
                old_data = self.cache[random_set].lines[random_index].data
                old_address = self.cache[random_set].lines[random_index].tag
                
                print("Cache Line to be Evaculated For new data, index = "+str(random_index))
                
                if(transaction=="GetShared"):
                    self.cache[random_set].lines[random_index].data = data
                    self.cache[random_set].lines[random_index].state = "S"
                    self.cache[random_set].lines[random_index].tag = address
                
                elif(transaction=="GetModified"):
                    self.cache[random_set].lines[random_index].data = data
                    self.cache[random_set].lines[random_index].state = "M"
                    self.cache[random_set].lines[random_index].tag = address
                self.update_lru_bits(random_set, random_index)
                
                print("Write Back Request --> InterConnect Network --> Directory Controller")
                if(old_state == "M" or old_state == "S"):
                    dataWriteBack = False
                    stateWriteBack = True
                    
                    # Write back the old data to directory controller incase of eviction
                    self.InterConnectNetwork.WriteBackRequestToDirectoryController(self.core, old_data, old_address, dataWriteBack, stateWriteBack)
            else:
                # Data evicted is in Invalid State, hence not written back to Directory Controller
                if(transaction=="GetShared"):
                    print("Latest Data received in shared state")
                    self.cache[random_set].lines[random_index].data = data
                    self.cache[random_set].lines[random_index].state = "S"
                    self.cache[random_set].lines[random_index].tag = address
                
                elif(transaction=="GetModified"):
                    print("Latest Data received in modified state")
                    self.cache[random_set].lines[random_index].data = data
                    self.cache[random_set].lines[random_index].state = "M"
                    self.cache[random_set].lines[random_index].tag = address
                self.update_lru_bits(random_set, random_index)
            
            self.random_index = None
            self.random_set = None
            
    def Response(self, address, transaction, lm):
        
        if(lm):
            for set in self.cache:
                for line in set.lines:
                    if(line.tag == address):
                        print("Data Invalidated for address = "+str(address)+" at core = "+str(self.core)+"** DATA EVICTION **")
                        line.state = ""
                        line.data = 0
                        line.tag = ""
                        return
        
        ## If this core1 has issued GetModified tran then it will get dataResponse and other core will get Response from Directory Controller
        elif(transaction=="GetModified"):
            for set in self.cache:
                for line in set.lines:
                    if(line.tag == address):
                        line.state = "I"
                        print("Data Invalidated for address = "+str(address)+" at core = "+str(self.core))
                        return
                    
        elif(transaction == "ChangeStateToShared"):
            for set in self.cache:
                for line in set.lines:
                    if(line.tag == address):
                        line.state = "S"
                        print("Data Access altered from M to S address = "+str(address)+" at core = "+str(self.core))
                        return             

    def GetShared(self, core, address, transaction):
        print(address)
        for i, set in enumerate(self.cache):
            for j, line in enumerate(set.lines):
                if(line.tag == address and (line.state == "M" or line.state == "S")):
                    
                    print("Data Hit in Cache of Core = "+str(core))
                    self.update_lru_bits(i, j)
                    return line.data
        
        # Data Not Found Requesting Data in S State
        self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction, False)
        return 
    
    def GetModified(self, core, address, transaction):
        flag=True
        for set in range(2):
            for line in range(2):
                
                # Data Hit in Cache
                if(self.cache[set].lines[line].tag == address):
                    flag=False
                    
                    # Return Data if the state is M
                    if(self.cache[set].lines[line].state == "M"):
                        print("Data hit in cache and state match as M")
                        self.update_lru_bits(set, line)
                        return self.cache[set].lines[line].data 
                    
                    # Data Hit in Cache but not in M state hence requesting for modified access of data
                    else:
                        print("Data hit in cache but non-functional state = "+str(self.cache[set].lines[line].state))
                        self.random_index = line
                        self.random_set = set
                        self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction, False)
        
        # Data not found hence requesting for modified access of data
        if flag:
            self.InterConnectNetwork.RequestToDirectoryController(self.core, address, transaction, False)
        return
            

    def Put(self, transaction, address):
        if transaction == "PUT":
            for set in range(2):
                # Data Hit in Cache
                for line in range(2):
                    if(self.cache[set].lines[line].tag == address ):
                        self.cache[set].lines[line].state = "I"
                        self.cache[set].lines[line].data = 0
                        self.cache[set].lines[line].tag = ""               
                        print("Data Invalidated for address = "+str(address)+" at core = "+str(self.core))
                        self.InterConnectNetwork.WriteBackRequestToDirectoryController(self.core, None, address, False, True)
                        break