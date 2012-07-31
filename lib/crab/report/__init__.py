from collections import namedtuple

from crab import CrabError, CrabStatus, CrabEvent
from crab.util.filter import CrabEventFilter

CrabReportJob = namedtuple('CrabReportJob', ['id_', 'start', 'end'])

CrabReport = namedtuple('CrabReport', ['num', 'error', 'warning', 'ok',
                                       'info', 'events'])

class CrabReportGenerator:
    """Class for generating reports on the operation of cron jobs.

    This class maintains a cache of job information and events
    to allow it to handle multiple report requests in an efficient
    manner.  This depends on a single configuration, so methods
    for adjusting the filtering are not provided."""

    def __init__(self, store,
                 skip_start=True, skip_ok=False, **kwargs):
        """Constructor for report object."""

        self.store = store

        self.filter = CrabEventFilter(store, skip_start=skip_start,
                                      skip_ok=skip_ok, **kwargs)
        self.cache_info = {}
        self.cache_event = {}
        self.cache_error = {}
        self.cache_warning = {}

    def __call__(self, jobs):
        """Function call method, to process a list of jobs.

        Takes a list of jobs, which is a list of CrabReportJob
        tuples.

        Returns a CrabReport object including the number of jobs to be
        included in the report and sets of jobs in each state,
        or None if there are no entries to show."""

        checked = set()
        error = set()
        warning = set()
        ok = set()
        num = 0
        report_info = {}
        report_events = {}

        for job in jobs:
            if job in checked:
                continue
            else:
                checked.add(job)

            (id_, start, end) = job

            if id_ in self.cache_info:
                info = self.cache_info[id_]
            else:
                info = self.store.get_job_info(id_)
                if info is None:
                    continue

                if info['jobid'] is None:
                    info['title'] = info['command']
                else:
                    info['title'] = info['jobid']

                self.cache_info[id_] = info

            if job in self.cache_event:
                events = self.cache_event[job]
                num_errors = self.cache_error[job]
                num_warnings = self.cache_warning[job]
            else:
                self.filter.set_timezone(info['timezone'])
                events = self.cache_event[job] = self.filter(
                             self.store.get_job_events(id_, limit=None,
                                                       start=start, end=end))
                num_errors = self.cache_error[job] = self.filter.errors
                num_warnings = self.cache_warning[job] = self.filter.warnings

            if events:
                num += 1

                if num_errors:
                    error.add(id_)
                elif num_warnings:
                    warning.add(id_)
                else:
                    ok.add(id_)

                report_info[id_] = info
                report_events[id_] = events

        if num:
            return CrabReport(num, error, warning, ok,
                              report_info, report_events)
        else:
            return None
