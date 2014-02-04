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
import xml.etree.ElementTree as ET

import httplib2


class Gitorious(object):

    def __init__(self, base_url, email, passwd):
        # base_url is something like http://gitorious.example.com
        # or if you are using HTTPS, https://secure.example.com
        self.gitorious_base_url = base_url
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

        self._verify_response(resp)

    def _verify_response(self, response):
        if response['status'][0] not in ('2', '3'):
            print response
            raise Exception("Request failed! Status code %s" %
                            response['status'])

    def _ensure_auth(self):
        if self.auth_cookie is None:
            self._auth()

    def _fetch_repo_xml(self, repo_name, project_name):
        self._ensure_auth()

        repo_data_url = ('%s/%s/%s.xml' %
                         (self.gitorious_base_url, project_name, repo_name))
        headers = {'Cookie': self.auth_cookie}
        resp, content = self.http.request(repo_data_url, 'GET',
                                          headers=headers)
        self._verify_response(resp)
        return content

    def get_repo_info(self, repo_name, project_name):
        repo_data = self._fetch_repo_xml(repo_name, project_name)
        repo_tree = ET.fromstring(repo_data)
        repo = {}
        for child in repo_tree:
            repo[child.tag] = child.text

        return repo

    def _fetch_project_xml(self, project_name):
        self._ensure_auth()

        repo_data_url = ('%s/%s.xml' %
                         (self.gitorious_base_url, project_name))
        headers = {'Cookie': self.auth_cookie}
        resp, content = self.http.request(repo_data_url, 'GET',
                                          headers=headers)
        self._verify_response(resp)
        return content

    def list_repos(self, project_name):
        project_data = self._fetch_project_xml(project_name)
        proj_tree = ET.fromstring(project_data)
        repo_nodes = proj_tree.findall('./repositories/mainlines/repository')
        repositories = []
        for repo_node in repo_nodes:
            repo = {}
            for child in repo_node:
                repo[child.tag] = child.text
            repositories.append(repo)

        return repositories

    def create_repo(self, repo_name, project_name, private_repo=False):
        self._ensure_auth()

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
                       'authenticity_token': token}
        if private_repo:
            create_data['private_repository'] = 1
        resp, content = self.http.request(create_url, 'POST',
                                          headers=create_headers,
                                          body=urllib.urlencode(create_data))

        self._verify_response(resp)


    def delete_repo(self, repo_name, project_name):
        self._ensure_auth()

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

        self._verify_response(resp)
