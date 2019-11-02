import ldap
import ldap.modlist as modlist
import json
from ansible.module_utils.basic import *


def ldap_connection(server_uri,admin_dn,admin_dn_pw):
    try:
        connection = ldap.initialize(server_uri)
    except:
        print ("cant connect to " + server_uri)
        exit(1)
    try:
        connection.simple_bind_s(admin_dn,admin_dn_pw)
    except:
        print("Wrong  credential")
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
    attr_dict = {"dn":"","data":""}
    attr_dict["dn"] = result[0]
    attr_dict["data"] = result[1]
    return attr_dict

def create_user(ldap_connection,dn,attribute):
    ldif = modlist.addModlist(attribute)
    result = ldap_connection.add_s(dn,ldif)

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
            'base_search': dict(required=True),
            'state': dict(default=None, choices=['present']),
            'server_uri': dict(default='ldapi:///'),
            'attribute': dict(default= user_attr),
            'admin_bind_dn': dict(default=None),
            'admin_bind_pw': dict(default='', no_log=True),
                }

            )
    dn = module.params['dn']
    base = module.params['base_search']
    state = module.params['state']
    server_uri = module.params['server_uri']
    admin_bind_dn = module.params['admin_bind_dn']
    admin_bind_pw = module.params['admin_bind_pw']

    conn = ldap_connection(server_uri,admin_bind_dn,admin_bind_pw)
    if state == None:
        result = search_ldap(conn, dn , base)
        if result == []:
            json.loads(
                {
                  "msg":"user not found "
                }
            )
        else:
            dict_array = []
            for res in result:
                dict_array += build_user_info(res)
                json.loads(
                    {
                        "msg":"user found",
                        "all_result": dict_array
                    }
                )

    else:
        attrs = module.params["attribute"]
        if attrs["name"] == "" or attrs["group"] == "" or attrs["password"] == "" or attrs["homedir"]:
            module.fail_json(
                {
                    "msg": "when state is present you must insert the name,group,password and home dir of the user",

                }
            )

    conn.unbind()








