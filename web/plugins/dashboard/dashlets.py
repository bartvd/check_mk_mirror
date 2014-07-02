#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

#   .--Overview------------------------------------------------------------.
#   |              ___                       _                             |
#   |             / _ \__   _____ _ ____   _(_) _____      __              |
#   |            | | | \ \ / / _ \ '__\ \ / / |/ _ \ \ /\ / /              |
#   |            | |_| |\ V /  __/ |   \ V /| |  __/\ V  V /               |
#   |             \___/  \_/ \___|_|    \_/ |_|\___| \_/\_/                |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_overview(params):
    html.write(
        '<table class=dashlet_overview>'
        '<tr><td valign=top>'
        '<a href="http://mathias-kettner.de/check_mk.html"><img style="margin-right: 30px;" src="images/check_mk.trans.120.png"></a>'
        '</td>'
        '<td><h2>Check_MK Multisite</h2>'
        'Welcome to Check_MK Multisite. If you want to learn more about Multisite, please visit '
        'our <a href="http://mathias-kettner.de/checkmk_multisite.html">online documentation</a>. '
        'Multisite is part of <a href="http://mathias-kettner.de/check_mk.html">Check_MK</a> - an Open Source '
        'project by <a href="http://mathias-kettner.de">Mathias Kettner</a>.'
        '</td>'
    )

    html.write('</tr></table>')

dashlet_types["overview"] = {
    "title"       : _("Overview / Introduction"),
    "description" : _("Displays an introduction and Check_MK logo."),
    "render"      : dashlet_overview,
    "allowed"     : config.builtin_role_ids,
    "selectable"  : False, # can not be selected using the dashboard editor
}

#.
#   .--MK-Logo-------------------------------------------------------------.
#   |               __  __ _  __     _                                     |
#   |              |  \/  | |/ /    | |    ___   __ _  ___                 |
#   |              | |\/| | ' /_____| |   / _ \ / _` |/ _ \                |
#   |              | |  | | . \_____| |__| (_) | (_| | (_) |               |
#   |              |_|  |_|_|\_\    |_____\___/ \__, |\___/                |
#   |                                           |___/                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_mk_logo(params):
    html.write('<a href="http://mathias-kettner.de/check_mk.html">'
     '<img style="margin-right: 30px;" src="images/check_mk.trans.120.png"></a>')

dashlet_types["mk_logo"] = {
    "title"       : _("Check_MK Logo"),
    "description" : _("Shows the Check_MK logo."),
    "render"      : dashlet_mk_logo,
    "allowed"     : config.builtin_role_ids,
    "selectable"  : False, # can not be selected using the dashboard editor
}

