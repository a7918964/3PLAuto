import requests
import time
import json
from GlobalVar import *

'''Tote Registration in TPL system'''


def __TPLCMSlogin__():
    LoginAPI = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/sso/login'
    Account = {
        "username": "MIX.TestAdmin1",
        "password": "1qaz@WSX"
    }
    LoginResponse = requests.post(LoginAPI, json=Account).json()
    token = LoginResponse['data']['roles']
    for system in token:
        if system['system'] == 'MOX':
            MOXtoken = system['token']
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `MOXtoken` = '{MOXtoken}' WHERE ID = 1")
        elif system['system'] == "MIX":
            MIXtoken = system['token']
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `MIXtoken` = '{MIXtoken}' WHERE ID = 1")
        elif system['system'] == "TPLRS":
            TPLtoken = system['token']
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `TPLtoken` = '{TPLtoken}' WHERE ID = 1")
    conn.commit()
    print("TPLCMS login success")


'''Please input how much tote you want to generate'''


def __NewToteRegistration__(TY11=0, TY12=0, TY14=0):
    cur.execute("SELECT MIXtoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MIXtoken = Result[0]
    TotalTotes = TY11 + TY12 + TY14
    RegistrationURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes'
    headers = {'Authorization': f'Bearer {MIXtoken}'}
    GenerateTote = {
        "ty11": TY11,
        "ty12": TY12,
        "ty14": TY14
    }
    RegistrationResponse = requests.post(
        RegistrationURL, json=GenerateTote, headers=headers)
    if RegistrationResponse.status_code == 200:
        print("Generate tote : " + RegistrationResponse.json()['message'])
        retry = 0
        while True:
            ToteRecordURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes/history?pageNo=1&pageSize=10&'
            ToteRecordResponse = requests.get(
                ToteRecordURL, headers=headers).json()
            registerTote = ToteRecordResponse['data']['list'][0]['toteCode']
            if len(registerTote) == TotalTotes or retry > 3:
                break
            else:
                retry += 1
                print("Get wrong generate tote record , retry...")
        ToteList_str = json.dumps(
            __SingleRegisterTote__(registerTote, headers))
        cur.execute(
            f"UPDATE `Var_3PL_Table` SET `NewRegisterToteList` = ? WHERE ID = 1", (ToteList_str,))
        conn.commit()
    else:
        print(RegistrationResponse.json()['message'])
    time.sleep(2)
    return registerTote


def __SingleRegisterTote__(ToteList, headers):
    print("Single tote registration...")
    for tote in ToteList:
        SingleRegistrationURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes/{tote}'
        requests.put(SingleRegistrationURL, headers=headers)
    print(ToteList)
    return ToteList
