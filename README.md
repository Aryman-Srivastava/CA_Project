# CA_Project

This repository stores project related in Course Computer Architecture. The description of project is as follows:

**About Coherency:**
Coherency refers to the consistency of data shared between different cores or processing units in a multi-core
processor. In a multi-core system, each core has its own local cache, which stores copies of data from the main
memory. In a single program, different threads might run on separate cores to perform parallel tasks. These threads
could be working on different aspects of the same problem and likely share the same data. When multiple cores
must work with the same data, coherency mechanisms ensure that all cores see a consistent view of that data.

**About Directories:**
A Directory is just one entity that is commonly used in Network architectures to maintain data coherency between
the cores. There are many ways of sizing and organizing the directory, and we consider a model where there is a
directory entry for every block of the memory.
**Coherency Protocol:**
A protocol is usually followed to effectively maintain data coherency. This is facilitated with the help of transactions
between the cores and the directory over the interconnect. For the purpose of this project, you do not need to
implement the interconnect network, but you can assume it is in place when making requests, transactions, and
responses (explained later). The coherency protocol to be followed is MOSI (Note: subtle differences exist in the
state implementations for MSI, MOSI, and other protocols). Each state in MOSI has been described below for clarity:

![image](https://github.com/Aryman-Srivastava/CA_Project/assets/88674260/997d40d8-c42c-4774-a1ff-eb32bf9fd478)

**Project Description:**
Every core is identical and follows the same set of instructions to communicate with the cache controller to fetch
data from the memory - into the cache. Following are the instructions, their description, and the reachable state(s)
because of their behavior:

![image](https://github.com/Aryman-Srivastava/CA_Project/assets/88674260/15716473-db29-426b-829c-f50cc7ce478a)

I.e., Each core can issue load requests to its cache controller; the cache controller will choose a block to evict when
it needs to make room for another block.
The Cache and Memory Organization:
1. The main-memory contains 64 address locations, and each L1 cache has 4 address locations.
2. Initialize the memory array with zeros at all locations.
3. Cache line width = size of memory location = 1 byte (byte-addressable)
4. The L1 caches must be 2 way set-associative, and the L1 controller follows the LRU (Least-Recently Used)
replacement policy.
5. The L1 cache controller also follows the write-through policy in the same cycle the data in a particular
address location is modified.

**Requests, Transactions, and Responses:**
Transactions between the cache controller and the directory controller are necessary to provide the cache
read/read-write access to a particular block in one of the mentioned coherence states (M, O, S, or I).
The request for these transactions is made by the core and passed on to its cache controller, which initiates the
appropriate transaction and gets a response from the destination. [2]
Acknowledgment from the destination as a response is omitted for the purpose of this project since every request
does get fulfilled in this simulation.
Valid Transaction for each of the mentioned instructions:

![image](https://github.com/Aryman-Srivastava/CA_Project/assets/88674260/eb9f48b9-375f-4ccc-80c7-e7c03b6fbf45)
