""" LDAP Authentication Module"""
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
# https://ldap3.readthedocs.io/en/latest/bind.html
# https://github.com/dbunn/MS-AD-LDAP3-Python/blob/master/ms_ad_group_examples.py
def verify_AD(uname, password):
    """ Searches for the DN of a user

    @param uname: NCIWIN Username
    @param param2: NCIWIN Password
    @return: (login_status -> bool , distingushed_name -> str)

    Usage:
    >>> verify_AD('bbennichan', password)
    >>> (True, 'Bitto Bennichan')
    """
    # pylint: disable=invalid-name
    connected = False
    dn = None
    uname = uname.lower().replace('nciwin\\', '')
    uname_with_domain = 'NCIWIN\\' +  uname
    search_filter = "(&(objectclass=user)(!(objectclass=computer))(sAMAccountName=" + uname  + "))"
    search_base = 'dc=nciwin,dc=local'
    ms_ad_server = Server('uszu3adcpwv004.internal.cloudapp.net', get_info=ALL)
    ms_ad_conn = Connection(
        ms_ad_server,
        user=uname_with_domain,
        password=password,
        authentication=NTLM
    )

    if ms_ad_conn.bind():
        connected = True
        ms_ad_conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['cn'],
            size_limit=0
        )
        if(ms_ad_conn.entries and len(ms_ad_conn.entries) > 0):
            dn = str(ms_ad_conn.entries[0].cn)
    ms_ad_conn.unbind()
    return connected, dn
