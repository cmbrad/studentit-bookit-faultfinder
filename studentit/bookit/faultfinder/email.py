import datetime
from studentit.mail import Mailer

EMAIL_STYLE = \
"""
table, th, td {
    border:1px solid black;
}

table {
    border-collapse:collapse;
    width:100%;
}

th, td {
    text-align:left;
    padding:8px;
}

th {
    background-color:#31465C;
    color:white;
}
"""

EMAIL_TEMPLATE = \
"""
<html>
<head>
<style>
{style}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _elem(tag, *content):
	content = map(str, content)
	return '<{tag}>{content}</{tag}>'.format(tag=tag, content=''.join(content))


def table(*content):
	return _elem('table', *content)


def th(*content):
	return _elem('th', *content)


def tr(*content):
	return _elem('tr', *content)


def td(*content):
	return _elem('td', *content)


def send_fault_email(username, password, resources, to_addr):
	mailer = Mailer(username, password)
	body = table(
		th('Site'),
		th('Location'),
		th('Resource'),
		th('Started on'),
		th('Age'),
		''.join([row(resource) for resource in resources])
	)
	content = EMAIL_TEMPLATE.format(style=EMAIL_STYLE, body=body)
	mailer.send(subject='Potential Faults {}'.format(datetime.date.today()), body=content, to_address=to_addr, insert_newlines=True)


def row(resource):
	site_name, location_name, resource_name, fault_begin, age = resource

	return tr(
		td(site_name),
		td(location_name),
		td(resource_name),
		td(fault_begin),
		td(age)
	)

