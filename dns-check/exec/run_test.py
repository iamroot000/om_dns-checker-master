import mysql.connector

import socket

import whois

import requests

import json

import time

import datetime

import os

import logging





class greatChecker(object):





    def __init__(self, host, user, passwd, dbase):

        self.host = host

        self.user = user

        self.passwd = passwd

        self.dbase = dbase

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.my_path = os.path.join(BASE_DIR, 'exec')



    def loggingFile(self, log_debug=None, log_info=None, log_warning=None, log_error=None, log_critical=None):

        logdir = os.path.join(self.my_path, 'logs/')

        os.popen("find {0} -type f -name '*.log' -mtime +40 -exec rm {1} \;".format(logdir, '{}'))

        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"

        logging.basicConfig(

            filename='{}{}-{}.log'.format(logdir, "mysqlsave", datetime.datetime.now().strftime("%Y-%m-%d")),

            format=LOG_FORMAT, level=logging.DEBUG)

        logger = logging.getLogger()

        if log_debug:

            logger.debug(str(log_debug))

        if log_info:

            logger.info(str(log_info))

        if log_warning:

            logger.warning(str(log_warning))

        if log_error:

            logger.error(str(log_error))

        if log_critical:

            logger.critical(str(log_critical))





    def conn(self):

        mydb = mysql.connector.connect(

            host=self.host,

            user=self.user,

            passwd=self.passwd,

            database=self.dbase

        )

        return mydb



    def get_dom(self):

        mydb = self.conn()

        cur = mydb.cursor()

        cur.execute("SELECT domain FROM SSLDOMAINS_ssldomain2")

        domains = cur.fetchall()

        return domains


    def get_cdndom(self):

        mydb = self.conn()

        cur = mydb.cursor()

        cur.execute("SELECT domain FROM cdn_cdndomain")

        domains = cur.fetchall()

        return domains

    def get_exdom(self):

        file_list = []

        file = os.path.join(self.my_path, 'exclude_dom.txt')

        file = open(file).read()

        for i in file.split():

            if len(i) != 0:

                file_list.append((i.strip(),))

        return file_list



    def get_registrar(self, dom):

        registrar = ''

        try:

            domain = whois.query(dom)

            registrar = domain.registrar

            self.loggingFile(log_debug="{}".format("#####" * 20))

            self.loggingFile(log_debug="Registrar Query OK", log_info=str("The Registrar is {}".format(registrar)))

        except Exception as e:

            self.loggingFile(log_debug="{}".format("#####" * 20))

            self.loggingFile(log_debug="Registrar Query ERROR", log_error=str(e))

            registrar = 'not found'

        return registrar



    def compare(self, ip1, ip2):

        res = ''

        if ip1 != 'error' and ip2 != 'error':

            if ip1 != ip2:

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="Comapre IP1 {} and IP2 {}".format(ip1, ip2), log_info=str("Result is 1"))

                res = '1'

            else:

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="Comapre IP1 {} and IP2 {}".format(ip1, ip2), log_info=str("Result is 0"))

                res = '0'

        else:

            self.loggingFile(log_debug="{}".format("#####" * 20))

            self.loggingFile(log_debug="Comapre IP1 {} and IP2 {}".format(ip1, ip2), log_info=str("Result is 2"))

            res = '2'

        return res



    def lezdodiz(self):

        lizt = self.get_dom()

        mydb = self.conn()

        cur = mydb.cursor()

        cur.execute("DELETE from {}".format("dnsdomainchecker"))

        for dom in lizt:

            (dom,) = dom

            dom = str(dom)

            data = {

                'get_domains': dom,

            }

            self.loggingFile(log_debug="{}".format("#####" * 20))

            self.loggingFile(log_debug="Domain Value", log_info=str("Domain is {}".format(dom)))

            try:

                idc = requests.post('http://127.0.0.1:8002/domain-checker/', data=data, timeout=120)

                idc = idc.json()

                idc = str(idc)

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="IDC API check OK", log_info=str("IDC Output is {}".format(idc)))

            except Exception as e:

                print('Timedout check 8002')

                idc = 'error'

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="IDC API check ERROR", log_error=str(e))

            registrar = self.get_registrar(dom)



            try:

                # china = requests.post('http://127.0.0.1:8001/domain-checker/', data=data, timeout=5)

                china = requests.post('http://120.24.167.117:8050/domain-checker/', data=data, timeout=120)

                china = china.json()

                #                               print china

                china_ip = str(china['ip'][0])

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="China API check OK", log_info=str("China Output is {}".format(china_ip)))

                china_nameserver = str(china['nameserver'][0])

                status = self.compare(china_ip, idc)

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="China API Get json OK ", log_info=str(china))

            except Exception as e:

                #       print 'Timedout check 8001'

                print(str(e))

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="China API check ERROR", log_error=str(e))

                china_ip = 'error'

                china_nameserver = "error"

                status = self.compare(china_ip, idc)

                self.loggingFile(log_debug="{}".format("#####" * 20))

                self.loggingFile(log_debug="China API Get json ERROR ", log_error=str(e))

                time.sleep(15)







            date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            sql = "INSERT INTO dnsdomainchecker(domain,idc,registrar,china,dns,date,result)VALUES(%s,%s,%s,%s,%s,%s,%s)"

            val = (dom, idc, registrar, china_ip, china_nameserver, date_now, status)

            self.loggingFile(log_debug="{}".format("#####" * 20))

            self.loggingFile(log_debug="All Value", log_info=str(val))

            cur.execute(sql, val)

            print(val)

            mydb.commit()

        #               mydb.save()

        return True





if __name__ == "__main__":

    host = "10.165.22.205"

    user = "yrollrei"

    passwd = "s22-C350"

    dbase = "argus_v2"



    g = greatChecker(host, user, passwd, dbase)



    domains = set([('client.ebdf.online',),('google.com',),('youtube.com',),(u'pc.yngtcb.cn',), (u'pc.baoyinlei.top',), (u'hkc.glzhan.cn',)]) - set(g.get_cdndom()) - set(g.get_exdom())
    for dom in domains:
        (dom,) = dom

        dom = str(dom)
        print(dom)




# print g.compare('123123','123321')
