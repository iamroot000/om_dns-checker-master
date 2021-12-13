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

                while  not ip:
                        print(ip)

                return data

if __name__=="__main__":
        domains = 'jiab88sdadnet'
        g = nsCheck()
        print(g.get_info(domains))

