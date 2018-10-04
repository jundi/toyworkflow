"""Sample workflow tasks for testing luigi."""

import os
import shutil
import logging
import luigi


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
FILEHANDLER = logging.FileHandler('task_log')
FILEHANDLER.setLevel(logging.INFO)
LOGGER.addHandler(FILEHANDLER)


class FatalWorkflowError(Exception):
    """Error that can not be fixed"""
    pass


class WorkflowError(Exception):
    """Error that might be fixed by retrying the task"""
    pass


class WorkflowTask(luigi.Task):
    """Base class for workflow tasks"""
    # retry_count = 10
    # disable_hard_timeout = true
    # disable_window_seconds = true
    workspace = luigi.Parameter()


class WriteFile(WorkflowTask):
    """Task that creates output1 in workspace directory."""

    def output(self):
        return luigi.LocalTarget(os.path.join(self.workspace, 'output1'))

    def run(self):
        LOGGER.info("The dataset is disabled: %s", str(self.disabled))
        with self.output().open('w') as outfile:
            outfile.write('foobar')


class CopyFile(WorkflowTask):
    """Task that copies output1 to output2 in workspace directory."""
    def requires(self):
        return WriteFile(workspace=self.workspace)

    def output(self):
        return luigi.LocalTarget(os.path.join(self.workspace, 'output2'))

    def run(self):
        LOGGER.info("The dataset is disabled: %s", str(self.disabled))

        if os.path.exists(os.path.join(self.workspace, 'fatal_error')):
            raise FatalWorkflowError('Encountered error, cancel workflow')

        if os.path.exists(os.path.join(self.workspace, 'error')):
            raise WorkflowError('Encountered error, retry workflow')

        shutil.copy(self.input().path, self.output().path)


@WorkflowTask.event_handler(luigi.Event.SUCCESS)
def report_task_success(task):
    """Success Handler"""
    LOGGER.info("Task %s finished in workspace %s",
                 task.__class__.__name__, task.workspace)


@WorkflowTask.event_handler(luigi.Event.FAILURE)
def report_task_failure(task, exception):
    """Failure Handler"""

    LOGGER.info("Task %s failed in workspace %s with error %s",
                 task.__class__.__name__, task.workspace, str(exception))

    # Disable task if error is Fatal
    if isinstance(exception, FatalWorkflowError):
        task.disabled = True
