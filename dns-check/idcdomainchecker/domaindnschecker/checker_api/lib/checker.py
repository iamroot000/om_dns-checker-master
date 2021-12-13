import sys, pprint
import socket


class nsCheck(object):

        def get_info(self,domain):
                rVal = {}
                count = 0
                try:
                    while count <= 3:
                        rVal['ip'] = socket.gethostbyname(domain)
                        if not rVal['ip']:
                            print(count)
                        else:
                            return rVal['ip']
                except Exception as e:
                        print(e)
                        rVal['ip'] = 'error'


                return rVal

if __name__=="__main__":
        domain = 'jiab888.net'
        g = nsCheck()
        print(g.get_info(domain))

