#!/usr/bin/python
# -*- coding: UTF-8 -*-

from .parser import Parser

class Peak:
    def __init__(self, _mass=0.0, _rel_area=0.0):
        self.mass = _mass
        self.rel_area = _rel_area
        
        
class EMass:    
    ELECTRON_MASS = 0.00054858
    DUMMY_MASS = -10000000
    
    def __init__(self, filepath="emass/ISOTOPE.DAT"):
        self.__elem_map = {}          #element map, map from element abbrevation to index in element list
        self.__elem_list = []         # list of list of peak 
        self.__filepath = filepath
        self.__init_data();

    def __init_data(self):
        elem_index = 0
        state = 0
   
        self.__elem_map.clear()
        self.__elem_list.clear();
        
        with open(self.__filepath, 'r', encoding = "utf8") as f:
            for index, line in enumerate(f.readlines()):
                line.strip()
                ist = line.split()
                
                if state == 0:
                    self.__elem_map[ist[0]] = elem_index
                    self.__elem_list.append([])
                    elem_index += 1
                    state = 1
                else:
                    p = Peak()
                    pattern = self.__elem_list[-1]
                    
                    if len(ist) >= 2:
                        p.mass = float(ist[0])
                        p.rel_area = float(ist[1])
                        
                        if len(pattern) > 0:
                            prev_mass = pattern[-1].mass
                            length = int(p.mass - prev_mass - 0.5)
                            for i in range(length):
                                filler = Peak(EMass.DUMMY_MASS, 0)
                                pattern.append(filler)
                                
                        pattern.append(p)
                    else:
                        state = 0
                        
    def calculate(self, formula, limit=0, charge=0):
        parser = Parser(self.__elem_map)
        fm = parser.parse(formula)
        result = self.__calculate(fm, limit, charge)
        return result
    
    def get_elem_map(self):
        return self.__elem_map;
    
    def get_elem_list(self):
        return self.__elem_list;
        
    def __calculate(self, fm, limit=0, charge=0):
        result = []
        
        # init result
        peak = Peak(0.0, 1.0)
        result.append(peak)
        
        for key in fm:
            elem_index = self.__elem_map[key]
            elem_count = fm[key]
            elem_pattern = self.__elem_list[elem_index]
            p_list = []
            p_list.append(elem_pattern)
            i = 0
            
            while elem_count > 0:
                sz = len(p_list)
                if i == sz:
                    p_list.append([])
                    EMass.__convolute_patterns(p_list[i], p_list[i-1], p_list[i-1])
                    EMass.__prune_pattern(p_list[i], limit)
                    
                if (elem_count & 1) > 0:
                    temp = []
                    EMass.__convolute_patterns(temp, result, p_list[i])
                    EMass.__prune_pattern(temp, limit)
                    result = temp
                    
                elem_count >>= 1
                i += 1
                
        for p in result:
            if charge > 0:
                p.mass = p.mass / charge - EMass.ELECTRON_MASS
            elif charge < 0:
                p.mass = p.mass / (0 - charge) + EMass.ELECTRON_MASS
                                               
        return result
    
    
    def __prune_pattern(pattern, limit):
        index = 0
        
        # prune the front
        while index < len(pattern):
            if pattern[index].rel_area > limit:
                break
            index += 1
            
        del pattern[0:index]
            
        # prune the end
        while True:
            if len(pattern) == 0:
                break
            if pattern[-1].rel_area > limit:
                break
            pattern.pop(-1)
            
        return
    
    def __convolute_patterns(result, g, f):
        result.clear()
        g_n = len(g)
        f_n = len(f)
        
        if g_n == 0 or f_n == 0:
            return
        
        for k in range(g_n + f_n - 1):
            sum_weight = 0
            sum_mass = 0
            
            start = 0
            if k >= (f_n - 1):
                start = k - f_n + 1
            end = k
            if k >= (g_n - 1):
                end = g_n - 1
                
            for i in range(start, end + 1):
                weight = g[i].rel_area * f[k-i].rel_area
                mass = g[i].mass + f[k-i].mass
                sum_weight += weight
                sum_mass += weight * mass
                
            p = Peak()
            if sum_weight == 0:
                p.mass = EMass.DUMMY_MASS
            else:
                p.mass = sum_mass/sum_weight
            
            p.rel_area = sum_weight
            result.append(p)      
        return
              
                      