import json
import os
import re
import time
import base64
import kubernetes.client
import requests

from systest_utils import statics, Logger, TestUtil
from datetime import datetime, timezone

from systest_utils.wlid import Wlid

from tests_scripts.helm.base_relevant_cves import BaseRelevantCves

DEFAULT_BRANCH = "release"


# def is_accesstoken_credentials(credentials):
#     return 'username' in credentials and 'password' in credentials and credentials['username'] != '' and credentials[
#         'password'] != ''


class RelevantCVEs(BaseRelevantCves):
    def __init__(self, test_obj=None, backend=None, kubernetes_obj=None, test_driver=None):
        super(RelevantCVEs, self).__init__(test_driver=test_driver, test_obj=test_obj, backend=backend,
                                                    kubernetes_obj=kubernetes_obj)

    def start(self):
        cluster, namespace = self.setup(apply_services=False)

        # P1 install helm-chart (armo)
        # 1.1 add and update armo in repo
        Logger.logger.info('install armo helm-chart')
        self.add_and_upgrade_armo_to_repo()

        since_time = datetime.now(timezone.utc).astimezone().isoformat()

        # 1.2 install armo helm-chart
        self.install_armo_helm_chart(helm_kwargs=self.test_obj.get_arg("helm_kwargs", default={}))

        # 1.3 verify installation
        self.verify_running_pods(namespace=statics.CA_NAMESPACE_FROM_HELM_NAME, timeout=360)

        #P2 apply workload
        Logger.logger.info('apply services')
        self.apply_directory(path=self.test_obj[("services", None)], namespace=namespace)
        Logger.logger.info('apply config-maps')
        self.apply_directory(path=self.test_obj[("config_maps", None)], namespace=namespace)
        Logger.logger.info('apply workloads')
        workload_objs: list = self.apply_directory(path=self.test_obj["deployments"], namespace=namespace)
        self.verify_all_pods_are_running(namespace=namespace, workload=workload_objs, timeout=360)

        #P3 verify results in storage
        # 3 test SBOM and CVEs created as expected in the storage
        Logger.logger.info('Get the scan result from local Storage')
        # 3.1 test SBOM created in the storage
        SBOMs, _ = self.wait_for_report(timeout=1200, report_type=self.get_SBOM_from_storage, SBOMKeys=self.get_workloads_images_hash(workload_objs))
        # 3.2 test SBOM created as expected result in the storage
        self.validate_expected_SBOM(SBOMs, self.test_obj["expected_SBOMs"])
        # 3.3 test CVEs created in the storage
        CVEs, _ = self.wait_for_report(timeout=1200, report_type=self.get_CVEs_from_storage, CVEsKeys=self.get_workloads_images_hash(workload_objs))
        # 3.4 test CVES created as expected result in the storage
        self.validate_expected_CVEs(CVEs, self.test_obj["expected_CVEs"])
        # 3.5 test filtered SBOM created in the storage
        filteredSBOM, _ = self.wait_for_report(timeout=1200, report_type=self.get_filtered_SBOM_from_storage, filteredSBOMKeys=self.get_instance_IDs(pods=self.kubernetes_obj.get_namespaced_workloads(kind='Pod', namespace=namespace), namespace=namespace))
        # 3.6 test filtered CVEs created as expected result in the storage
        self.validate_expected_SBOM(filteredSBOM, self.test_obj["expected_filtered_SBOMs"])
        # 3.7 test filtered SBOM created in the storage
        Logger.logger.info('exposing operator (port-fwd)')
        self.expose_operator(cluster)

        self.send_vuln_scan_command(cluster=cluster, namespace=namespace)

        filteredCVEs, _ = self.wait_for_report(timeout=1200, report_type=self.get_filtered_CVEs_from_storage, filteredSBOMKEys=self.get_workloads_images_hash(workload_objs))
        # 3.8 test filtered CVEs created as expected result in the storage
        self.validate_expected_CVEs(filteredSBOM, self.test_obj["expected_filtered_CVEs"])

        # # P4 get CVEs results
        # # 4.1 get summary result
        Logger.logger.info('Get the scan result from Backend')
        expected_number_of_pods = self.get_expected_number_of_pods(
            namespace=namespace)
        be_summary, _ = self.wait_for_report(timeout=1200, report_type=self.backend.get_scan_results_sum_summary,
                                             namespace=namespace, since_time=since_time,
                                             expected_results=expected_number_of_pods)
        self.test_no_errors_in_scan_result(be_summary)

        # # 4.2 get container scan id
        containers_scan_id = self.get_container_scan_id(be_summary=be_summary)
        # # 4.3 get CVEs for containers

        self.test_backend_cve_against_storage_result(since_time=since_time, containers_scan_id=containers_scan_id, be_summary=be_summary, storage_CVEs={statics.ALL_CVES_KEY: CVEs, statics.FILTERED_CVES_KEY: filteredCVEs})

        Logger.logger.info('delete armo namespace')
        self.uninstall_armo_helm_chart()
        TestUtil.sleep(150, "Waiting for aggregation to end")

        Logger.logger.info("Deleting cluster from backend")
        self.delete_cluster_from_backend_and_tested()
        self.test_cluster_deleted(since_time=since_time)

        return self.cleanup()