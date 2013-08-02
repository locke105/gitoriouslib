# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Mathew Odden <locke105@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import re
import urllib

import httplib2


class Gitorious(object):

    def __init__(self, uri_base, email, passwd):
        # uri_base is something like http://gitorious.example.com
        # or if you are using HTTPS, https://secure.example.com
        self.gitorious_base_url = uri_base
        self.email = email
        self.passwd = passwd
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)
        self.auth_cookie = None

    def _parse_auth_token(self, content):
        tokens = re.findall(('input name="authenticity_token" '
                             'type="hidden" value="([\w\d/=+]+)"'), content)
        if len(tokens) == 1:
            return tokens[0]
        else:
            print content
            raise Exception("Authenticity token not found!")

    def _auth(self):
        login_url = self.gitorious_base_url + '/login'
        resp, content = self.http.request(login_url, 'GET')

        token = self._parse_auth_token(content)

        temp_cookie = resp['set-cookie']

        auth_data = dict(email=self.email, password=self.passwd)
        auth_data['authenticity_token'] = token
        auth_url = self.gitorious_base_url + '/sessions'
        auth_headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'text/html',
                        'Cookie': temp_cookie}
        resp, content = self.http.request(auth_url, 'POST',
                                          headers=auth_headers,
                                          body=urllib.urlencode(auth_data))

        self.auth_cookie = resp['set-cookie']

        if resp['status'][0] not in ('2', '3'):
            print resp
            print content
            raise Exception("Auth failed! Status code %s" % resp['status'])

    def create_repo(self, repo_name, project_name):
        if self.auth_cookie is None:
            self._auth()

        form_url = ('%s/%s/repositories/new' %
                    (self.gitorious_base_url, project_name))
        form_headers = {'Cookie': self.auth_cookie}
        resp, content = self.http.request(form_url, 'GET',
                                          headers=form_headers)

        token = self._parse_auth_token(content)

        create_url = ('%s/%s/repositories' %
                      (self.gitorious_base_url, project_name))
        create_headers = {'Content-type': 'application/x-www-form-urlencoded',
                          'Accept': 'application/json',
                          'Cookie': self.auth_cookie}
        create_data = {'repository[name]': repo_name,
                       'repository[description]': repo_name,
                       'repository[merge_requests_enabled]': 1,
                       'private_repository': 0,
                       'authenticity_token': token}
        resp, content = self.http.request(create_url, 'POST',
                                          headers=create_headers,
                                          body=urllib.urlencode(create_data))

        if resp['status'][0] not in ('2', '3'):
            print resp
            print content
            raise Exception("Request failed! Status code %s" % resp['status'])

    def delete_repo(self, repo_name, project_name):
        if self.auth_cookie is None:
            self._auth()

        form_url = ('%s/%s/%s/confirm_delete' %
                    (self.gitorious_base_url, project_name, repo_name))
        form_headers = {'Cookie': self.auth_cookie}
        resp, content = self.http.request(form_url, 'GET',
                                          headers=form_headers)

        token = self._parse_auth_token(content)

        delete_url = ('%s/%s/%s' %
                      (self.gitorious_base_url, project_name, repo_name))
        delete_headers = {'Content-type': 'application/x-www-form-urlencoded',
                          'Accept': 'application/json',
                          'Cookie': self.auth_cookie}
        delete_data = {'_method': 'delete',
                       'authenticity_token': token}
        resp, content = self.http.request(delete_url, 'POST',
                                          headers=delete_headers,
                                          body=urllib.urlencode(delete_data))

        if resp['status'][0] not in ('2', '3'):
            print resp
            print content
            raise Exception("Request failed! Status code %s" % resp['status'])