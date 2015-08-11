#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



import forester
import requests
import sys

from forester import errors
from forester.scm import wms
from testrunner import testcase
from testutils import mock

class WmsTest(testcase.TestCase):
    def setUp(self):
        testcase.TestCase.setUp(self)
        mock.mock(requests, 'get')
        self.base = 'http://example.com'
        self.path = 'scc/foo'

    def testFetch200ReturnsText(self):
        response = mock.MockObject()
        url='http://example.com/api/repos/scc/foo/poll/bar'
        response_text = u'text'
        response._mock.set(url=url, 
                status_code=200,
                raise_for_status=lambda: None,
                text=response_text,
                )
        requests.get._mock.setReturn(response, url)
        repo = wms.WmsRepository(self.base, self.path, branch='bar')

        text = repo.fetch('http://example.com/api/repos/scc/foo/poll/bar')

        self.assertEqual(text, response_text)

    def testFetch404RaisesError(self):
        response = mock.MockObject()
        url='http://example.com/api/repos/scc/foo/poll/bar'
        status_code=404
        response_text = u'text'
        def raisesWmsError():
            raise errors.ForesterWmsError(url, status_code)
        response._mock.set(url=url, status_code=status_code,
                raise_for_status=raisesWmsError, text=response_text,
                )
        requests.get._mock.setReturn(response, url)
        repo = wms.WmsRepository(self.base, self.path, branch='bar')

        err = self.assertRaises(errors.ForesterWmsError,
                             repo.fetch, url)

        self.assertEqual(err.url, url)
        self.assertEqual(err.status_code, status_code)


