import sys
import os
from pathlib import Path
from ScriptCollection.GeneralUtilities import GeneralUtilities
from ScriptCollection.ScriptCollectionCore import ScriptCollectionCore
from ScriptCollection.TasksForCommonProjectStructure import TasksForCommonProjectStructure


def common_tasks():
    file = str(Path(__file__).absolute())
    folder_of_current_file = os.path.dirname(file)
    sc = ScriptCollectionCore()
    version = sc.get_semver_version_from_gitversion(GeneralUtilities.resolve_relative_path("../..", os.path.dirname(file)))  # Should always be the same as the project-version
    sc.replace_version_in_ini_file(GeneralUtilities.resolve_relative_path("../setup.cfg", folder_of_current_file), version)
    sc.replace_version_in_python_file(GeneralUtilities.resolve_relative_path("../Adame/Adame.py", folder_of_current_file), version)
    t = TasksForCommonProjectStructure()
    additionalargumentsfile_from_commandline_arguments = t.get_additionalargumentsfile_from_commandline_arguments(sys.argv, None)
    t.standardized_tasks_do_common_tasks(file, version, 1, "QualityCheck", True, additionalargumentsfile_from_commandline_arguments, sys.argv)


if __name__ == "__main__":
    common_tasks()
