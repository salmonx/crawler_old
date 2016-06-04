class Error:
    def __init__(self):

            self.dns = 0  # Name or service not known  |  DNS 
            self.conntimeout = 0
            self.pooltimeout = 0
            self.reset = 0
            self.refuse = 0
            self.others = 0

            # record list
            self.rdns = [] 
            self.rconntimeout = []
            self.rpooltimeout = []
            self.rreset = []
            self.rrefuse = []
            self.rothers = []
            self.lasterrurl = ""


    def __str__(self):

            total = self.dns+self.conntimeout+self.pooltimeout+self.reset+self.refuse+self.others
            if total <= 0:
                return ""

            str = "[ERROR:%d " % total
            if self.dns > 0:
                str += "DNS:%d " % self.dns
            if self.conntimeout > 0:
                str += "CONN:%d " % self.conntimeout
            if self.reset > 0:
                str += "RESET:%d " % self.reset
            if self.refuse > 0:
                str += "REFUSE:%d " % self.refuse
            if self.pooltimeout > 0:
                str += "POOL:%d " % self.pooltimeout

            if self.others > 0:
                str += "OTHERS:%d" % self.others
            
            if len(str) > 0:
                str += " %s ]" %  (self.lasterrurl)
                    
            return str
