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
    # TEST FOR GET_STATUS
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

    def _check_get_status_info(self, data, type, info, id_name):
        """generic funtionc to test get_status with additional info"""
        id = list(data[type].keys())[0]
        self.assertTrue(info in list(data[type][id].keys()))
        infos = data[type][id][info]
        self.assertTrue("key_toto" in list(infos.keys()))
        self.assertEqual(infos["key_toto"][id_name], id)
        self.assertEqual(infos["key_toto"]["key"], "key_toto")
        self.assertEqual(infos["key_toto"]["value"], "value_toto")

    #
    # DELETION TEST
    #

    def test_delete_groups(self):
        """Create a groups, check and try to delete it"""
        groups = self.imp.call("spv.services", "create_groups", "toto")
        self.groups.append(list(groups.keys()))
        self.assertEqual(
            len(
                self.imp.call(
                    "spv.services", "get_groups", {"group_id": list(groups.keys())[0]}
                )
            ),
            1,
        )
        self.imp.call("spv.services", "delete_groups", list(groups.keys()))
        self.assertEqual(
            len(
                self.imp.call(
                    "spv.services", "get_groups", {"group_id": list(groups.keys())[0]}
                )
            ),
            0,
        )

    def test_delete_checks(self):
        """Create a checks, check and try to delete it"""
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "a",
                    "plugin_check": "b",
                    "name": "c",
                    "repeat": 100,
                    "repeat_on_error": 100,
                }
            ],
        )
        self.checks.append(list(checks.keys()))
        self.assertEqual(
            len(
                self.imp.call(
                    "spv.services",
                    "get_plugin_checks",
                    {"check_id": list(checks.keys())[0]},
                )
            ),
            1,
        )
        self.imp.call("spv.services", "delete_checks", list(checks.keys()))
        self.assertEqual(
            len(
                self.imp.call(
                    "spv.services",
                    "get_plugin_checks",
                    {"check_id": list(checks.keys())[0]},
                )
            ),
            0,
        )

    def test_delete_objects(self):
        """Create a objects, check and try to delete it"""
        objects = self.imp.call("spv.services", "create_objects", [{"address": "toto"}])
        self.objects.append(list(objects.keys()))
        self.assertEqual(
            len(
                self.imp.call(
                    "spv.services", "get_objects", {"obj_id": list(objects.keys())[0]}
                )
            ),
            1,
        )
        self.imp.call("spv.services", "delete_objects", list(objects.keys()))
        self.assertEqual(
            len(
                self.imp.call(
                    "spv.services", "get_objects", {"obj_id": list(objects.keys())[0]}
                )
            ),
            0,
        )

    #
    # CREATE TEST
    #

    def test_create_group(self):
        """Test multiple group creation and returned values."""
        # FIXME: group names are currently not unique but should probably be
        # create
        groups = self.imp.call("spv.services", "create_groups", ["toto", "tata"])
        self.groups.append(list(groups.keys()))

        # test_returned_dict
        self.assertEqual(len(groups), 2)

        for group_id in list(groups.keys()):
            self.assertTrue(isinstance(group_id, int))
            self.assertTrue(len(groups[group_id]), 2)
            for valid_key in ("grp_id", "name"):
                self.assertTrue(valid_key in groups[group_id])

        self.assertFalse("errors" in groups)

    def test_create_checks(self):
        """Test multiple check creation and returned values."""
        # create
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "toto",
                    "plugin_check": "test1",
                    "name": "This is test 1",
                    "repeat": 10,
                    "repeat_on_error": 10,
                },
                {
                    "plugin": "toto",
                    "plugin_check": "test2",
                    "name": "This is test 2",
                    "repeat": 10,
                    "repeat_on_error": 10,
                    "infos": {"key1": "Value1", "key2": "Value2"},
                },
            ],
        )
        self.checks.append(list(checks.keys()))

        # test_returned_dict
        self.assertEqual(len(checks), 2)

        for check_id in list(checks.keys()):
            self.assertTrue(isinstance(check_id, int))
            self.assertTrue(len(checks[check_id]), 4)
            for valid_key in ("chk_id", "plugin", "plugin_check"):
                self.assertTrue(valid_key in checks[check_id])

        self.assertFalse("errors" in checks)

    def test_error_create_checks(self):
        """Create a wrong checks and test the failure"""
        # create
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "toto",
                    "plugin_check": "toto",
                    "name": "toto",
                    "repeat": 10,
                    "repeat_on_error": 10,
                },
                {
                    "plugin": "toto",
                    "plugin_check": "toto",
                    "name": "toto",
                    "repeat": 10,
                    "repeat_on_error": 10,
                },
            ],
        )
        key = [k for k in list(checks.keys()) if isinstance(k, int)]
        self.checks.append(key)
        self.assertTrue("errors" in list(checks.keys()))

    def test_create_objects(self):
        """Test multiple object creation and returned values."""
        # create
        objects = self.imp.call(
            "spv.services",
            "create_objects",
            [
                {"address": "toto"},
                {"address": "tata", "infos": {"key1": "Value1", "key2": "Value2"}},
            ],
        )
        self.objects.append(list(objects.keys()))

        # test_returned_dict
        self.assertEqual(len(objects), 2)
        for object_id in list(objects.keys()):
            self.assertTrue(isinstance(object_id, int))
            self.assertTrue(len(objects[object_id]), 2)
            for valid_key in ("obj_id", "address"):
                self.assertTrue(valid_key in objects[object_id])

        self.assertFalse("errors" in objects)

    def test_error_create_objects(self):
        """create a wrong objects and test the failure"""
        # create
        objects = self.imp.call(
            "spv.services", "create_objects", [{"address": "toto"}, {"address": "toto"}]
        )
        key = [k for k in list(objects.keys()) if isinstance(k, int)]
        self.objects.append(key)
        self.assertTrue("errors" in list(objects.keys()))

    # TODO: Set status infos

    #
    # GET TEST
    #

    def _get_test(self, params, data, api_func, test_func):
        """Generic test for test_get_* functions

        @params: list of key value for research in spv API
                [
                    [key, param], ...
                ]
        @data: value returned when create an groups/object/checks
        @api_func: function of the spv API to call
        @test_func: function to call to validate the call to api_func

        """
        for param, param_key in params:
            for key in list(data.keys()):
                ret = self.imp.call(
                    "spv.services", api_func, {param: data[key][param_key]}
                )
                test_func(ret, data, key)

        # check if the new entries that we create are in the global list
        all_groups = self.imp.call("spv.services", api_func)
        result_keys = [
            key for key in list(all_groups.keys()) if key in list(data.keys())
        ]
        self.assertEqual(len(result_keys), len(list(data.keys())))

    def test_get_groups(self):
        """Create groups and get it from spv with different filter"""
        groups = self.imp.call(
            "spv.services",
            "create_groups",
            ["test_list_group1", "test_list_group2", "test_list_group3"],
        )
        self.groups.append(list(groups.keys()))

        def test_result(ret, groups, key):
            self.assertEqual(ret[key]["id"], groups[key]["grp_id"])
            self.assertEqual(ret[key]["name"], groups[key]["name"])

        self._get_test(
            [["group_id", "grp_id"], ["group_name", "name"]],
            groups,
            "get_groups",
            test_result,
        )

    def test_get_objects(self):
        """Create objects and get it from spv with different filter"""
        objects = self.imp.call(
            "spv.services",
            "create_objects",
            [
                {"address": "test/get_objects/1"},
                {"address": "test/get_objects/2", "infos": {"key_toto": "toto"}},
            ],
        )
        self.objects.append(list(objects.keys()))

        def test_result(ret, objects, key):
            self.assertEqual(ret[key]["obj_id"], objects[key]["obj_id"])
            self.assertEqual(ret[key]["address"], objects[key]["address"])
            self.assertEqual(ret[key]["creation_date"], objects[key]["creation_date"])

        self._get_test(
            [
                ["obj_id", "obj_id"],
                ["address", "address"],
                ["creation_date", "creation_date"],
            ],
            objects,
            "get_objects",
            test_result,
        )

        keys = list(objects.keys())
        keys.sort()
        ret = self.imp.call("spv.services", "get_objects", {"info_key": "key_toto"})
        self.assertEqual(len(ret), 1)
        test_result(ret, objects, keys[1])

        ret = self.imp.call("spv.services", "get_objects", {"info_value": "toto"})
        self.assertEqual(len(ret), 1)
        test_result(ret, objects, keys[1])

        # check get multiple objects with on filter
        ret = self.imp.call(
            "spv.services",
            "get_objects",
            {"creation_date": objects[keys[0]]["creation_date"]},
        )
        result_keys = [key for key in list(ret.keys()) if key in keys]
        self.assertEqual(len(result_keys), 2)

    def test_get_checks(self):
        """Create checks and get it from spv with different filter"""
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "toto",
                    "plugin_check": "test1",
                    "name": "This is test 1",
                    "repeat": 10,
                    "repeat_on_error": 10,
                },
                {
                    "plugin": "toto",
                    "plugin_check": "test2",
                    "name": "This is test 2",
                    "repeat": 10,
                    "repeat_on_error": 10,
                    "infos": {"test_key_": "test_val_"},
                },
            ],
        )
        self.checks.append(list(checks.keys()))

        def test_result(ret, checks, key):
            self.assertEqual(ret[key]["chk_id"], checks[key]["chk_id"])
            self.assertEqual(ret[key]["plugin"], checks[key]["plugin"])
            self.assertEqual(ret[key]["plugin_check"], checks[key]["plugin_check"])

        self._get_test(
            [
                ["chk_id", "chk_id"],
                ["plugin", "plugin"],
                ["plugin_check", "plugin_check"],
            ],
            checks,
            "get_plugin_checks",
            test_result,
        )

        keys = list(checks.keys())
        keys.sort()
        ret = self.imp.call(
            "spv.services", "get_plugin_checks", {"info_key": "test_key_"}
        )
        self.assertEqual(len(ret), 1)
        test_result(ret, checks, keys[1])

        ret = self.imp.call(
            "spv.services", "get_plugin_checks", {"info_value": "test_val_"}
        )
        self.assertEqual(len(ret), 1)
        test_result(ret, checks, keys[1])

        # check get multiple checks with on filter
        ret = self.imp.call(
            "spv.services", "get_plugin_checks", {"plugin_name": "toto"}
        )
        self.assertEqual(len(ret), 2)

    #
    # UPDATE TEST
    #

    def test_update_groups(self):
        """Create group and update it"""
        groups = self.imp.call("spv.services", "create_groups", ["test_list_group1"])
        self.groups.append(list(groups.keys()))
        id = list(groups.keys())[0]
        ret = self.imp.call(
            "spv.services",
            "update",
            {"groups": {id: {"grp_id": id, "name": "name_update"}}},
        )
        ret = self.imp.call("spv.services", "get_groups", {"group_id": id})
        self.assertEqual(ret[id]["name"], "name_update")

    def test_update_checks(self):
        """Createecks and update it"""
        checks = self.imp.call(
            "spv.services",
            "create_checks",
            [
                {
                    "plugin": "toto",
                    "plugin_check": "test1",
                    "name": "test name",
                    "repeat": 10,
                    "repeat_on_error": 10,
                }
            ],
        )
        self.checks.append(list(checks.keys()))
        id = list(checks.keys())[0]
        ret = self.imp.call(
            "spv.services",
            "update",
            {
                "checks": {
                    id: {
                        "chk_id": id,
                        "name": "salut",
                        "plugin": "salut",
                        "plugin_check": "salut",
                        "repeat": 21,
                        "repeat_on_error": 2,
                    }
                }
            },
        )
        ret = self.imp.call("spv.services", "get_plugin_checks", {"check_id": id})
        self.assertEqual(ret[id]["name"], "salut")
        self.assertEqual(ret[id]["plugin"], "salut")
        self.assertEqual(ret[id]["plugin_check"], "salut")
        self.assertEqual(ret[id]["repeat"], 21)
        self.assertEqual(ret[id]["repeat_on_error"], 2)

    def test_update_objects(self):
        """Create object and update it"""
        objects = self.imp.call("spv.services", "create_objects", [{"address": "test"}])
        self.objects.append(list(objects.keys()))

        id = list(objects.keys())[0]
        ret = self.imp.call(
            "spv.services",
            "update",
            {"objects": {id: {"obj_id": id, "address": "test_update"}}},
        )
        ret = self.imp.call("spv.services", "get_objects", {"obj_id": id})
        self.assertEqual(ret[id]["address"], "test_update")


if __name__ == "__main__":
    # unittest.main()
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ServiceTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
