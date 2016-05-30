#!/usr/bin/python  
# coding=utf-8  



hashbits=32


#生成simhash值     
def simhash(tokens):  
    v = [0] * hashbits  
    for t in [_string_hash(x) for x in tokens]: #t为token的普通hash值            
        for i in range(hashbits):  
            bitmask = 1 << i  
            if t & bitmask :  
                v[i] += 1 #查看当前bit位是否为1,是的话将该位+1  
            else:  
                v[i] -= 1 #否则的话,该位-1  
    fingerprint = 0  
    for i in range(hashbits):  
        if v[i] >= 0:  
            fingerprint += 1 << i  
    return fingerprint #整个文档的fingerprint为最终各个位>=0的和  
 
#求海明距离  
def hamming_distance(hash1 , hash2):


    x = (hash1 ^ hash2) & ((1 << hashbits) - 1)  
    tot = 0;  
    while x :  
        tot += 1  
        x &= x - 1  
    return tot  
 
#求相似度  
def similarity (hash1,hash2):  
    a = float(hash1)  
    b = float(hash2)  
    if a > b : return b / a  
    else: return a / b  
 
#针对source生成hash值   (一个可变长度版本的Python的内置散列)  
def _string_hash(source):         
    if source == "":  
        return 0  
    else:  
        x = ord(source[0]) << 7  
        m = 1000003  
        #mask = 2 ** hashbits - 1
        mask = 4294967295 # 2**32-1
        for c in source:  
            x = ((x * m) ^ ord(c)) & mask  
        x ^= len(source)  
        if x == -1:  
            x = -2  
        return x  



if __name__ == '__main__':
    
    s = 'a b c d'
    hash1 = simhash(s.split())
   
    s = 'a x b c d'
    hash2 = simhash(s.split())
   
    print(hamming_distance(hash1,hash2) , "   " , similarity(hash1,hash2))

