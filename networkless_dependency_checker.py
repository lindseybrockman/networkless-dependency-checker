#!/usr/bin/env python
import sys

try:
    from pip._vendor.pkg_resources import (
        get_distribution,
        DistributionNotFound,
        Requirement,
        VersionConflict
    )
except ImportError:
    raise ImportError('This script requires a pip installation.')


class NetworklessDependencyFinder(object):
    def __init__(self, requirements_file='requirements.txt'):
        self.requirements_file = requirements_file
        self.project_requirements = self.get_project_requirements()

    def get_project_requirements(self):
        """Parses the requirements txt file and saves results to an instance variable. Flags, comments, empty lines are skipped.
        """
        requirements_txt = open(self.requirements_file, 'r')
        requirements = requirements_txt.read()
        requirements = requirements.split('\n')

        return requirements

    def run(self):
        all_requirements_fufilled = True
        for line_number, line in enumerate(self.project_requirements, start=1):
            if self.is_valid_requirement(line):
                requirement = Requirement.parse(line)
                message = self._run(requirement, line_number)
                if message:
                    sys.stderr.write(message)

    @classmethod
    def is_valid_requirement(cls, requirement):
        try:
            Requirement.parse(requirement)
        except ValueError:
            return False
        else:
            return True

    def _run(self, parsed_requirement, line_number):
        message = ''
        try:
            get_distribution(parsed_requirement)
        except DistributionNotFound:
            message = '[ERROR] {} line {}: {} not found on system\n'.format(
                self.requirements_file,
                line_number,
                parsed_requirement
            )
        except VersionConflict:
            exc_type, conflicting_version, traceback = sys.exc_info()
            message = '[ERROR] {} line {}: {} is required but version {} is available \n'.format(
                self.requirements_file,
                line_number,
                parsed_requirement,
                conflicting_version.args[0].version
            )

        if self._requirement_is_unpinned(parsed_requirement):
            message += '[WARNING] {} line {}: {} requirement is not pinned. >:(\n'.format(
                self.requirements_file,
                line_number,
                parsed_requirement
            )

        return message

    def _requirement_is_unpinned(self, requirement):
        requirement_version_is_specified = bool(requirement.specs)
        return not requirement_version_is_specified


if __name__ == '__main__':
    # TODO: allow flag to override requirements.txt filename and path
    dependency_finder = NetworklessDependencyFinder()
    dependency_finder.run()