#.
#   .--Globes/Stats--------------------------------------------------------.
#   |       ____ _       _                  ______  _        _             |
#   |      / ___| | ___ | |__   ___  ___   / / ___|| |_ __ _| |_ ___       |
#   |     | |  _| |/ _ \| '_ \ / _ \/ __| / /\___ \| __/ _` | __/ __|      |
#   |     | |_| | | (_) | |_) |  __/\__ \/ /  ___) | || (_| | |_\__ \      |
#   |      \____|_|\___/|_.__/ \___||___/_/  |____/ \__\__,_|\__|___/      |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_hoststats(params):
    table = [
       ( _("Up"), "#0b3",
        "searchhost&is_host_scheduled_downtime_depth=0&hst0=on",
        "Stats: state = 0\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "StatsAnd: 2\n"),

       ( _("Down"), "#f00",
        "searchhost&is_host_scheduled_downtime_depth=0&hst1=on",
        "Stats: state = 1\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "StatsAnd: 2\n"),

       ( _("Unreachable"), "#f80",
        "searchhost&is_host_scheduled_downtime_depth=0&hst2=on",
        "Stats: state = 2\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "StatsAnd: 2\n"),

       ( _("In Downtime"), "#0af",
        "searchhost&search=1&is_host_scheduled_downtime_depth=1",
        "Stats: scheduled_downtime_depth > 0\n" \
       )
    ]
    filter = "Filter: custom_variable_names < _REALNAME\n"

    render_statistics(html.var('id', "hoststats"), "hosts", table, filter)

dashlet_types["hoststats"] = {
    "title"       : _("Host Statistics"),
    "sort_index"  : 45,
    "description" : _("Displays statistics about host states as globe and a table."),
    "render"      : dashlet_hoststats,
    "refresh"     : 60,
    "allowed"     : config.builtin_role_ids,
    "size"        : (30, 18),
    "resizable"   : False,
}

def dashlet_servicestats(params):
    table = [
       ( _("OK"), "#0b3",
        "searchsvc&hst0=on&st0=on&is_in_downtime=0",
        "Stats: state = 0\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),

       ( _("In Downtime"), "#0af",
        "searchsvc&is_in_downtime=1",
        "Stats: scheduled_downtime_depth > 0\n" \
        "Stats: host_scheduled_downtime_depth > 0\n" \
        "StatsOr: 2\n"),

       ( _("On Down host"), "#048",
        "searchsvc&hst1=on&hst2=on&hstp=on&is_in_downtime=0",
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state != 0\n" \
        "StatsAnd: 3\n"),

       ( _("Warning"), "#ff0",
        "searchsvc&hst0=on&st1=on&is_in_downtime=0",
        "Stats: state = 1\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),

       ( _("Unknown"), "#f80",
        "searchsvc&hst0=on&st3=on&is_in_downtime=0",
        "Stats: state = 3\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),

       ( _("Critical"), "#f00",
        "searchsvc&hst0=on&st2=on&is_in_downtime=0",
        "Stats: state = 2\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),
    ]
    filter = "Filter: host_custom_variable_names < _REALNAME\n"

    render_statistics(html.var('id', "servicestats"), "services", table, filter)


dashlet_types["servicestats"] = {
    "title"       : _("Service Statistics"),
    "sort_index"  : 50,
    "description" : _("Displays statistics about service states as globe and a table."),
    "render"      : dashlet_servicestats,
    "refresh"     : 60,
    "allowed"     : config.builtin_role_ids,
    "size"        : (30, 18),
    "resizable"   : False,
}

def render_statistics(pie_id, what, table, filter):
    html.write("<div class=stats>")
    pie_diameter     = 130
    pie_left_aspect  = 0.5
    pie_right_aspect = 0.8

    # Is the query restricted to a certain WATO-path?
    wato_folder = html.var("wato_folder")
    if wato_folder:
        # filter += "Filter: host_state = 0"
        filter += "Filter: host_filename ~ ^/wato/%s/\n" % wato_folder.replace("\n", "")

    # Is the query restricted to a host contact group?
    host_contact_group = html.var("host_contact_group")
    if host_contact_group:
        filter += "Filter: host_contact_groups >= %s\n" % host_contact_group.replace("\n", "")

    # Is the query restricted to a service contact group?
    service_contact_group = html.var("service_contact_group")
    if service_contact_group:
        filter += "Filter: service_contact_groups >= %s\n" % service_contact_group.replace("\n", "")

    query = "GET %s\n" % what
    for entry in table:
        query += entry[3]
    query += filter

    result = html.live.query_summed_stats(query)
    pies = zip(table, result)
    total = sum([x[1] for x in pies])

    html.write('<canvas class=pie width=%d height=%d id="%s_stats" style="float: left"></canvas>' %
            (pie_diameter, pie_diameter, pie_id))
    html.write('<img src="images/globe.png" class="globe">')

    html.write('<table class="hoststats%s" style="float:left">' % (
        len(pies) > 1 and " narrow" or ""))
    table_entries = pies
    while len(table_entries) < 6:
        table_entries = table_entries + [ (("", "#95BBCD", "", ""), "&nbsp;") ]
    table_entries.append(((_("Total"), "", "all%s" % what, ""), total))
    for (name, color, viewurl, query), count in table_entries:
        url = "view.py?view_name=" + viewurl + "&filled_in=filter&search=1&wato_folder=" \
              + html.urlencode(html.var("wato_folder", ""))
        if host_contact_group:
            url += '&opthost_contactgroup=' + host_contact_group
        if service_contact_group:
            url += '&optservice_contactgroup=' + service_contact_group
        html.write('<tr><th><a href="%s">%s</a></th>' % (url, name))
        style = ''
        if color:
            style = ' style="background-color: %s"' % color
        html.write('<td class=color%s>'
                   '</td><td><a href="%s">%s</a></td></tr>' % (style, url, count))

    html.write("</table>")

    r = 0.0
    pie_parts = []
    if total > 0:
        # Count number of non-empty classes
        num_nonzero = 0
        for info, value in pies:
            if value > 0:
                num_nonzero += 1

        # Each non-zero class gets at least a view pixels of visible thickness.
        # We reserve that space right now. All computations are done in percent
        # of the radius.
        separator = 0.02                                    # 3% of radius
        remaining_separatorspace = num_nonzero * separator  # space for separators
        remaining_radius = 1 - remaining_separatorspace     # remaining space
        remaining_part = 1.0 # keep track of remaining part, 1.0 = 100%

        # Loop over classes, begin with most outer sphere. Inner spheres show
        # worse states and appear larger to the user (which is the reason we
        # are doing all this stuff in the first place)
        for (name, color, viewurl, q), value in pies[::1]:
            if value > 0 and remaining_part > 0: # skip empty classes

                # compute radius of this sphere *including all inner spheres!* The first
                # sphere always gets a radius of 1.0, of course.
                radius = remaining_separatorspace + remaining_radius * (remaining_part ** (1/3.0))
                pie_parts.append('chart_pie("%s", %f, %f, %r, true);' % (pie_id, pie_right_aspect, radius, color))
                pie_parts.append('chart_pie("%s", %f, %f, %r, false);' % (pie_id, pie_left_aspect, radius, color))

                # compute relative part of this class
                part = float(value) / total # ranges from 0 to 1
                remaining_part           -= part
                remaining_separatorspace -= separator


    html.write("</div>")
    html.javascript("""
function chart_pie(pie_id, x_scale, radius, color, right_side) {
    var context = document.getElementById(pie_id + "_stats").getContext('2d');
    if (!context)
        return;
    var pie_x = %(x)f;
    var pie_y = %(y)f;
    var pie_d = %(d)f;
    context.fillStyle = color;
    context.save();
    context.translate(pie_x, pie_y);
    context.scale(x_scale, 1);
    context.beginPath();
    if(right_side)
        context.arc(0, 0, (pie_d / 2) * radius, 1.5 * Math.PI, 0.5 * Math.PI, false);
    else
        context.arc(0, 0, (pie_d / 2) * radius, 0.5 * Math.PI, 1.5 * Math.PI, false);
    context.closePath();
    context.fill();
    context.restore();
    context = null;
}


if (has_canvas_support()) {
    %(p)s
}
""" % { "x" : pie_diameter / 2, "y": pie_diameter/2, "d" : pie_diameter, 'p': '\n'.join(pie_parts) })

#.
#   .--PNP-Graph-----------------------------------------------------------.
#   |         ____  _   _ ____        ____                 _               |
#   |        |  _ \| \ | |  _ \      / ___|_ __ __ _ _ __ | |__            |
#   |        | |_) |  \| | |_) |____| |  _| '__/ _` | '_ \| '_ \           |
#   |        |  __/| |\  |  __/_____| |_| | | | (_| | |_) | | | |          |
#   |        |_|   |_| \_|_|         \____|_|  \__,_| .__/|_| |_|          |
#   |                                               |_|                    |
#   +----------------------------------------------------------------------+
#   | Renders a single performance graph                                   |
#   '----------------------------------------------------------------------'

def dashlet_pnpgraph(params):
    service = params.get('service')
    if not service:
        service = "_HOST_"

    site = params.get('site')
    if not site:
        base_url = defaults.url_prefix
    else:
        base_url = html.site_status[site]["site"]["url_prefix"]
    base_url += "pnp4nagios/index.php/"
    var_part = "?host=%s&srv=%s&source=0&view=%s&theme=multisite&_t=%d" % \
            (pnp_cleanup(params['host']), pnp_cleanup(service), params['timerange'], int(time.time()))

    pnp_url = base_url + "graph" + var_part
    img_url = base_url + "image" + var_part
    html.write('<a href="%s"><img border=0 src="%s"></a>' % (pnp_url, img_url))

dashlet_types["pnpgraph"] = {
    "title"       : _("Performance Graph"),
    "sort_index"  : 20,
    "description" : _("Displays a performance graph of a host or service."),
    "render"      : dashlet_pnpgraph,
    "refresh"     : 60,
    "size"        : (60, 21),
    "allowed"     : config.builtin_role_ids,
    "opt_params"  : [ "service" ],
    "parameters"  : [
        ("site", DropdownChoice(
            title = _('Site'),
            choices = config.sorted_sites,
        )),
        ("host", TextAscii(
            title = _('Hostname'),
        )),
        ("service", TextAscii(
            title = _('Service Description'),
        )),
        ("timerange", DropdownChoice(
            default_value = '1',
            choices= [
                ("0", _("4 Hours")),  ("1", _("25 Hours")),
                ("2", _("One Week")), ("3", _("One Month")),
                ("4", _("One Year")),
            ],
        )),
    ],
    "styles": """
.dashlet.pnpgraph .dashlet_inner {
    background-color: #fff;
    text-align: center;
}
""",
}

#.
#   .--nodata--------------------------------------------------------------.
#   |                                  _       _                           |
#   |                  _ __   ___   __| | __ _| |_ __ _                    |
#   |                 | '_ \ / _ \ / _` |/ _` | __/ _` |                   |
#   |                 | | | | (_) | (_| | (_| | || (_| |                   |
#   |                 |_| |_|\___/ \__,_|\__,_|\__\__,_|                   |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_nodata(params):
    html.write("<div class=nograph><div class=msg>")
    html.write(params.get("text"))
    html.write("</div></div>")

dashlet_types["nodata"] = {
    "title"       : _("Static text"),
    "sort_index"     : 100,
    "description" : _("Displays a static text to the user."),
    "render"      : dashlet_nodata,
    "allowed"     : config.builtin_role_ids,
    "parameters"  : [
        ("text", TextAscii(
            title = _('Text'),
            size = 50,
        )),
    ],
}

#.
#   .--View----------------------------------------------------------------.
#   |                      __     ___                                      |
#   |                      \ \   / (_) _____      __                       |
#   |                       \ \ / /| |/ _ \ \ /\ / /                       |
#   |                        \ V / | |  __/\ V  V /                        |
#   |                         \_/  |_|\___| \_/\_/                         |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_view_url(params):
    return "view.py?view_name=%s&display_options=HRSIXL&_display_options=HRSIXL&_body_class=dashlet" % \
            (params['view_name'])

dashlet_types["view"] = {
    "title"          : _("View"),
    "sort_index"     : 10,
    "description"    : _("Displays a the content of a Multisite view."),
    "iframe_urlfunc" : dashlet_view_url,
    "allowed"        : config.builtin_role_ids,
}

#.
#   .--Custom URL----------------------------------------------------------.
#   |         ____          _                    _   _ ____  _             |
#   |        / ___|   _ ___| |_ ___  _ __ ___   | | | |  _ \| |            |
#   |       | |  | | | / __| __/ _ \| '_ ` _ \  | | | | |_) | |            |
#   |       | |__| |_| \__ \ || (_) | | | | | | | |_| |  _ <| |___         |
#   |        \____\__,_|___/\__\___/|_| |_| |_|  \___/|_| \_\_____|        |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_url(params):
    return params['url']

dashlet_types["url"] = {
    "title"          : _("Custom URL"),
    "sort_index"     : 80,
    "description"    : _("Displays the content of a custom website."),
    "iframe_urlfunc" : dashlet_url,
    "allowed"        : config.builtin_role_ids,
    "size"           : (30, 10),
    "parameters"  : [
        ("url", TextAscii(
            title = _('URL'),
            size = 50,
        )),
    ],
}