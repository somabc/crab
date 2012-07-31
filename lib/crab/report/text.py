from crab import CrabEvent, CrabStatus

def report_to_text(report, event_list=True):
    lines = []
    sections = ['error', 'warning', 'ok']
    titles = ['Jobs with Errors', 'Jobs with Warnings', 'Successful Jobs']

    for (section, title) in zip(sections, titles):
        jobs = getattr(report, section)
        if jobs:
            lines.append(title)
            lines.append('=' * len(title))
            lines.append('')
            for id_ in jobs:
                lines.append('    ' + _summary_line(report, id_))
            lines.append('')

    if event_list:
        lines.append('Event Listing')
        lines.append('=============')
        lines.append('')

        for id_ in set.union(report.error, report.warning, report.ok):
            subhead = _summary_line(report, id_)
            lines.append(subhead)
            lines.append('-' * len(subhead))
            lines.append('')

            for e in report.events[id_]:
                lines.append('    ' + _event_line(e))

            lines.append('')

    return "\n".join(lines)


def _summary_line(report, id_):
    info = report.info[id_]
    return '{0:10} {1:10} {2}'.format(info['host'], info['user'], info['title'])

def _event_line(event):
    return '{0:10} {1:10} {2}'.format(CrabEvent.get_name(event['type']),
                                CrabStatus.get_name(event['status']),
                                event['datetime'])
