from django.test import TestCase

# Create your tests here.
import json
import requests

# ####设备IP和申请的apiliscense的kye和passwd

#####登录的账号和密码
def create_conf_test():
    hostIP = '10.67.18.206'
    # oauth_consumer_key = 'JDB_M'
    oauth_consumer_key = 'TrueLink'
    oauth_consumer_secret = '12345678'
    username = '9999991000033'
    password = '888888'
    url_account_token = "http://%s/api/v1/system/token" % hostIP
    postdata_account_token = {
        "oauth_consumer_key": oauth_consumer_key,
        "oauth_consumer_secret": oauth_consumer_secret,
    }

    s = requests.Session()
    ret = s.post(url_account_token, data=postdata_account_token)
    account_token = json.loads(ret.text).get('account_token')
    print(account_token)

    url_get_cookie = "http://%s/api/v1/system/login" % hostIP
    postdata_get_cookie = {
        "password": password,
        "username": username,
        "account_token": account_token
    }

    ret = s.post(url_get_cookie, data=postdata_get_cookie)
    print(ret.text, ret.cookies)

    url_creat_meeting = "http://%s/api/v1/mc/confs" % hostIP
    meeting_tem_params = {
        "name": "test1",
        "conf_type": 0,
        "create_type": 1,
        "duration": 60,
        "bitrate": 1024,
        "closed_conf": 0,
        "safe_conf": 0,
        "encrypted_type": 0,
        "encrypted_auth": 0,
        "call_times": 0,
        "call_interval": 20,
        "password": "",
        "mute": 0,
        "silence": 0,
        "video_quality": 0,
        "dual_mode": 1,
        "voice_activity_detection": 0,
        "vacinterval": 0,
        "cascade_mode": 1,
        "cascade_upload": 1,
        "cascade_return": 0,
        "cascade_return_para": 0,
        "public_conf": 0,
        "vmp_enable": 0,
        "mix_enable": 1,
        "poll_enable": 0,
        "invited_mt_num": 1,
        "max_join_mt": 8,
        "creator": {
            "name": username,
            "account": "27752b1f-7009-464b-829b-ff2886607548",
            "account_type": 1,
            "telephone": ""
        },
        "chairman": {
            "name": username,
            "account": "27752b1f-7009-464b-829b-ff2886607548",
            "account_type": 1
        },
        "video_formats": [
            {
                "format": 5,
                "resolution": 12,
                "frame": 30,
                "bitrate": 1024
            },
            {
                "format": 0,
                "resolution": 0,
                "frame": 0,
                "bitrate": 0
            },
            {
                "format": 0,
                "resolution": 0,
                "frame": 0,
                "bitrate": 0
            },
            {
                "format": 0,
                "resolution": 0,
                "frame": 0,
                "bitrate": 0
            }
        ],
        "one_reforming": 0,
        "auto_end": 1,
        "preoccpuy_resource": 0,
        "mute_filter": 0,
        "fec_mode": 0,
        "doubleflow": 0
    }

    params = json.dumps(meeting_tem_params)

    postdata_create_meeting = {
        "account_token": account_token,
        "params": params
    }
    headers = {
        'Accept': 'application/json'
    }
    a = set()
    print(a, type(a))
    ret = s.post(url_creat_meeting,params=postdata_create_meeting, headers=headers)
    print(ret.text, ret.status_code)

    s.close()

if __name__ == '__main__':
    a = {1,2,3}
    b = {1,2,4,5}
    print(a & b)