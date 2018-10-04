Toy workflow for luigi testing
==============================

To use central scheduler, copy ``luigi.cfg`` to  ``/etc/luigi/luigi.cfg``, and start workflow::

   luigi --module workflow CopyFile --workspace test_workspace

When using local scheduler luigi must be configured with commandline parameters::

   luigi --module workflow CopyFile --local-scheduler --workspace test_workspace --worker-keep-alive --worker-retry-external-tasks --scheduler-retry-delay 10
