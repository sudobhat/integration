#!/usr/bin/python
# Copyright 2017 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from fabric.api import *
import pytest

from .. import conftest
from ..common import *
from ..common_setup import standard_setup_with_signed_artifact_client
from .common_update import update_image_successful, common_update_procedure
from ..MenderAPI import auth_v2, deploy
from .mendertesting import MenderTesting

@MenderTesting.fast
class TestSignedUpdates(MenderTesting):
    """
        Signed artifacts are well tested in the client's acceptance tests, so
        we will only test basic backend integration with signed images here.
    """

    def test_signed_artifact_success(self, standard_setup_with_signed_artifact_client):

        mender_clients = standard_setup_with_signed_artifact_client.get_mender_clients()

        if not env.host_string:
            execute(self.test_signed_artifact_success,
                    standard_setup_with_signed_artifact_client,
                    hosts=mender_clients)
            return

        host_ip = standard_setup_with_signed_artifact_client.get_virtual_network_host_ip()
        update_image_successful(host_ip, install_image=conftest.get_valid_image(), signed=True)

    @pytest.mark.parametrize("standard_setup_with_signed_artifact_client", ["force_new"], indirect=True)
    def test_unsigned_artifact_fails_deployment(self, standard_setup_with_signed_artifact_client):
        """
            Make sure that an unsigned image fails, and is handled by the backend.
            Notice that this test needs a fresh new version of the backend, since
            we installed a signed image earlier without a verification key in mender.conf
        """

        mender_clients = standard_setup_with_signed_artifact_client.get_mender_clients()

        if not env.host_string:
            execute(self.test_unsigned_artifact_fails_deployment,
                    standard_setup_with_signed_artifact_client,
                    hosts=mender_clients)
            return

        deployment_id, _ = common_update_procedure(install_image=conftest.get_valid_image())
        deploy.check_expected_status("finished", deployment_id)
        deploy.check_expected_statistics(deployment_id, "failure", 1)

        for d in auth_v2.get_devices():
            assert "expecting signed artifact, but no signature file found" in \
                deploy.get_logs(d["id"], deployment_id)
