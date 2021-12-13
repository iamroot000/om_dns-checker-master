from nslookup import Nslookup
import sys, json, pprint


class nsCheck(object):
        """docstring for nsCheck"""

        def get_info(self,domains):
                dns_server = ["180.76.76.76"]
                rval = []
                dns_query = Nslookup(dns_servers=dns_server)
                ips_record = dns_query.dns_lookup(domains)
                ip = ips_record.answer

                data ={
                        'ip': ip,
                        'nameserver': dns_server
                }
                count = 0
                while count <= 3 :
                        ips_record = dns_query.dns_lookup(domains)
                        ip = ips_record.answer
                        if not ip:

                                count  = count + 1
                                print(count)
                        else:
                                return data

                return data

if __name__=="__main__":
        domains = '777.bbet8.me'
        g = nsCheck()
        print(g.get_info(domains))

