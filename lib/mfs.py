import gc
import os

def mem_stat():
    gc.collect()  # Collect garbage and free up memory
    allocd = gc.mem_alloc() / 1024
    free = gc.mem_free() / 1024
    print(allocd, "kb used out of ", (allocd + free), "kb", sep='')
    return    
        
    
def flash_stat():
    statvfs = os.statvfs('/')
    total = (statvfs[0] * statvfs[2]) // 1024
    free = (statvfs[0] * statvfs[3]) // 1024
    print(total - free, "kb used out of ", total, 'kb', sep='')
    print(free, 'kb free', sep='')
