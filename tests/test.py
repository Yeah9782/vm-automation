import support_functions
import vm_functions
import unittest

version_good = "7.0.4r154605"
vm_good = "ws2019"
vm_bad = "bad"
snapshot_good = "live"
snapshot_bad = "bad"
file_good = "./firefox.exe"
file_bad = "./bad.exe"
file_dst = "C:\\windows\\temp\\file.exe"
user_good = "Administrator"
pass_good = "12345678"
user_bad = "bad"
pass_bad = "bad"
ips_good = ["10.0.2.15", "192.168.56.113"]


class TestStringMethods(unittest.TestCase):
    # vm_functions options
    vm_functions.logging.disable()
    vm_functions.vboxmanage_path = "vboxmanage"
    vm_functions.timeout = 60

    def test01_file_info(self):
        result = support_functions.file_info(file_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1],"f2d2638afb528c7476c9ee8e83ddb20e686b0b05f53f2f966fd9eb962427f8aa",)
        self.assertEqual(result[2], "374fb48a959a96ce92ae0e4346763293")
        self.assertEqual(result[3], 1070)

    def test02_file_info_nonexisted(self):
        result = support_functions.file_info(file_bad)
        self.assertEqual(result, 1)

    def test03_virtualbox_version(self):
        result = vm_functions.virtualbox_version()
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], version_good)
        self.assertEqual(result[2], "")

    def test04_vm_start(self):
        vm_functions.vm_stop(vm_good)
        result = vm_functions.vm_start(vm_good)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], f'VM "{vm_good}" has been successfully started.')
        self.assertEqual(result[2], "")

    def test05_vm_start_running(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_start(vm_good)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "is already locked by a session")

    def test06_vm_start_nonexisting(self):
        result = vm_functions.vm_start(vm_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "Could not find a registered machine")

    def test07_vm_upload(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_upload(vm_good, user_good, pass_good, file_good, file_dst)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], "")
        self.assertEqual(result[2], "")

    def test08_vm_upload_nonexisting_file(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_upload(vm_good, user_good, pass_good, file_bad, file_dst)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "VERR_FILE_NOT_FOUND")

    def test09_vm_upload_incorrect_credentials(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_upload(vm_good, user_bad, pass_bad, file_good, file_dst)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "The specified user was not able to logon on guest")

    def test10_vm_download_incorrect_credentials(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_download(vm_good, user_good, pass_bad, file_bad, file_dst)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "The specified user was not able to logon on guest")

    def test11_vm_download_nonexisting_file(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_download(vm_good, user_good, pass_good, file_dst, file_bad)
        vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "Querying guest file information failed")

    def test12_vm_stop(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "100%")

    def test13_vm_stop_stopped(self):
        vm_functions.vm_stop(vm_good)
        result = vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "VBOX_E_INVALID_VM_STATE")

    def test14_vm_snapshot_restore_good(self):
        result = vm_functions.vm_snapshot_restore(vm_good, snapshot_good)
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], "Restoring snapshot")
        self.assertRegex(result[2], "100%")

    def test15_vm_snapshot_restore_nonexisting_a(self):
        result = vm_functions.vm_snapshot_restore(vm_good, snapshot_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "Could not find a snapshot")

    def test16_vm_snapshot_restore_nonexisting_b(self):
        result = vm_functions.vm_snapshot_restore(vm_bad, snapshot_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "")
        self.assertRegex(result[2], "Could not find a registered machine")

    def test17_list_ips(self):
        vm_functions.vm_start(vm_good)
        result = vm_functions.list_ips(vm_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], ips_good)
        self.assertEqual(result[2], "")


if __name__ == "__main__":
    unittest.main()
