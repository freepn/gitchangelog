# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import os
import textwrap

from .common import BaseGitReposTest, cmd, gitchangelog


class TemplatingTest(BaseGitReposTest):
    """Base for all tests needing to start in a new git small repository"""

    def setUp(self):
        super(TemplatingTest, self).setUp()

        self.git.commit(
            message='new: begin',
            author='Bob <bob@example.com>',
            date='2000-01-01 10:00:00',
            allow_empty=True)

    def test_unexistent_template_name(self):
        """Unexisting template should get a proper error message"""

        gitchangelog.file_put_contents(
            ".gitchangelog.rc",
            "output_engine = makotemplate('doesnotexist')")
        out, err, errlvl = cmd('$tprog')
        self.assertEqual(
            errlvl, 1,
            msg="Should fail as template does not exist")
        self.assertEqual(
            out, "",
            msg="No stdout was expected since there was an error. "
            "Current stdout:\n%r" % out)
        self.assertContains(
            err, "doesnotexist",
            msg="There should be an error message mentioning 'doesnotexist'. "
            "Current stderr:\n%s" % err)
        self.assertContains(
            err, "restructuredtext",
            msg="The error message should mention 'available'. "
            "Current stderr:\n%s" % err)
        self.assertContains(
            err, "mako",
            msg="The error message should mention 'mako'. "
            "Current stderr:\n%s" % err)
        self.assertContains(
            err, "restructuredtext",
            msg="The error message should mention 'restructuredtext'. "
            "Current stderr:\n%s" % err)

    def test_template_has_access_to_full_commit(self):
        """Existing files should be accepted as valid templates"""

        gitchangelog.file_put_contents(
            "mytemplate.tpl",
            textwrap.dedent("""
                % for version in data["versions"]:
                ${version["tag"]}
                % for section in version["sections"]:
                  ${section["label"]}:
                % for commit in section["commits"]:
                    - ${commit["commit"].subject}
                % endfor
                % endfor
                % endfor
                """))
        gitchangelog.file_put_contents(
            ".gitchangelog.rc",
            "output_engine = makotemplate('mytemplate.tpl')")

        reference = textwrap.dedent("""
            None
              New:
                - new: begin
            """)

        out, err, errlvl = cmd('$tprog')
        self.assertEqual(
            err, "",
            msg="There should be non error messages. "
            "Current stderr:\n%s" % err)
        self.assertEqual(
            errlvl, 0,
            msg="Should succeed to find template")
        self.assertNoDiff(
            reference, out)

