#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Unit tests for webengine-spv-services. """

from importer import Importer
from pprint import pprint
import unittest


class ServiceTest(unittest.TestCase):
    def setUp(self):
        """Initialize test environment."""
        # TODO: clean up spvd database beforehand
        self.imp = Importer()
        self.imp["distant_url"] = "https://192.168.2.81/exporter/"
        self.groups = []
        self.checks = []
        self.objects = []

    def tearDown(self):
        """Clean up test environment."""
        groups = [grp_id for list_id in self.groups for grp_id in list_id]
        checks = [chk_id for list_id in self.checks for chk_id in list_id]
        objects = [obj_id for list_id in self.objects for obj_id in list_id]

        if groups:
            self.imp.call("spv.services", "delete_groups", groups)
        if checks:
            self.imp.call("spv.services", "delete_checks", checks)
        if objects:
            self.imp.call("spv.services", "delete_objects", objects)

    #
    # TEST FOR GET_CHECKS
    #

    def _get_status_tests_create_data(self):
        """Test create object,group,check for get_status tests"""
        groups = self.imp.call("spv.services", "create_groups", ["test_groups"])
        self.groups.append(list(groups.keys()))
        objects = self.imp.call(
            "spv.services",
            "create_objects",
            [
                {
                    "address": "test_address",
                    "infos": {"key_toto": "value_toto"},
                    "group_id": list(groups.keys())[0],
                }
            ],
        )
        self.objects.append(list(objects.keys()))
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "hey",
                    "plugin_check": "salut",
                    "name": "toi",
                    "repeat": 100,
                    "repeat_on_error": 100,
                    "infos": {"key_toto": "value_toto"},
                    "group_id": list(groups.keys())[0],
                }
            ],
        )
        self.checks.append(list(checks.keys()))
        return [groups, objects, checks]

    def _get_status_test_value(self, data, groups, objects, checks):
        keys = list(data.keys())
        keys.sort()
        self.assertTrue(keys == ["checks", "groups", "objects", "status"])
        self.assertTrue(data["checks"][list(checks.keys())[0]]["name"] == "toi")
        self.assertTrue(data["groups"][list(groups.keys())[0]]["name"] == "test_groups")
        self.assertTrue(
            data["objects"][list(objects.keys())[0]]["address"] == "test_address"
        )
        self.assertTrue(data["status"][0]["grp_id"] == list(groups.keys())[0])
        self.assertTrue(data["status"][0]["chk_id"] == list(checks.keys())[0])
        self.assertTrue(data["status"][0]["obj_id"] == list(objects.keys())[0])

    def test_get_status_check_status(self):
        """['get_checks'] Get every status with on specific status"""
        self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services", "get_checks", {"status": ["FINISHED", "ERROR"]}
        )
        for status in ret["status"]:
            self.assertTrue(status["check_status"] in ["FINISHED", "ERROR"])
        ret_finish = self.imp.call("spv.services", "get_checks", {"status": "FINISHED"})
        self.assertNotEqual(len(ret), 0)
        for status in ret_finish["status"]:
            self.assertEqual(status["check_status"], "FINISHED")
        len_error = len(
            self.imp.call("spv.services", "get_checks", {"status": "ERROR"})["status"]
        )
        self.assertEqual(len(ret["status"]), len(ret_finish["status"]) + len_error)

    def test_get_status_group_name(self):
        """['get_checks'] Get every status with on specific group_name"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"group_name": [list(groups.values())[0]["name"]]},
        )
        self._get_status_test_value(ret, groups, objects, checks)

    def test_get_status_object_address(self):
        """['get_checks'] Get every status with on specific object address"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"object_address": list(objects.values())[0]["address"]},
        )
        self._get_status_test_value(ret, groups, objects, checks)

    def test_get_status_plugin_name(self):
        """['get_checks'] Get every status with on specific plugin name"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"plugin_name": list(checks.values())[0]["plugin"]},
        )
        self._get_status_test_value(ret, groups, objects, checks)

    def test_get_status_plugin_check(self):
        """['get_checks'] Get every status with on specific plugin check"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"plugin_check": list(checks.values())[0]["plugin_check"]},
        )
        self._get_status_test_value(ret, groups, objects, checks)

    def test_get_status_group_id(self):
        """['get_checks'] Get every status with on specific groups_id"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services", "get_checks", {"group_id": list(groups.keys())[0]}
        )
        self._get_status_test_value(ret, groups, objects, checks)

    def test_get_status_check_id(self):
        """['get_checks'] Get every status with on specific check_id"""
        groups, objects, checks = self._get_status_tests_create_data()
        checks_second = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "1",
                    "plugin_check": "2",
                    "name": "3",
                    "repeat": 100,
                    "repeat_on_error": 100,
                    "group_id": list(groups.keys())[0],
                }
            ],
        )
        self.checks.append(list(checks_second.keys()))
        ret = self.imp.call(
            "spv.services", "get_checks", {"check_id": list(checks.keys())[0]}
        )
        self._get_status_test_value(ret, groups, objects, checks)

    def test_get_status_status_id(self):
        """['get_checks'] Get status with a additional info on status"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services", "get_checks", {"group_id": list(groups.keys())[0]}
        )
        ret_status = self.imp.call(
            "spv.services",
            "set_checks_status",
            [
                {
                    "status_id": ret["status"][0]["status_id"],
                    "sequence_id": 0,
                    "status": "coucou !",
                    "message": "salut",
                    "status_infos": {"key_status": "value_status"},
                }
            ],
        )
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"group_id": list(groups.keys())[0], "get_status_infos": True},
        )
        self.assertEqual(list(ret["status"][0]["status_infos"].keys()), ["key_status"])
        self.assertEqual(
            ret["status"][0]["status_infos"]["key_status"]["key"], "key_status"
        )
        self.assertEqual(
            ret["status"][0]["status_infos"]["key_status"]["value"], "value_status"
        )
        self.assertEqual(
            ret["status"][0]["status_infos"]["key_status"]["status_id"],
            ret["status"][0]["status_id"],
        )

    def test_get_status_limit(self):
        """['get_checks'] Get object/checks/grousp by group_id with a limit"""
        groups, objects, checks = self._get_status_tests_create_data()
        checks_second = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "1",
                    "plugin_check": "2",
                    "name": "3",
                    "repeat": 100,
                    "repeat_on_error": 100,
                    "group_id": list(groups.keys())[0],
                }
            ],
        )
        self.checks.append(list(checks_second.keys()))
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"group_id": list(groups.keys())[0], "limit": 1},
        )
        self.assertEqual(len(ret["checks"]), 1)
        ret = self.imp.call(
            "spv.services", "get_checks", {"group_id": list(groups.keys())[0]}
        )
        self.assertEqual(len(ret["checks"]), 2)

    def _check_get_status_info(self, data, type, info, id_name):
        """Generic funtionc to test get_status with additional info"""
        id = list(data[type].keys())[0]
        self.assertTrue(info in list(data[type][id].keys()))
        infos = data[type][id][info]
        self.assertTrue("key_toto" in list(infos.keys()))
        self.assertEqual(infos["key_toto"][id_name], id)
        self.assertEqual(infos["key_toto"]["key"], "key_toto")
        self.assertEqual(infos["key_toto"]["value"], "value_toto")

    def test_get_status_object_info(self):
        """['get_checks'] Get object with additional info"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"group_id": list(groups.keys())[0], "get_object_infos": True},
        )
        self._check_get_status_info(ret, "objects", "object_infos", "obj_id")

    def test_get_status_check_info(self):
        """['get_checks'] Get check with additional info"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {"group_id": list(groups.keys())[0], "get_check_infos": True},
        )
        self._check_get_status_info(ret, "checks", "check_infos", "chk_id")

    def test_get_status_detailed_infos(self):
        """['get_checks'] Test get_status  with 'get_detailed_infos' to False"""
        groups, objects, checks = self._get_status_tests_create_data()
        ret = self.imp.call(
            "spv.services",
            "get_checks",
            {
                "group_id": list(groups.keys())[0],
                "get_check_infos": True,
                "get_detailed_infos": False,
            },
        )
        self.assertEqual(
            ret["checks"][list(ret["checks"].keys())[0]]["check_infos"],
            {"key_toto": "value_toto"},
        )

    def test_get_checks_params_none(self):
        """['get_checks'] Test get_status with params not specified"""
        self._get_status_tests_create_data()
        ret = self.imp.call("spv.services", "get_checks", None)
        self.assertTrue(ret != None)

    #
    # CREATE TEST
    #

    def test_create_status(self):
        """['get_checks'] Test status creation and retrieval from various search criteria.

        Create a group, then check and object and assign them to previously
        create group in order to trigger status creation."""

        groups = self.imp.call("spv.services", "create_groups", ["test_group"])
        self.groups.append(list(groups.keys()))
        objects = self.imp.call(
            "spv.services",
            "create_objects",
            [{"address": "test_address", "group_id": list(groups.keys())[0]}],
        )
        self.objects.append(list(objects.keys()))
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "test_plugin",
                    "plugin_check": "check1",
                    "name": "Name of test check",
                    "repeat": 10,
                    "repeat_on_error": 10,
                    "group_id": list(groups.keys())[0],
                }
            ],
        )
        self.checks.append(list(checks.keys()))

        gets = {}
        gets[0] = self.imp.call(
            "spv.services", "get_checks", {"group_id": list(groups.keys())[0]}
        )
        gets[1] = self.imp.call(
            "spv.services", "get_checks", {"check_id": list(checks.keys())[0]}
        )
        gets[2] = self.imp.call(
            "spv.services",
            "get_checks",
            {"object_address": list(objects.values())[0]["address"]},
        )

        self.assertEqual(gets[0], gets[1])
        self.assertEqual(gets[1], gets[2])

    def test_update_check(self):
        """['get_checks'] Reschedule batch of/one status_id and check them/it."""
        self._get_status_tests_create_data()
        ret = self.imp.call("spv.services", "get_checks")

        id1 = ret["status"][0]["status_id"]
        id2 = ret["status"][1]["status_id"]
        id3 = ret["status"][2]["status_id"]

        ret = self.imp.call("spv.services", "get_checks", {"status_id": id1})
        id_first_check = ret["status"][0]["next_check"]
        self.imp.call("spv.services", "reschedule_check", [id1, id2, id3])
        ret = self.imp.call("spv.services", "get_checks", {"status_id": id1})
        id_second_check = ret["status"][0]["next_check"]
        self.imp.call("spv.services", "reschedule_check", (id3, id2, id1))
        ret = self.imp.call("spv.services", "get_checks", {"status_id": id1})
        id_third_check = ret["status"][0]["next_check"]

        self.assertTrue(
            id_first_check < id_second_check and id_second_check < id_third_check
        )

        ret = self.imp.call("spv.services", "get_checks", {"status_id": id1})
        id_first_check = ret["status"][0]["next_check"]
        self.imp.call("spv.services", "reschedule_check", id1)
        ret = self.imp.call("spv.services", "get_checks", {"status_id": id1})
        id_second_check = ret["status"][0]["next_check"]
        self.imp.call("spv.services", "reschedule_check", id1)
        ret = self.imp.call("spv.services", "get_checks", {"status_id": id1})
        id_third_check = ret["status"][0]["next_check"]

        self.assertTrue(
            id_first_check < id_second_check and id_second_check < id_third_check
        )


if __name__ == "__main__":
    # unittest.main()
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ServiceTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
