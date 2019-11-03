import ldap
import ldap.modlist as modlist
import json,random
from ansible.module_utils.basic import *


def ldap_connection(server_uri,admin_dn,admin_dn_pw):
    try:
        connection = ldap.initialize(server_uri)
    except:
        print(json.dumps({
            "msg":"cant connect to " + server_uri
        }))
        exit(1)
    try:
        connection.simple_bind_s(admin_dn,admin_dn_pw)
    except:
        print(json.dumps({
            "msg": "Wrong  credential"
        }))
        exit(1)
    return connection

def search_ldap(ldap_connection,cn,search_base):
    base = search_base
    scope = ldap.SCOPE_ONELEVEL
    search_filter = cn
    attr = ['*']
    result = ldap_connection.search_s(
        base,
        scope,
        search_filter,
        attr
    )
    return result

def build_user_info(result):
    attr_dict = {"dn": "", "data": ""}
    attr_dict["dn"] = str(result[0])
    attr_dict["data"] = result[1]
    for data in attr_dict["data"]:
        attr_dict["data"][data] = attr_dict["data"][data][0].decode('utf-8')
    return attr_dict

def create_user(ldap_connection,dn,attribute):
    ldif = modlist.addModlist(attribute)
    try:
        ldap_connection.add_s(dn,ldif)
    except:
        print(json.dumps({
            "msg":"There was a problem adding the user"
        }))
        exit(1)
    print(json.dumps({
        "msg": "The user " + dn + " was added successfully"
    }))

def main():
    user_attr = {
        "name":"",
        "group":"",
        "password":"",
        "homedir":""
    }
    module=AnsibleModule(
        argument_spec={
            'dn': dict(required=True),
            'base': dict(required=True),
            'state': dict(default=None, choices=['present']),
            'server_uri': dict(default='ldapi:///'),
            'attribute': dict(default= user_attr),
            'admin_bind_dn': dict(default=None),
            'admin_bind_pw': dict(default='', no_log=True),
                }

            )
    dn = module.params['dn']
    base = module.params['base']
    state = module.params['state']
    server_uri = module.params['server_uri']
    admin_bind_dn = module.params['admin_bind_dn']
    admin_bind_pw = module.params['admin_bind_pw']

    conn = ldap_connection(server_uri,admin_bind_dn,admin_bind_pw)
    if state == None:
        result = search_ldap(conn, dn , base)
        if result == []:
            print(json.dumps(
                {
                  "msg":"user not found "
                }
            ))
        else:
            dict_array = []
            for res in result:
                dict_array.append(build_user_info(res))
            print(json.dumps(
                {
                    "msg":"user found",
                    "all_result": dict_array,
                }
            ))

    else:
        attrs = module.params["attribute"]
        if attrs["name"] == "" or attrs["group"] == "" or attrs["password"] == "" or attrs["homedir"]:
            print (json.dumps(
                {
                    "msg": "when state is present you must insert the name,group,password and home dir of the user",

                }
            ))
            exit(1)
        else:
            uid = random.randint(100, 100000)
            attrs = {}
            attrs['objectclass'] = [bytes('top', 'utf-8'), bytes('account', 'utf-8'), bytes('posixAccount', 'utf-8'),
                                    bytes('shadowAccount', 'utf-8')]
            attrs['cn'] = bytes(attribute['name'], 'utf-8')
            attrs['uid'] = bytes(str(uid), 'utf-8')
            attrs['uidNumber'] = bytes(str(uid), 'utf-8')
            attrs['gidNumber'] = bytes(str(uid), 'utf-8')
            attrs['homeDirectory'] = bytes(attribute['homedir'], 'utf-8')
            attrs['loginShell'] = bytes('/bin/bash', 'utf-8')
            attrs['userPassword'] = bytes(attribute['password'], 'utf-8')
            attrs['shadowLastChange'] = bytes('0', 'utf-8')
            attrs['shadowMax'] = bytes('99999', 'utf-8')
            attrs['shadowWarning'] = bytes('99999', 'utf-8')
            user_dn = "cn=" + user_attr["name"] + ",ou=people," + base
            create_user(conn,user_dn,attrs)
    conn.unbind()
if __name__ == '__main__':
    main()
