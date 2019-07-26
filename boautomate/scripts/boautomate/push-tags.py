
import sys
import re

"""
    Propagate tags
    ==============
    
    When application was tagged with eg. 2.7.3, then tag also 2.7 and 2. 
    If there is no "3", then push to latest and to the latest-stable.
"""

sys.path.append('/opt/boautomate')

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from boautomate.boautomatelib.nodeexecutor.pipeline import stage, info, fail, success
from boautomate.boautomatelib.payloadparser.actions import *
from boautomate.boautomatelib.payloadparser.facts import DockerRepositoryFact
from boautomate.boautomatelib.tools.lib.docker import RegistryException
from boautomate.boautomatelib.tools.lib.sort import natural_sort


class PushTags(NodeExecutor):
    # configurable settings
    regexp: re.Pattern
    separator: str
    latest_stable_name: str

    present_tags: list

    def main(self):
        """
        Pipeline method
        :return:
        """

        with stage('Validate requirements'):
            self.assert_facts_present([DockerRepositoryFact.identify()])
            self.assert_what_is_going_on_at_least_one_of([ACTION_DOCKER_PUSH])

            registry_fact = self.context().get_fact(DockerRepositoryFact.identify())  # type: DockerRepositoryFact

            if not registry_fact.updated_tags:
                info('No tags pushed')
                return

            info('Repository:', registry_fact.url)
            info('Incoming tags to process:', registry_fact.updated_tags)

        with stage('Prepare regexp'):
            self.regexp = re.compile(r'^v?([0-9.+]+)$')
            self.latest_stable_name = 'latest-stable'
            self.separator = '.'

        with stage('Validate tags'):
            self._stage_validate_tags(registry_fact.updated_tags)

        with stage('Propagate tags'):
            try:
                results = self._stage_propagate_tags(registry_fact.updated_tags)

            except RegistryException as e:
                info('Error occurred: ' + str(e))
                info('Response: ' + str(e.response))

                raise e

        with stage('Notify'):
            success('Pushed tags:', results)

    def _stage_validate_tags(self, tags: list):
        self.present_tags = self.context().docker_registry().current_repository().tags()
        self._assert_contains(tags, self.present_tags)

        info('Present tags:', self.present_tags)

    def _stage_propagate_tags(self, tags: list) -> list:
        """
        Stage method, propagates multiple tags

        :param tags:
        :return:
        """

        origin_tag: str
        results = []

        for origin_tag in tags:
            if not self._is_valid_version_to_propagate(origin_tag):
                info('Tag %s does not match regexp' % origin_tag)
                continue

            for propagated_tag in self._get_tags_to_propagate_for_tag(origin_tag):
                self.context().docker_registry().current_repository().tag(propagated_tag, origin_tag)
                results.append(propagated_tag)

        return results

    def _get_tags_to_propagate_for_tag(self, tag: str):
        """ eg. for 5.0.5 => 5.0 and 5 """

        tags_to_push = []
        split = tag.split(self.separator)
        left = len(split)

        while left != 1 and len(split) > 1:
            left -= 1
            tags_to_push.append(".".join(split[0:left]))

        if self.latest_stable_name and self._is_tag_latest_stable(tag):
            tags_to_push.append(self.latest_stable_name)

        info('Will tag ' + tag + ' as ' + str(tags_to_push) + '')

        return tags_to_push

    def _is_tag_latest_stable(self, tag: str):
        normalized_all_tags = map(
            lambda t: self._normalize_tag(t),
            self.present_tags
        )

        only_versions = filter(
            lambda t: self._is_valid_version_to_propagate(t),
            normalized_all_tags
        )

        in_proper_order = list(reversed(natural_sort(only_versions)))

        if len(in_proper_order) == 0:
            return False

        return in_proper_order[0] == self._normalize_tag(tag)

    def _normalize_tag(self, tag: str):
        return tag.lstrip('v.-+ ')

    def _is_valid_version_to_propagate(self, version: str):
        return self.regexp.match(version) is not None

    def _assert_contains(self, tags: list, in_tags_list: list):
        for tag in tags:
            if tag not in in_tags_list:
                fail('Source tag %s not found in the docker registry' % tag)


PushTags().main()
