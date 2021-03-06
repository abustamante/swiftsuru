import swiftclient
from swiftsuru.conf import AUTH_URL, USER, KEY


class SwiftClient(object):
    """
    python-swiftclient abstraction.
    This class authenticates the user and stores an authenticated connection
    with Swift's server.
    It also abstracts swiftclient actions, so you don't have to store the connection
    yourself or perform the actions on top of it, for example, what could be:
        cli = SwiftClient() # do some dirty work for you
        cli.conn.post_account(<...>)
    This is kind of ugly, to make it cleaner we abstract the connection for you, e.g:
        cli = SwiftClient()
        cli.create_account(<...>) # much better!
    """

    def __init__(self, keystone_conn=None):
        """
        Authenticates on swift with AUTH_URL, USER, and KEY from conf.py.
        Gets auth information for next API calls via conn.get_auth() and
        a authenticated client connection for performing actions.
        """
        if keystone_conn:
            token = keystone_conn.conn.auth_token
            endpoints = keystone_conn.get_storage_endpoints()
            url = endpoints['adminURL']

            self.conn = swiftclient.client.Connection(preauthurl=url, preauthtoken=token, insecure=True)
        else:
            conn = swiftclient.client.Connection(authurl=AUTH_URL, user=USER, key=KEY)
            auth_url, auth_token = conn.get_auth()
            self.conn = swiftclient.client.Connection(preauthurl=auth_url, preauthtoken=auth_token)

    def create_account(self, headers):
        self.conn.post_account(headers)

    def remove_account(self, subject):
        self.conn.post_account({"X-Remove-Account-Meta-Subject": subject})

    def account_containers(self):
        """
        Returns a list of existing containers for a given account.
        Now this account is on conf.py, but it should be given by __init__ method
        """
        return self.conn.get_account()[1]

    def create_container(self, name, headers):
        self.conn.put_container(name, headers)

    def remove_container(self, name, headers):
        self.conn.post_container(name, headers)

    def set_cors(self, container, url, append=True):
        if append:
            cors_urls = self.get_cors(container)
            url = '{} {}'.format(cors_urls, url).strip()

        headers = {'X-Container-Meta-Access-Control-Allow-Origin': url}
        self.conn.post_container(container, headers)

    def unset_cors(self, container, url):
        cors_urls = self.get_cors(container)
        new_cors_urls = cors_urls.replace(url, '').strip()

        headers = {'X-Container-Meta-Access-Control-Allow-Origin': new_cors_urls}
        self.conn.post_container(container, headers)

    def get_cors(self, container):
        headers = self.conn.head_container(container)
        cors_header = 'x-container-meta-access-control-allow-origin'

        return headers.get(cors_header, '')
