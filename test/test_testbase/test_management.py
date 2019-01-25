# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making QTA available.
# Copyright (C) 2016THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the BSD 3-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
#
"""testcase for management
"""

import multiprocessing
import os
import shlex
import shutil
import unittest

from testbase.management import RunTest
from testbase.runner import runner_types
from testbase.report import report_types
from testbase.util import get_time_str


class RuntestTest(unittest.TestCase):
    """
    """

    def test_args_parsing(self):
        cmdline = "-w working_dir xxxx oooo.test".split()
        args = RunTest.parser.parse_args(cmdline)
        self.assertEqual(args.working_dir, "working_dir")
        self.assertEqual(args.tests, ["xxxx", "oooo.test"])

        cmdline = "--status Ready --status Design --priority BVT --priority High --priority Normal" \
                  " --tag xxx --tag ooo --excluded-tag aaa --excluded-tag bbb" \
                  " --owner apple --owner banana xxxx".split()
        args = RunTest.parser.parse_args(cmdline)
        self.assertEqual(args.status, ["Ready", "Design"])
        self.assertEqual(args.priorities, ["BVT", "High", "Normal"])
        self.assertEqual(args.tags, ["xxx", "ooo"])
        self.assertEqual(args.excluded_tags, ["aaa", "bbb"])
        self.assertEqual(args.owners, ["apple", "banana"])
        self.assertEqual(args.tests, ["xxxx"])

    def test_report_args_parsing(self):
        cmdline = 'xxxx --report-type stream --report-args "--no-output-result --no-summary"'
        cmdline = shlex.split(cmdline)
        args = RunTest.parser.parse_args(cmdline)
        report_type = report_types[args.report_type]
        report_type.parse_args(shlex.split(args.report_args))

        output_file = "json_report.json"
        cmdline = 'xxxx --report-type json --report-args "--output %s"' % output_file
        cmdline = shlex.split(cmdline)
        args = RunTest.parser.parse_args(cmdline)
        report_type = report_types[args.report_type]
        report_type.parse_args(shlex.split(args.report_args))
        if os.path.exists(output_file):
            os.remove(output_file)

    def test_runner_args_parsing(self):
        test_pairs = [
                   ('xxxx --runner-type basic --runner-args "--retries 3"', 1),
                   ('xxxx --runner-type multithread --runner-args "--retries 3 --concurrency 0"', multiprocessing.cpu_count()),
                   ('xxxx --runner-type multiprocess --runner-args "--retries 3 --concurrency 3"', 3)
                   ]
        for cmdline, concurrency in test_pairs:
            args = RunTest.parser.parse_args(shlex.split(cmdline))
            runner_type = runner_types[args.runner_type]
            runner = runner_type.parse_args(shlex.split(args.runner_args), None, None)
            self.assertEqual(getattr(runner, "concurrency", 1), concurrency)

    def test_failed_returncode(self):
        working_dir = "test_online_report_%s" % get_time_str()
        cmdline = '--report-type html test.sampletest.hellotest.FailedCase'
        cmdline += " -w " + working_dir
        self.addCleanup(shutil.rmtree, working_dir, ignore_errors=True)
        args = RunTest.parser.parse_args(cmdline.split())
        proc = multiprocessing.Process(target=RunTest().execute, args=(args,))
        proc.start()
        proc.join()
        self.assertEqual(proc.exitcode, 1)

    def test_success_returncode(self):
        working_dir = "test_online_report_%s" % get_time_str()
        cmdline = '--report-type html test.sampletest.hellotest.PassedCase'
        cmdline += " -w " + working_dir
        self.addCleanup(shutil.rmtree, working_dir, ignore_errors=True)
        args = RunTest.parser.parse_args(cmdline.split())
        proc = multiprocessing.Process(target=RunTest().execute, args=(args,))
        proc.start()
        proc.join()
        self.assertEqual(proc.exitcode, 0)


if __name__ == "__main__":
    unittest.main(defaultTest="RuntestTest.test_failed_returncode")
