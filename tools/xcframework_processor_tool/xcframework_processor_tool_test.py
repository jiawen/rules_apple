# Copyright 2022 The Bazel Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for xcframework_processor_tool."""

import os
import plistlib
import tempfile
import unittest

from build_bazel_rules_apple.tools.xcframework_processor_tool import xcframework_processor_tool


_MOCK_XCFRAMEWORK_INFO_PLIST = {
    "AvailableLibraries": [
        {
            "LibraryIdentifier": "ios-arm64",
            "LibraryPath": "MyFramework.framework",
            "SupportedArchitectures": ["arm64"],
            "SupportedPlatform": "ios"
        },
        {
            "LibraryIdentifier": "ios-arm64_x86_64-simulator",
            "LibraryPath": "MyFramework.framework",
            "SupportedArchitectures": ["arm64", "x86_64"],
            "SupportedPlatform": "ios",
            "SupportedPlatformVariant": "simulator"
        },
        {
            "LibraryIdentifier": "watchos-x86_64-simulator",
            "LibraryPath": "MyFramework.framework",
            "SupportedArchitectures": ["x86_64"],
            "SupportedPlatform": "watchos",
            "SupportedPlatformVariant": "simulator"
        }
    ],
    "CFBundlePackageType": "XFWK",
    "XCFrameworkFormatVersion": "1.0"
}


class XcframeworkProcessorToolTest(unittest.TestCase):

  def test_get_library_from_plist_with_unsupported_platform(self):
    with self.assertRaisesRegex(
        ValueError,
        r"Imported XCFramework does not support the following platform.*"):
      xcframework_processor_tool._get_library_from_plist(
          info_plist=_MOCK_XCFRAMEWORK_INFO_PLIST,
          platform="tvos",
          architecture="arm64",
          environment="device",
      )

  def test_get_library_from_plist_with_unsupported_architecture(self):
    with self.assertRaisesRegex(
        ValueError,
        r"Imported XCFramework does not support the following platform.*"):
      xcframework_processor_tool._get_library_from_plist(
          info_plist=_MOCK_XCFRAMEWORK_INFO_PLIST,
          platform="ios",
          architecture="armv7",
          environment="device",
      )

  def test_get_library_from_plist_with_unsupported_platform_variant(self):
    with self.assertRaisesRegex(
        ValueError,
        r"Imported XCFramework does not support the following platform.*"):
      xcframework_processor_tool._get_library_from_plist(
          info_plist=_MOCK_XCFRAMEWORK_INFO_PLIST,
          platform="watchos",
          architecture="x86_64",
          environment="device",
      )

  def test_get_library_from_plist_with_supported_target_triplet(self):
    xcframework_library = xcframework_processor_tool._get_library_from_plist(
        info_plist=_MOCK_XCFRAMEWORK_INFO_PLIST,
        platform="ios",
        architecture="arm64",
        environment="simulator",
    )
    self.assertIsInstance(xcframework_library, dict)

    expected_xcframework_library = {
        "LibraryIdentifier": "ios-arm64_x86_64-simulator",
        "LibraryPath": "MyFramework.framework",
        "SupportedArchitectures": ["arm64", "x86_64"],
        "SupportedPlatform": "ios",
        "SupportedPlatformVariant": "simulator"
    }
    self.assertDictEqual(xcframework_library, expected_xcframework_library)

  def test_tool_raises_error_with_invalid_info_plist(self):
    info_plist_fp = tempfile.NamedTemporaryFile(delete=False)
    self.addCleanup(lambda: os.unlink(info_plist_fp.name))

    with info_plist_fp:
      invalid_plist_content = {"Foo": "Bar"}
      plistlib.dump(invalid_plist_content, info_plist_fp)

    with self.assertRaisesRegex(
        ValueError,
        r"Info.plist file does not contain key: 'XCFrameworkFormatVersion'.*"):
      xcframework_processor_tool._get_plist_dict(
          info_plist_path=info_plist_fp.name)


if __name__ == "__main__":
  unittest.main()
