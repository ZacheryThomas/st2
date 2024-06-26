# -*- coding: utf-8 -*-
# Copyright 2020 The StackStorm Authors.
# Copyright 2019 Extreme Networks, Inc.
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

"""
NOTE: This file is only used for backward compatibility tests with new dist_utils.py in
st2common/tests/unit/test_dist_utils.py.

DO NOT USE THIS FILE ANYWHERE ELSE!
"""

from __future__ import absolute_import

import os
import re
import sys

# NOTE: This script can't rely on any 3rd party dependency so we need to use this code here
PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
else:
    text_type = unicode  # noqa  # pylint: disable=E0602

GET_PIP = "curl https://bootstrap.pypa.io/get-pip.py | python"

try:
    from pip import __version__ as pip_version
except ImportError as e:
    print("Failed to import pip: %s" % (text_type(e)))
    print("")
    print("Download pip:\n%s" % (GET_PIP))
    sys.exit(1)

try:
    # pip < 10.0
    from pip.req import parse_requirements
except ImportError:
    # pip >= 10.0

    try:
        from pip._internal.req.req_file import parse_requirements
    except ImportError as e:
        print("Failed to import parse_requirements from pip: %s" % (text_type(e)))
        print("Using pip: %s" % (str(pip_version)))
        sys.exit(1)

__all__ = [
    "fetch_requirements",
    "apply_vagrant_workaround",
    "get_version_string",
    "parse_version_string",
]


def fetch_requirements(requirements_file_path):
    """
    Return a list of requirements and links by parsing the provided requirements file.
    """
    links = []
    reqs = []
    for req in parse_requirements(requirements_file_path, session=False):
        # Note: req.url was used before 9.0.0 and req.link is used in all the recent versions
        link = getattr(req, "link", getattr(req, "url", None))
        if link:
            links.append(str(link))
        reqs.append(str(req.req))
    return (reqs, links)


def apply_vagrant_workaround():
    """
    Function which detects if the script is being executed inside vagrant and if it is, it deletes
    "os.link" attribute.
    Note: Without this workaround, setup.py sdist will fail when running inside a shared directory
    (nfs / virtualbox shared folders).
    """
    if os.environ.get("USER", None) == "vagrant":
        del os.link


def get_version_string(init_file):
    """
    Read __version__ string for an init file.
    """

    with open(init_file, "r") as fp:
        content = fp.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)

        raise RuntimeError("Unable to find version string in %s." % (init_file))


# alias for get_version_string
parse_version_string = get_version_string
