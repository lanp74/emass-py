"""
parser.py: parser for molecular formulas

Author: Lan Peng <lanp74@sina.com>

Based on c++ source of EMass tools developed by Perttu Haimi
"""

class Parser:
    def __init__(self, elem_map={}):
        self.__elem_map = elem_map
        self.__tokenizer = None
        
    def parse(self, formula):
        fm = {}
        self.__tokenizer = Tokenizer(formula)
        self.__tokenizer.next_token()
        
        element_list = self.__parse_node()
        
        if self.__tokenizer.ttype() != TokenType.EOS:
            raise Exception("End of input expected")
        
        element_list.fill_compound(1, fm)
        self.__clean_formula(fm)
        return fm
    
    def __clean_formula(self, fm):
        erasable_keys = []        
        for key in fm:
            if fm[key] == 0:
                erasable_keys.append(key)                
        for key in erasable_keys:
            del fm[key]            
        return
    
    def __parse_node(self):
        inner = ElementListNode()
        outer = ElementListNode()
        
        while self.__tokenizer.ttype() == TokenType.LPAREN or \
                self.__tokenizer.ttype() == TokenType.ELEMENT:
                
            if self.__tokenizer.ttype() == TokenType.LPAREN:
                self.__tokenizer.next_token()
                inner = self.__parse_node()
                if self.__tokenizer.ttype() != TokenType.RPAREN:
                    raise Exception("Expected right parenthesis!")
            else:
                # new element
                if self.__elem_map.__contains__(self.__tokenizer.tval()):
                    # find element
                    inner = ElementListNode(self.__tokenizer.tval())
                else:
                    raise Exception(self.__tokenizer.tval() + " is not an element!")
             
            self.__tokenizer.next_token()
            
            if self.__tokenizer.ttype() == TokenType.NUM:
                count = 0
                try:
                    count = int(self.__tokenizer.tval())
                except:
                    count = 0
                inner.set_count(count)
                self.__tokenizer.next_token()
                
            outer.add(inner)
        return outer
              
        
class TokenType:
    LPAREN = 1
    RPAREN = 2
    EOS = 3
    NUM = 4
    ELEMENT = 5
    
class States:
    START = 1
    ALPHA = 2
    LITERAL = 3
    NUMBER = 4
    END = 5
    STOP = 6
        
class Tokenizer:
    ENDTOKEN = "%END%"
    def __init__(self, formula):
        self.__input = formula
        self.__ttype = TokenType.EOS
        self.__tval = ""
        self.__i = 0
        self.__last = 0
        self.__input += Tokenizer.ENDTOKEN
            
    def ttype(self):
        return self.__ttype
    
    def tval(self):
        return self.__tval
        
    def next_token(self):
        s = States.START
        self.__last = self.__i
        
        while True:
            c = self.__input[self.__i]
            
            if s == States.START:
                if c.isdigit() or c == "-":
                    self.__ttype = TokenType.NUM
                    self.__tval = c
                    s = States.NUMBER
                elif c.isupper():
                    self.__ttype = TokenType.ELEMENT
                    self.__tval = c
                    s = States.ALPHA
                elif c == "[":
                    self.__ttype = TokenType.ELEMENT
                    self.__tval = ""
                    s = States.LITERAL
                elif c == "(":
                    self.__ttype = TokenType.LPAREN
                    s = States.STOP
                elif c == ")":
                    self.__ttype = TokenType.RPAREN
                    s = States.STOP
                elif c == "%":
                    self.__ttype = TokenType.EOS
                    s = States.END
                else:
                    raise Exception("Parse Error!")
                    
            elif s == States.ALPHA:
                if c.islower():
                    self.__tval += c
                else:
                    return
                
            elif s == States.LITERAL:
                if c == "%":
                    raise Exception("Missing left bracket!")
                elif c != "]":
                    self.__tval += c
                else:
                    self.__i += 1
                    return
            
            elif s == States.NUMBER:
                if c.isdigit():
                    self.__tval += c
                else:
                    return
                
            elif s == States.END:
                if self.__input.rfind(Tokenizer.ENDTOKEN) == self.__i - 1:
                    s = States.STOP
                else:
                    raise Exception("Illegal character: %")
            elif s == States.STOP:
                return 
            
            self.__i += 1        
        return
        
        
class INode:
    def __init__(self):
        return
    
    def fill_compound(weight, fm):
        return
    
class ElementNode(INode):
    def __init__(self, element):
        self.__element = element
        
    def fill_compound(self, weight, fm):
        if fm.__contains__(self.__element):
            fm[self.__element] += weight
        else:
            fm[self.__element] = weight
            
class ElementListNode(INode):        
    def __init__(self, element=""):
        self.__node_list = []
        self.__count = 1
        if element != "":
            en = ElementNode(element)
            self.__node_list.append(en)
        
    def add(self, node):
        self.__node_list.append(node)
        
    def set_count(self, n):
        self.__count = n
        
    def fill_compound(self, weight, fm):
        total_weight = self.__count * weight
        for node in self.__node_list:
            node.fill_compound(total_weight, fm)
            