import requests
import socket
import json
import schedule
import time
from send import Send

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

def get_ip():
    try:
        ip = requests.get('https://ident.me').text.strip()
        return ip
    except:
        return None

def get_domain_ip(domain):
    try:
        address = socket.getaddrinfo(domain, None)
        return address[0][4][0]
    except Exception as e:
        return None

def getRecordID(subdomain):
    try:
        cred = credential.Credential("SecretId", "SecretKey")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)
        req = models.DescribeRecordListRequest()
        params = {
            "Domain": "YOUR DOMAIN",
            "RecordType": "A",
            "Keyword": subdomain
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeRecordList(req)
        # print(resp.to_json_string())
        return json.loads(str(resp))["RecordList"][0]["RecordId"]
    except TencentCloudSDKException as err:
        return None

def update(subdomain,ipaddress):
    try:
        cred = credential.Credential("SecretId", "SecretKey")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)
        req = models.ModifyRecordRequest()
        params = {
            "Domain": "YOUR DOMAIN",
            "SubDomain": subdomain,
            "RecordType": "A",
            "RecordLine": "默认",
            "Value": ipaddress,
            "TTL": 600,
            "RecordId": getRecordID(subdomain)
        }
        req.from_json_string(json.dumps(params))
        resp = client.ModifyRecord(req)
        # print(resp.to_json_string())
        if json.loads(str(resp))["RecordId"] == getRecordID(subdomain):
            return 'Updated'
    except TencentCloudSDKException as err:
        return None

def check():
    ip = get_ip()
    if ip != get_domain_ip('chanify.westwall.vip'):
        value = update('chanify',ip)
        if value != 'Updated':
            # 此处可配置你的Webhook
        else:
            with open ("./log", 'a+') as f:
                f.write(time.strftime('[%Y-%m-%d %H:%M:%S]') + "Updated to %s" % ip)
            f.close()
    else:
        pass

schedule.every(10).minutes.do(check)

while True:
    schedule.run_pending()
