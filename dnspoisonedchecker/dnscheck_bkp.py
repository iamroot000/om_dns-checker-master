import requests
import json
import mysql.connector

def dnspoisoned():

    mydb = mysql.connector.connect(
        host="10.167.11.205",
        user="yrollrei",
        passwd="s22-C350",
        database="argus_v2"
    )




    mycursor = mydb.cursor()
    mycursor.execute("SELECT domain FROM SSLDOMAINS_ssldomain2")
    domdom = mycursor.fetchall()


    

    for dom in domdom:

        try:
            domstr = ''.join(dom)
            # domstrl = "'" + domstr + "'"
            apikey = '024978650fb61a94b8dd683732ba75c9717b6297'
            url = 'https://api.viewdns.info/chinesefirewall/'
            # apikey = '6ca9d45c53dc9ff3405a6fc8d0a6f3a5d52b7431' #mine
            # apikey = '024978650fb61a94b8dd683732ba75c9717b6297' #office
            params = {
                'output': 'json',
                'domain': domstr,
                'apikey': apikey
            }
    
            res = dict();
            response = requests.get(url, params)
            rescon = json.dumps(response.json())
            result = json.loads(rescon)
            exp_res = result['expectedresponse']
            print(domstr)
            print("expected_result = " + exp_res)
            for r in result['response']['detail']['server']:
                res[r['location']] = r['resultvalue']
    
            print(res)
    
            val = (
            domstr, exp_res, res['Beijing'], res['Shenzhen'], res['Inner Mongolia'], res['Heilongjiang Province'],
            res['Yunnan Province'])
            sql = "INSERT INTO domain_dnspoisonedchecker(domain,expectedresponse,beijing,shenzhen,inner_mongolia,heilongjiang,yunnan) VALUES(%s, %s, %s, %s, %s, %s, %s)"
            mycursor.execute(sql,val)
            print(domstr)
            print("expected_result = " + exp_res)
            print(res)

        except Exception as e:
            val = (
                domstr, '---', '---', '---', '---', '---', '---')
            sql = "INSERT INTO domain_dnspoisonedchecker(domain,expectedresponse,beijing,shenzhen,inner_mongolia,heilongjiang,yunnan) VALUES(%s, %s, %s, %s, %s, %s, %s)"
            mycursor.execute(sql, val)
    
            print(sql)




    return True


if __name__=='__main__':
    print(dnspoisoned())


