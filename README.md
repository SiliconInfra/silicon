## Models Documentation

### Table of Contents

* [Eventlog](#eventlog)

### Eventlog

#### Table of Contents

* [Overview](#overview)
  * [Supported Django and Python Versions](#supported-django-and-python-versions)
* [Documentation](#documentation)
  * [Usage](#usage)
  * [Signals](#signals)

#### Overview

`eventlog` is a simple app that provides an easy and clean interface for logging diagnostic as well as business intelligence data about activity that occurs in your site.

By default this app writes directly to the database.

For small sites, it should be good enough to use inline but you might want to consider wrapping calls to the `log()` method and queue them in
a job manager like `celery` so that the calls become asynchronous.

##### Supported Django and Python versions

Django / Python | 3.6 | 3.7 | 3.8
--------------- | --- | --- | ---
3.0  |  *  |  *  |  *


#### Documentation

##### Usage

Using `eventlog` is pretty simple. Throughout your site, you just call a single function, `log()` to record whatever information you want to log. If you are wanting to log things from third party apps, your best bet is to use signals. Hopefully the app in question provides some useful signals, but if not, perhaps some of the built in model signals will be enough (e.g. `pre_save`, `post_delete`, etc.)

Example:

```python
from eventlog.models import log

def some_view(request):
    # stuff is done in body of view
    # then at the end before returning the response:
    log(
        user=request.user,
        action="CREATED_FOO_WIDGET",
        obj=foo,
        extra={
            "title": foo.title
        }
    )
    return HttpResponse()
```

The `action` parameter can be any string you choose. By convention, we
always use all caps. Take note, however, whatever you choose, will be the
label that appears in the admin's list filter, so give it some thought on
naming conventions in your site so that the admin interface makes sense
when you have 50,000 log records you want to filter down and analyze.

The `extra` parameter can be anything that will serialize to JSON. Results
become easier to manage if you keep it at a single level. Also, keep in
mind that this is displayed in the admin's list view so if you put too much
it can take up a lot of space. A good rule of thumb here is put enough
identifying data to get a sense for what is going on and a key or keys
that enable you to dig deeper if you want or need to.

##### Mixin

You can also easily make your class based views auto-logged by using the
`pinax.eventlog.mixins.EventLogMixin`. The only requirement is defining an
`action_kind` property on the view. But you can also override a number of
properties to customize what is logged.

##### Signals

There is a signal that you are setup a receiver for to enable you to trigger
other actions when an event has been logged:

`event_logged` provides an `event` object as an argument that is the event that
was just logged.