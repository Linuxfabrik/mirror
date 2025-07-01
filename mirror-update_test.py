import unittest

class TestCommandBuilder(unittest.TestCase):
    def test_add_delete_flag_if_not_explicitly_disabled(self):
        target_path = "/test/"
        repo = {
            "repoid": "test"
        }

        cmd_args = "--assumeyes --download-metadata --download-path='{TARGET_PATH}' --downloadcomps --newest-only --norepopath --repoid='{REPOID}'".format(
            REPOID=repo["repoid"],
            TARGET_PATH=target_path,
        )

        if "keep_old_rpms" not in repo or repo["keep_old_rpms"] == False:
            cmd_args = cmd_args + " --delete"

        cmd = "reposync {CMD_ARGS}".format(
            CMD_ARGS=cmd_args,
        )

        self.assertEqual(cmd, "reposync --assumeyes --download-metadata --download-path='{TARGET_PATH}' --downloadcomps --newest-only --norepopath --repoid='{REPOID}' --delete".format(
            REPOID=repo["repoid"],
            TARGET_PATH=target_path,
        ))

    def test_ignore_delete_flag_if_disabled(self):
        target_path = "/test/"
        repo = {
            "repoid": "test",
            "keep_old_rpms": True
        }

        cmd_args = "--assumeyes --download-metadata --download-path='{TARGET_PATH}' --downloadcomps --newest-only --norepopath --repoid='{REPOID}'".format(
            REPOID=repo["repoid"],
            TARGET_PATH=target_path,
        )

        if "keep_old_rpms" not in repo or repo["keep_old_rpms"] == False:
            cmd_args = cmd_args + " --delete"

        cmd = "reposync {CMD_ARGS}".format(
            CMD_ARGS=cmd_args,
        )

        self.assertEqual(cmd, "reposync --assumeyes --download-metadata --download-path='{TARGET_PATH}' --downloadcomps --newest-only --norepopath --repoid='{REPOID}'".format(
            REPOID=repo["repoid"],
            TARGET_PATH=target_path,
        ))
