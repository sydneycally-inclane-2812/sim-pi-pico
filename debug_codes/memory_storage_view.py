import gc
import os

# Function to gather memory stats
def get_memory_stats():
    gc.collect()  # Collect garbage and free up memory
    free_memory = gc.mem_free()
    allocated_memory = gc.mem_alloc()
    total_memory = free_memory + allocated_memory
    print("Memory Stats:")
    print(f"Total memory: {total_memory} bytes")
    print(f"Free memory: {free_memory} bytes")
    print(f"Allocated memory: {allocated_memory} bytes")
    print("-" * 30)

# Function to gather storage stats
def get_storage_stats():
    statvfs = os.statvfs('/')
    block_size = statvfs[0]
    total_blocks = statvfs[2]
    free_blocks = statvfs[3]
    total_storage = block_size * total_blocks
    free_storage = block_size * free_blocks
    used_storage = total_storage - free_storage
    print("Storage Stats:")
    print(f"Total storage: {total_storage} bytes")
    print(f"Used storage: {used_storage} bytes")
    print(f"Free storage: {free_storage} bytes")
    print("-" * 30)

# Call both functions
get_memory_stats()
get_storage_stats()
