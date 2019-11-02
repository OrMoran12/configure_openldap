import ldap
import ldap.modlist as modlist
import json

def ldap_connection(server_uri,admin_dn,admin_dn_pw):
    try:

        connection = ldap.initialize(server_uri)
    except:
        return "cant connect to " + server_uri
    connection.simple_bind_s(admin_dn,admin_dn_pw)
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

def create_user(ldap_connection,dn,attribute):
    ldif = modlist.addModlist(attribute)
    print(ldif)
    result = ldap_connection.add_s(dn,ldif)
    print(result)

con = ldap_connection('ldapi:///','cn=ldapadm,dc=or,dc=com','Aa123456!')
attrs = {}
attrs['objectclass'] = ['top', 'account', 'posixAccount', 'shadowAccount']
attrs['cn'] = 'User One'
attrs['uid'] = 'user1'
attrs['uidNumber'] = '3001'
attrs['gidNumber'] = '3000'
attrs['homeDirectory'] = '/home/user1'
attrs['loginShell'] = '/bin/bash'
attrs['description'] = 'Proud first user'
attrs['gecos'] = 'Via6, N#1010, 6th Avenue'
attrs['userPassword'] = 'iiit123'
attrs['shadowLastChange'] = '0'
attrs['shadowMax'] = '99999'
attrs['shadowWarning'] = '99999'
dn = "cn=test1,ou=people,dc=or,dc=com"
ldif = modlist.addModlist(attrs)


con.add_s(dn,ldif)
con.unbind()