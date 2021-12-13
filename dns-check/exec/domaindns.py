import json, datetime, logging, os, sys, mysql.connector, shutil, datetime, requests, time
from run import *
from smtp_send import sendMail




class DomainDNS():


    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.my_path = os.path.join(BASE_DIR, 'exec')
        secretfile = os.path.join(self.my_path, '.secret.json')
        data = open(secretfile, 'r')
        data = json.load(data)
        self.host = data["host"]
        self.user = data["user"]
        self.passwd = data["password"]
        self.database = data["database"]
        self.result_name = "result"
        self.domain_field = 1
        self.idc_field = 2
        self.china_field = 4
        self.result_field = 7
        self.table = 'dnsdomainchecker'
        self.column = "*"
        try:
            self.mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                database=self.database
            )
        except Exception as e:
            self.loggingFile(log_debug="{}".format("#####" * 20))
            self.loggingFile(log_debug="MySQL Query Error", log_error=str(e))


    def loggingFile(self, log_debug=None, log_info=None, log_warning=None, log_error=None, log_critical=None):
        logdir = os.path.join(self.my_path, 'logs/')
        os.popen("find {0} -type f -name '*.log' -mtime +40 -exec rm {1} \;".format(logdir, '{}'))
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(
            filename='{}{}-{}.log'.format(logdir, self.table,datetime.datetime.now().strftime("%Y-%m-%d-%H")),
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

    def domainException(self, domain=None):
        except_dom = ["gi.987rb.com"]
        f = open('domainexception.json', )
        domain_ex = json.load(f)
        if domain in domain_ex["DOMAIN"]:
            return True
        else:
            if domain not in except_dom:
                domain_ex["DOMAIN"].append(domain)
                f = open('domainexception.json', 'w')
                json.dump(domain_ex, f, indent=4)
            return False


    def mysqlQuery(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT {} FROM {} WHERE domain not in ('omtools.me') AND tags is NULL".format(self.column, self.table))
        data = mycursor.fetchall()
        self.loggingFile(log_debug="{}".format("#####" * 20))
        self.loggingFile(log_debug="MySQL Query", log_info=data)
        return data


    def mysqlEdit(self):
        dbdata = self.mysqlQuery()
        for i in dbdata:
            mycursor = self.mydb.cursor()
            if i[self.china_field] == 'error' or i[self.idc_field] == 'error':
                sql = "UPDATE {} SET {} = %s WHERE {} = %s".format(self.table, self.result_name, i[0])
                val = (2, i[0])
                self.loggingFile(log_debug="{}".format("#####" * 20))
                self.loggingFile(log_debug="MySQL Output Error", log_warning=i)
                self.loggingFile(log_debug="{}".format("-----" * 20))
                self.loggingFile(log_debug="MySQL Output Error info", log_warning="id={}, idc={}, china={}".format(i[0], i[self.dns_field], i[self.china_field]))
                mycursor.execute(sql, val)
            elif i[self.idc_field] != i[self.china_field]:
                sql = "UPDATE {} SET {} = %s WHERE {} = %s".format(self.table, self.result_name, i[0])
                val = (1, i[0])
                self.loggingFile(log_debug="{}".format("#####" * 20))
                self.loggingFile(log_debug="MySQL Output Not Equal", log_error=i)
                self.loggingFile(log_debug="{}".format("-----" * 20))
                self.loggingFile(log_debug="MySQL Output Not Equal info", log_error="id={}, idc={}, china={}".format(i[0], i[self.dns_field], i[self.china_field]))
                mycursor.execute(sql, val)
            elif i[self.idc_field] == i[self.china_field] and i[self.china_field] != 'error' or i[self.idc_field] != 'error':
                sql = "UPDATE {} SET {} = %s WHERE {} = %s".format(self.table, self.result_name, i[0])
                val = (0, i[0])
                self.loggingFile(log_debug="{}".format("#####" * 20))
                self.loggingFile(log_debug="MySQL Output Equal", log_info=i)
                self.loggingFile(log_debug="{}".format("-----" * 20))
                self.loggingFile(log_debug="MySQL Output Equal info", log_info="id={}, idc={}, china={}".format(i[0], i[self.dns_field], i[self.china_field]))
                mycursor.execute(sql, val)
            self.mydb.commit()
            mycursor.execute("SELECT {} FROM {}".format(self.column, self.table))
            self.loggingFile(log_debug="{}".format("+++++" * 20))
            self.loggingFile(log_debug="MySQL Output Error info", log_info="{}".format(mycursor.fetchall()))
        return "Database UPDATE"


    def mysqlZabbixQuery(self):
        rVal = {
            "data" : []
        }
        dbdata = self.mysqlQuery()
        for i in dbdata:
            if int(i[self.result_field]) > 0:
                rVal["data"].append({
                    "{#DOMAIN}": i[self.domain_field],
                    "{#IDC}": i[self.idc_field],
                    "{#CHINA}": i[self.china_field],
                    "{#RESULT}": int(i[self.result_field])
                }
                )
        return json.dumps(rVal, indent=4)


    def mysqlSendMail(self):
        chinadomain = "http://www.chinafirewalltest.com/?siteurl="
        to_send = []
        rVal = {
            "data": []
        }
        dbdata = self.mysqlQuery()
        for i in dbdata:
            if int(i[self.result_field]) > 0:
                _data = {"get_domains": "https://{}".format(i[self.domain_field])}
                try:
                    _result = requests.post('http://120.24.167.117:8050/domain-checker/access/', data=_data, timeout=120).json()
                    # _result = {u'dom_status': 1}
                except Exception as e:
                    self.loggingFile(log_debug="{}".format("#####" * 20))
                    self.loggingFile(log_debug="China API Check ERROR.".format(i[self.domain_field]),
                                     log_error=str(e))
                    time.sleep(10)
                    for i2 in range(0,3):
                        try:
                            _result = requests.post('http://120.24.167.117:8050/domain-checker/access/', data=_data,
                                                timeout=120).json()
                            break
                        except Exception as e:
                            self.loggingFile(log_debug="{}".format("#####" * 20))
                            self.loggingFile(log_debug="{} try: China API Check ERROR.".format(i2, i[self.domain_field]),
                                             log_error=str(e))
                            _result = {'dom_status': 2}
                mycursor = self.mydb.cursor()
                val = (int(_result["dom_status"]), i[self.domain_field])
                mycursor.execute("update {} set result=%s where domain=%s".format(self.table), val)
                self.mydb.commit()
                self.loggingFile(log_debug="{}".format("#####" * 20))
                self.loggingFile(log_debug="China API Check {} if accessible.".format(i[self.domain_field]), log_info=_result)
                if int(_result["dom_status"]) == 1:
                    rVal["data"].append({
                        "{#DOMAIN}": i[self.domain_field],
                        "{#IDC}": i[self.idc_field],
                        "{#CHINA}": i[self.china_field],
                        "{#RESULT}": int(_result["dom_status"])
                    }
                    )
        for i in rVal["data"]:
            try:
                dom_result = self.domainException(i["{#DOMAIN}"])
            except Exception as e:
                dom_result = "Domain Exception Error: {}".format(i["{#DOMAIN}"])
                print("Domain Exception Error: {}".format(str(e)))
            if dom_result:
                print("Dont Send Email: {}".format(i["{#DOMAIN}"]))
            else:
                print("Send Email: {}".format(i["{#DOMAIN}"]))
                _value = "Domain: {}\t\tIDC IP: {}\t\tCHINA IP: {}\t\t".format(i["{#DOMAIN}"], i["{#IDC}"], i["{#CHINA}"])
                _value2 = "Click here to verify: {}{}\n".format(chinadomain, i["{#DOMAIN}"])
                to_send.append(_value)
                to_send.append(_value2)
        email_subject = "Blocked Domains in China {}".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        if rVal["data"]:
            if len(to_send) == 0 and len(rVal["data"]) != 0:
                email_content = '''Hi All,

No New Blocked Domains this week.


'''
            else:
                email_content = '''Hi All,
            
These are the domains that are blocked by the Great Firewall of China. Kindly verify domain stability on https://17ce.com or https://boce.com or https://www.chaicp.com/home_cha/chaymqiang_z. Thanks


{}'''.format('\n'.join(to_send))
        else:
            email_content = '''Hi All,
            
All Domains are Normal and not blocked by the Great Firewall of China.
{}'''.format('\n'.join(to_send))
        #print(sendMail(['yroll.macalino@m1om.me'], email_subject, email_content))
        print(sendMail(['omgroup@m1om.me'], email_subject, email_content))



    def mysqlInsert(self):
        source = os.path.join(self.my_path, 'data.json')
        destination = os.path.join(self.my_path, 'logs/data-{}.json'.format(datetime.datetime.now().strftime("%Y-%m-%d")))
        rVal = {
            "data": []
        }
        g = greatChecker(DomainDNS().host, DomainDNS().user, DomainDNS().passwd, DomainDNS().database)
        mycursor = self.mydb.cursor()
        mycursor.execute("DELETE from {}".format(self.table))
        self.mydb.commit()
        self.loggingFile(log_debug="{}".format("#####" * 20))
        self.loggingFile(log_debug="MySQL Delete Table Data", log_info=str("DELETE FROM {}".format(self.table)))
        g.lezdodiz()


if __name__ == '__main__':
    try:
        if sys.argv[1] == "savedb":
            DomainDNS().mysqlInsert()
        elif sys.argv[1] == "sendemail":
            print(DomainDNS().mysqlSendMail())
        elif sys.argv[1] == "zabbixq":
            print(DomainDNS().mysqlZabbixQuery())
        elif sys.argv[1] == "testing":
            print(DomainDNS().mysqlZabbixQuery())
        else:
            print('''To save MYSQL use "python domaindns.py savedb" 
To Check Zabbix Monitoring "python domaindns.py zabbixq"
To Send Email "python domaindns.py sendemail"''')
    except Exception as e:
        print(str(e))
        print('''To save MYSQL use "python domaindns.py savedb"
To Check Zabbix Monitoring "python domaindns.py zabbixq"
To Send Email "python domaindns.py sendemail"''')

