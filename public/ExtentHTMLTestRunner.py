"""
A TestRunner for use with the Python unit testing framework. It
generates a HTML report to show the result at a glance.
The simplest way to use this is to invoke its main method. E.g.
    import unittest
    import HTMLTestRunner
    ... define your tests ...
    if __name__ == '__main__':
        HTMLTestRunner.main()
For more customization options, instantiates a HTMLTestRunner object.
HTMLTestRunner is a counterpart to unittest's TextTestRunner. E.g.
    # output to a file
    fp = file('my_report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                title='My unit test',
                description='This demonstrates the report output by HTMLTestRunner.'
                )
    # Use an external stylesheet.
    # See the Template_mixin class for more customizable options
    runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="my_stylesheet.css" type="text/css">'
    # run the test
    runner.run(my_test_suite)
"""

__author__ = "Wai Yip Tung"
__update__ = "wishchen"
__version__ = "1.0"

"""
Change History
Version 1.0
* Use extent report HTML templete create test report. 
Version 0.8.2
* Show output inline instead of popup window (Viorel Lupu).
Version in 0.8.1
* Validated XHTML (Wolfgang Borgert).
* Added description of test classes and test cases.
Version in 0.8.0
* Define Template_mixin class for customization.
* Workaround a IE 6 bug that it does not treat <script> block as CDATA.
Version in 0.7.1
* Back port to Python 2.3 (Frank Horowitz).
* Fix missing scroll bars in detail log (Podi).
"""

# TODO: color stderr
# TODO: simplify javascript using ,ore than 1 class in the class attribute?

import datetime
import io
import sys
import time
import unittest
import re
from xml.sax import saxutils


# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before HTMLTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.

class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


# ----------------------------------------------------------------------
# Template

class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.
    Overall structure of an HTML report
    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
        0: 'pass',
        1: 'fail',
        2: 'error',
    }

    DEFAULT_TITLE = 'Unit Test Report'
    DEFAULT_DESCRIPTION = ''

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""
    <!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'/>
    <meta name='description' content=''/>
    <meta name='robots' content='noodp, noydir'/>
    <meta name='viewport' content='width=device-width, initial-scale=1'/>
    <meta id="timeStampFormat" name="timeStampFormat" content='MMM d, yyyy hh:mm:ss a'/>
    <link href='https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,600' rel='stylesheet' type='text/css'>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href='http://extentreports.com/resx/dist/css/extent.css' type='text/css' rel='stylesheet'/>
    <title>%(title)s - TestReport</title>
    %(stylesheet)s

</head>
<body class='extent standard default hide-overflow dark'>
<div id='theme-selector' alt='切换主题，默认黑色' title='切换主题'>
    <span><i class='material-icons'>desktop_windows</i></span>
</div>
%(heading)s
<div class='container'>
    %(report)s
    %(dashboard_view)s
</div>

</body>
%(script_js)s
</html>
"""
    # variables: (title, generator, stylesheet, heading, heading, ending)

    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">
    NAV = """
    <nav>
    <div class="nav-wrapper">
        <img  src="//qhstaticssl.kujiale.com/as/c15149e4e8596375a988df166762f185/coops-icon.png">
        <!-- slideout menu -->
        <ul id='slide-out' class='side-nav fixed hide-on-med-and-down'>
            <li class='waves-effect active'><a href='#!' view='test-view'
                                               onclick="configureView(0);chartsView('test');"><i class='material-icons'>dashboard</i></a>
            </li>
            <!-- <li class='waves-effect'><a href='#!' view='category-view' onclick="configureView(1)"><i
                    class='material-icons'>label_outline</i></a></li>
            <li class='waves-effect'><a href='#!' onclick="configureView(-1);chartsView('dashboard');"
                                        view='dashboard-view'><i class='material-icons'>track_changes</i></a></li> -->
        </ul>
        <!-- report name -->
        <span class='report-name'>Test Report: %(title)s</span>
        <!-- report headline -->
        <span class='report-headline'></span>
        <!-- nav-right -->
        <ul id='nav-mobile' class='right hide-on-med-and-down nav-right'>
            <li>
                <a href='#!'>
                    <span class='label suite-start-time blue darken-3'>Start_time: %(start_time)s</span>
                </a>
            </li>
            <li>
                <a href='#!'>
                    <span class='label blue darken-3'>Duration: %(duration)s </span>
                </a>
            </li>
        </ul>
    </div>
</nav>
    """

    TEST_VIEW = """
    <div id='test-view' class='view'>
        %(control_section)s
        %(view_charts)s
        %(test_list)s

        <div class='subview-right left'>
            <div class='view-summary'>
                <h5 class='test-name'></h5>
                <div id='step-filters' class="right">
                    <span class="blue-text" status="info" alt="info" title="info"><i
                            class="material-icons">info_outline</i></span>
                    <span class="green-text" status="pass" alt="pass" title="pass"><i class="material-icons">check_circle</i></span>
                    <span class="red-text" status="fail" alt="fail" title="fail"><i
                            class="material-icons">cancel</i></span>
                    <span class="red-text text-darken-4" status="fatal" alt="fatal" title="fatal"><i
                            class="material-icons">cancel</i></span>
                    <span class="pink-text text-lighten-1" status="error" alt="error" title="error"><i
                            class="material-icons">error</i></span>
                    <span class="orange-text" alt="warning" status="warning" title="warning"><i
                            class="material-icons">warning</i></span>
                    <span class="teal-text" status="skip" alt="skip" title="skip"><i
                            class="material-icons">redo</i></span>
                    <span status="clear" alt="Clear filters" title="Clear filters"><i
                            class="material-icons">clear</i></span>
                </div>
            </div>
        </div>
    </div>
    %(category_view)s

"""
    CONTROL_SECTION = """
    <section id='controls'>
            <div class='controls grey lighten-4'>
                <!-- test toggle -->
                <div class='chip transparent'>
                    <a class='dropdown-button tests-toggle' data-activates='tests-toggle' data-constrainwidth='true'
                       data-beloworigin='true' data-hover='true' href='#'>
                        <i class='material-icons'>warning</i> Status
                    </a>
                    <ul id='tests-toggle' class='dropdown-content'>
                        <li status='pass'><a href='#!'>Pass <i class='material-icons green-text'>check_circle</i></a>
                        </li>
                        <li status='fail'><a href='#!'>Fail <i class='material-icons red-text'>cancel</i></a></li>
                        <li status="skip"><a href="#!">Skip <i class="material-icons cyan-text">redo</i></a></li>
                        <li class='divider'></li>
                        <li status='clear' clear='true'><a href='#!'>Clear Filters <i
                                class='material-icons'>clear</i></a></li>
                    </ul>
                </div>
                <!-- test toggle -->
                <!-- category toggle -->
                <div class='chip transparent'>
                    <a class='dropdown-button category-toggle' data-activates='category-toggle'
                       data-constrainwidth='false' data-beloworigin='true' data-hover='true' href='#'>
                        <i class='material-icons'>local_offer</i> Category
                    </a>
                    <ul id='category-toggle' class='dropdown-content'>
                        %(suite_name)s
                        <li class='divider'></li>
                        <li class='clear'><a href='#!' clear='true'>Clear Filters</a></li>
                    </ul>
                </div>
                <!-- category toggle -->
                <!-- clear filters -->
                <div class='chip transparent hide'>
                    <a class='' id='clear-filters' alt='Clear Filters' title='Clear Filters'>
                        <i class='material-icons'>close</i> Clear
                    </a>
                </div>
                <!-- clear filters -->
                <!-- enable dashboard -->
                <div id='toggle-test-view-charts' class='chip transparent'>
                    <a class='pink-text' id='enable-dashboard' alt='Enable Dashboard' title='Enable Dashboard'>
                        <i class='material-icons'>track_changes</i> Dashboard
                    </a>
                </div>
                <!-- enable dashboard -->
                <!-- search -->
                <div class='chip transparent' alt='Search Tests' title='Search Tests'>
                    <a href="#" class='search-div'>
                        <i class='material-icons'>search</i> Search
                    </a>
                    <div class='input-field left hide'>
                        <input style="color: red" id='search-tests' type='text' class='validate browser-default'
                               placeholder='Search Tests...'>
                    </div>
                </div>
                <!-- search -->
            </div>
        </section>
    """
    SECTION_SUIT_NAME = """
    <li><a href='#'>%(desc)s</a></li>
    """

    VIEW_CHARTS = """
    <div id='test-view-charts' class='subview-full'>
            <div id='test-view-charts' class='subview-full'>
                <div id='charts-row' class='row nm-v nm-h'>
                    <div class=''>
                        <div class='card-panel nm-v' style="font-weight: bold;font-size:30px;">
                            <div class='left panel-name'>执行结果</div>
                            <div class='chart-box'>
                                <canvas id='parent-analysis' width='100' height='80'></canvas>
                            </div>
                            <div class='block text-small'>
                            <span class='tooltipped' data-position='top' style="font-weight: bold;font-size:15px;color:#00af00"><span
                                    class='strong'>%(pass_count)s</span> 个用例 passed</span>
                                <span class='tooltipped' data-position='top' style="font-weight: bold;font-size:15px;color:#F7464A"><span
                                        class='strong'>%(fail_count)s</span> 个用例 failed</span>
                            </div>
                            <div class='block text-small' style="font-weight: bold;font-size:15px;color:#ff6347">
                            <span class='strong tooltipped' data-position='top'
                            >%(error_count)s</span>
                                个用例 errored
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """

    SUBVIEW_LEFT = """
    <div class='subview-left left'>
            <div class='view-summary'>
                <h5>接口</h5>
                <ul id='test-collection' class='test-collection'>
                %(test_collection)s
                </ul>
            </div>
    </div>            
    """

    TEST_COLLECTION = """
    %(li_test_active)s
    <div class='test-heading'>
        <span class='test-name'>%(desc)s</span>
        <span class='test-time'>desc: %(doc)s </span>
        %(status_span)s
    </div>
    <div class='test-content hide'>
        <div class='test-desc'>Pass: %(Pass)s ;
                                Fail: %(fail)s ;
                                Error: %(error)s ;
        </div>
        <div class='test-attributes'>
            <div class='category-list'>
                <span class='category label white-text'>%(desc)s</span>
            </div>
        </div>
        <ul class='collapsible node-list' data-collapsible='accordion'>
            %(test_collection_ul_list)s
        </ul>
    </div>
    """
    TEST_COLLECTION_UL_LIST = """
            %(node_level)s
            <div class='collapsible-header'>
                <div class='node-name'>%(desc)s</div>
                <span class='node-time'>desc: %(doc)s</span>
                %(status_span)s
            </div>
            <div class='collapsible-body'>
                <div class='category-list right'>
                    <span class='category label white-text'>%(desc)s</span>
                </div>
                <div class='node-steps'>
                    <table class='bordered table-results'>
                        <thead>
                        <tr>
                            <th>Status</th>
                            <th>Identity</th>
                            <th>Details</th>
                        </tr>
                        </thead>
                        <tbody>
                        %(t_body)s
                        </tbody>
                    </table>
                 </div>
             </div>
            </li>
    """
    TBODY = """
        <tr class='info' status='info'>
            <td class='status info' title='info' alt='info'><i
                    class='material-icons'>low_priority</i></td>
            <td class='timestamp'>output</td>
            <td class='step-details'>%(script)s</td>
        </tr>
        <tr class='info' status='info'>
            <td class='status info' title='info' alt='info'><i
                    class='material-icons'>low_priority</i></td>
            <td class='timestamp'>outputexcept</td>
            <td class='step-details'>%(uescript)s
            </td>
        </tr>
    """
    CATEGORY_VIEW = """
    <div id='category-view' class='view hide'>
        <section id='controls'>
            <div class='controls grey lighten-4'>
                <!-- search -->
                <div class='chip transparent' alt='Search Tests' title='Search Tests'>
                    <a href="#" class='search-div'>
                        <i class='material-icons'>search</i> Search
                    </a>

                    <div class='input-field left hide'>
                        <input tyle="color: red;" id='search-tests' type='text'
                               class='validate browser-default'
                               placeholder='Search Tests...'>
                    </div>

                </div>
                <!-- search -->
            </div>
        </section>

        <div class='subview-left left'>
            <div class='view-summary'>
                <h5>Categories</h5>
                <ul id='category-collection' class='category-collection'>
                    <li class='category displayed active'>
                        <div class='category-heading'>
                            <span class='category-name'>All Suites</span>
                            <span class='category-status right'>
                                <span class='label pass'>%(Pass)s </span>
                                <span class='label fail'>%(fail)s</span>
                            </span>
                        </div>
                        <div class='category-content hide'>
                            <div class='category-status-counts'>
                                <span class='label green accent-4 white-text'>Passed: %(Pass)s</span>
                                <span class='label red lighten-1 white-text'>Failed: %(fail)s</span>
                                <span class='label blue lighten-1 white-text'>Errored: %(error)s</span>
                                <span class="label yellow darken-2 white-text">Skipped: </span>
                            </div>
                            <div class='category-tests'>
                                <table class='bordered table-results'>
                                    <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>TestName</th>
                                        <th>Status</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    %(category_tbody)s
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </li>
                    %(category_active)s
                <div class='subview-right left'>
            <div class='view-summary'>
                <h5 class='category-name'></h5>
            </div>
        </div>
    </div>


    """
    CATEGORY_TBODY = """
    <tr style="border: 1px solid #49cc90; background-color: rgba(73, 204, 144, .1)">
        <td>%(start_time)s</td>
        <td class='linked' test-id='%(name)s_%(cid)s'>%(desc)s</td>
        <td>%(category_tbody_td)s</td>
    </tr>
    <tr>
        <td></td>
        <td class='linked' test-id='暂未处理'></td>
        <td>%(category_tbody_td)s</td>
    </tr>

    """

    CATEGORY_ACTIVE = """
    <li class='category displayed active'>
        <div class='category-heading'>
            <span class='category-name'>%(desc)s</span>
            <span class='category-status right'>
                <span class='label pass'>%(Pass)s </span>
                <span class='label fail'>%(fail)s</span>
            </span>
        </div>
        <div class='category-content hide'>
            <div class='category-status-counts'>
                <span class='label green accent-4 white-text'>Passed: %(Pass)s</span>
                <span class='label red lighten-1 white-text'>Failed: %(fail)s</span>
                <span class='label blue lighten-1 white-text'>Errored: %(error)s</span>
            </div>
            <div class='category-tests'>
                <table class='bordered table-results'>
                    <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>TestName</th>
                        <th>Status</th>
                    </tr>
                    </thead>
                    <tbody>

                    </tbody>
                </table>
            </div>
        </div>
    </li>
    """
    DASHBOARD_VIEW = """
    <div id='dashboard-view' class='view hide'>
        <div class='card-panel transparent np-v'>
            <h5>Dashboard</h5>
            <div class='row'>
                <div class='col s2'>
                    <div class='card-panel r'>
                        Pass
                        <div class='panel-lead'>%(Pass)s</div>
                    </div>
                </div>
                <div class='col s2'>
                    <div class='card-panel r'>
                        Fail
                        <div class='panel-lead'>%(fail)s</div>
                    </div>
                </div>
                <div class='col s2'>
                    <div class='card-panel r'>
                        Error
                        <div class='panel-lead'>%(error)s</div>
                    </div>
                </div>
                <div class='col s2'>
                    <div class='card-panel r'>
                        Skip
                        <div class='panel-lead'></div>
                    </div>
                </div>
                <div class='col s2'>
                    <div class='card-panel r'>
                        Start
                        <div class='panel-lead'>%(start_time)s</div>
                    </div>
                </div>
                <div class='col s2'>
                    <div class='card-panel r'>
                        Time Taken
                        <div class='panel-lead'>%(duration)s seconds</div>
                    </div>
                </div>
                <div class='col s4'>
                    <div class='card-panel'>
                        <span class='right label cyan white-text'>Categories</span>
                        <p>&nbsp;</p>
                        <table>
                            <tr>
                                <th>Name</th>
                                <th>Passed</th>
                                <th>Failed</th>
                                <th>Errored</th>
                                <th>Skipped</th>
                            </tr>
                            <tr>
                                <td>All Suites</td>
                                <td class="pass">%(Pass)s</td>
                                <td class="fail">%(fail)s</td>
                                <td class="error">%(error)s</td>
                                <td class="skip"></td>
                            </tr>
                                <tr>
                                    <td id="unknown"></td>
                                    <td class="pass"></td>
                                    <td class="fail"></td>
                                    <td class="error"></td>
                                    <td class="skip"></td>
                                </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

    SCRIPT_JS = """
    <script>
        var test_suite_success = %(Pass)s;


        var statusGroup = {
            passParent: %(Pass)s,
            failParent: %(fail)s,
            fatalParent: 0,
            errorParent: %(error)s,
            warningParent: 0,
            skipParent: 0,
            exceptionsParent: 0,

            passChild: test_suite_success,
            failChild: %(fail)s,
            fatalChild: 0,
            errorChild: 0,
            warningChild: 0,
            skipChild: 0,
            infoChild: 0,
            exceptionsChild: 0,

            passGrandChild: 0,
            failGrandChild: 0,
            fatalGrandChild: 0,
            errorGrandChild: 0,
            warningGrandChild: 0,
            skipGrandChild: 0,
            infoGrandChild: 0,
            exceptionsGrandChild: 0,
        };

    </script>

    <script src='http://extentreports.com/resx/dist/js/extent.js' type='text/javascript'></script>


    <script type='text/javascript'>
        $(window).off("keydown");
    </script>
    """
    STYLESHEET_TMPL = """
    <style type="text/css">
        .node.level-1 ul {
            display: none;
        }
        .node.level-1.active ul {
            display: block;
        }
        .card-panel.environment th:first-child {
            width: 30%;
        }
        .small_img{
            height: 180px; 
            width: 100px; 
            padding: 10px;
            float: left;
            background-repeat: no-repeat; 
            background-position: center center; 
            background-size: cover; 
          } 
        .black_overlay{ 
            display: none; 
            position: absolute; 
            top: 0%; 
            left: 0%; 
            width: 100%; 
            height: 100%; 
            background-color: white; 
            z-index:1001; 
            -moz-opacity: 0.8; 
            opacity:.80; 
            filter: alpha(opacity=80);  
        } 
        .big_img { 
            cursor: pointer;
            display: none; 
            position: absolute; 
            height: 650px;
            left:50%; 
            top: 50%;
            margin: -300px 0px 0px -200px;
            z-index:1002; 
            overflow: auto; 
        }
    </style>
"""

    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_ATTRIBUTE_TMPL = """
    去掉
    <p class='attribute'><strong>%(name)s:</strong> %(value)s</p>
"""  # variables: (name, value)

    # ------------------------------------------------------------------------
    # Report
    #

    REPORT_TMPL = """
<p id='show_detail_line'>Show
<a href='javascript:showCase(0)'>Summary</a>
<a href='javascript:showCase(1)'>Failed</a>
<a href='javascript:showCase(2)'>All</a>
</p>
<table id='result_table'>
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>
<tr id='header_row'>
    <td>Test Group/Test case</td>
    <td>Count</td>
    <td>Pass</td>
    <td>Fail</td>
    <td>Error</td>
    <td>View</td>
    <td>Screenshot</td>
</tr>
%(test_list)s
<tr id='total_row'>
    <td>Total</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
</table>
"""  # variables: (test_list, count, Pass, fail, error)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(desc)s</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td><a href="javascript:showClassDetail('%(cid)s',%(count)s)">Detail</a></td>
    <td>&nbsp;</td>
</tr>
"""  # variables: (style, desc, count, Pass, fail, error, cid)

    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>
    <!--css div popup start-->
    <a class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')" >
        %(status)s</a>
    <div id='div_%(tid)s' class="popup_window">
        <div style='text-align: right; color:red;cursor:pointer'>
        <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none' " >
           [x]</a>
        </div>
        <pre>
        %(script)s
        </pre>
    </div>
    <!--css div popup end-->
    </td>
    <td align='center'>
    %(uescript)s
    </td>
</tr>
"""  # variables: (tid, Class, style, desc, status)
    REPORT_IMAGE = r"""
    <img class="small_img" src="%(screenshot)s"  onclick="document.getElementById('light_%(screenshot_id)s').style.display ='block';document.getElementById('fade_%(screenshot_id)s').style.display='block'"/>
    """

    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>%(status)s</td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_OUTPUT_TMPL = r"""
%(output)s
"""  # variables: (output)
    REPORT_TEST_OUTPUT_EXCEPT_TMPL= r"""
%(outputexcept)s
"""
    REPORT_TEST_OUTPUT_IMAGE = r""" 
%(screenshot)s
"""
    REPORT_TEST_OUTPUT_CASEID = r"""
%(case_id)s
"""
    # ------------------------------------------------------------------------
    # ENDING
    #

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""


# -------------------- The end of the Template class -------------------


TestResult = unittest.TestResult


class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.

    def __init__(self, verbosity=1):
        TestResult.__init__(self)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        # self.outputBuffer = StringIO.StringIO()
        self.outputBuffer = io.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')


class HTMLTestRunner(Template_mixin):
    """
    """

    def __init__(self, stream=sys.stdout, verbosity=1, title=None, description=None):
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description

        self.startTime = datetime.datetime.now()

    def run(self, test):
        "Run the given test case or test suite."
        result = _TestResult(self.verbosity)
        test(result)
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)
        # print >>sys.stderr, '\nTime Elapsed: %s' % (self.stopTime-self.startTime)
        print(sys.stderr, '\nTime Elapsed: %s' % (self.stopTime - self.startTime))
        return result

    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.__class__
            # if not rmap.has_key(cls):
            if not cls in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        if result.success_count: status.append('Pass %s' % result.success_count)
        if result.failure_count: status.append('Failure %s' % result.failure_count)
        if result.error_count:   status.append('Error %s' % result.error_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            ('Start Time', startTime),
            ('Duration', duration),
            ('Status', status),
        ]

    def generateReport(self, test, result):
        report_attrs = self.getReportAttributes(result)
        generator = 'HTMLTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        ending = self._generate_ending()
        dashboard_view = self._generate_dashboardView(report_attrs, result)
        scriptJS = self._generate_script(result)

        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
            dashboard_view=dashboard_view,
            script_js=scriptJS,
        )
        self.stream.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs):
        # 弃掉 HEADING_ATTRIBUTE_TMPL
        a_lines = []
        startTime = ""
        duration = ""
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
            startTime = value if name == "Start Time" else startTime
            duration = value if name == "Duration" else duration
        # 取出来Start Time、Duration、Status
        heading = self.NAV % dict(
            title=saxutils.escape(self.title),
            start_time=startTime,
            duration=duration,
            description=saxutils.escape(self.description),
        )
        return heading

    def _generate_script(self, result):
        scriptJS = self.SCRIPT_JS % dict(
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )
        return scriptJS

    def _generate_dashboardView(self, report_attrs, result):
        a_lines = []
        startTime = ""
        duration = ""
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
            startTime = value if name == "Start Time" else startTime
            duration = value if name == "Duration" else duration
        dashboard_view = self.DASHBOARD_VIEW % dict(
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            start_time=startTime,
            duration=duration,
        )
        return dashboard_view

    def _generate_report(self, result):
        rows = []
        row1s = []
        section_name = []
        categoryTbody = []
        categoryActive = []
        sortedResult = self.sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):
            # subtotal for a class
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            # desc = doc and '%s: %s' % (name, doc) or name
            desc = doc and '%s' % (name) or name
            #只选择最后的接口名
            desc=desc.split('.')[-1]

            # section中suite name
            sectionName = self.SECTION_SUIT_NAME % dict(
                desc=desc,
            )
            section_name.append(sectionName)

            testCollectionUlList = []
            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e, testCollectionUlList)

            if ne > 0:
                liTestActive = '<li class="test displayed active has-leaf error" status="error" bdd="false" test-id="' + desc + '_' + str(
                    cid + 1) + '">'
                statusSpan = '<span class="test-status right error">error</span>'
                nodeLevel = '<li class="node level-1 leaf error" status="error" test-id="' + desc + '_' + str(
                    cid + 1) + '">'
                categoryTbodyTd = '<span class="test-status error">error</span>'
            elif nf > 0:
                liTestActive = '<li class="test displayed active has-leaf fail" status="fail" bdd="false" test-id="' + desc + '_' + str(
                    cid + 1) + '">'
                statusSpan = '<span class="test-status right fail">fail</span>'
                nodeLevel = '<li class="node level-1 leaf fail" status="fail" test-id="' + desc + '_' + str(
                    cid + 1) + '">'
                categoryTbodyTd = '<span class="test-status fail">fail</span>'
            else:
                liTestActive = '<li class="test displayed active has-leaf pass" status="pass" bdd="true" test-id="' + desc + '_' + str(
                    cid + 1) + '">'
                statusSpan = '<span class="test-status right pass">pass</span>'
                nodeLevel = '<li class="node level-1 leaf pass" status="pass" test-id="' + desc + '_' + str(
                    cid + 1) + '">'
                categoryTbodyTd = '<span class="test-status pass">pass</span>'
            row1 = self.TEST_COLLECTION % dict(
                li_test_active=liTestActive,
                status_span=statusSpan,
                node_level=nodeLevel,
                desc=desc,
                doc=doc,
                count=np + nf + ne,
                Pass=np,
                fail=nf,
                error=ne,
                test_collection_ul_list=''.join(testCollectionUlList),
                cid='c%s' % (cid + 1),
            )
            row1s.append(row1)
            category_tbody = self.CATEGORY_TBODY % dict(
                name=name,
                desc=desc,
                start_time=self.startTime,
                cid=cid,
                category_tbody_td=categoryTbodyTd,
            )
            categoryTbody.append(category_tbody)

            category_active = self.CATEGORY_ACTIVE % dict(
                desc=desc,
                Pass=np,
                fail=nf,
                error=ne,
            )
            categoryActive.append(category_active)

        controlSection = self.CONTROL_SECTION % dict(
            suite_name=''.join(section_name)
        )
        viewCharts = self.VIEW_CHARTS % dict(
            pass_count=str(result.success_count),
            fail_count=str(result.failure_count),
            error_count=str(result.error_count),
        )
        subviewLeft = self.SUBVIEW_LEFT % dict(
            test_collection=''.join(row1s),
        )
        category_view = self.CATEGORY_VIEW % dict(
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            category_tbody=categoryTbody,
            category_active=categoryActive,
        )

        report = self.TEST_VIEW % dict(
            control_section=controlSection,
            view_charts=viewCharts,
            # test_list=''.join(rows),
            test_list=subviewLeft,
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.failure_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            category_view=category_view,
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, e, testCollectionUlList):
        # e.g. 'pt1.1', 'ft1.1', etc
        has_output = bool(o or e)
        tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        tmpl = has_output and self.TBODY or self.REPORT_TEST_NO_OUTPUT_TMPL

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            # uo = o.decode('latin-1')
            uo = str(o)
        else:
            uo = e
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            # ue = e.decode('latin-1')
            ue = e
        else:
            ue = e

        # ss = uo[uo.rfind('screenshot'):uo.rfind('.png') + 4]
        ssreg = re.compile(r'screenshot_.+?png')
        ss = ssreg.findall(uo)
        # ss = ';'.join(ss)
        #遇到[time:替换成<br/>[time:
        #output=saxutils.escape(uo + ue).replace(r'[time:','<br/>[time:'),
        '''
        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(uo + ue).replace(r'\r\n', '<br/>'),
        )
        images = []
        for ima in ss:
            image = self.REPORT_IMAGE % dict(
                # screenshot = saxutils.escape(uo+ue)
                screenshot_id=ima.split(".")[0],
                screenshot=saxutils.escape(ima)
            )
            images.append(image)
        images = ''.join(images)
        '''
        uescript = self.REPORT_TEST_OUTPUT_EXCEPT_TMPL % dict(
            outputexcept=saxutils.escape(ue),
        )
        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            output=saxutils.escape(uo).replace(r'[time:','<br/>[time:'),
        )

        tBody = self.TBODY % dict(
            script=script,
            uescript=uescript,
        )
        if n == 1:
            nodeLevel = '<li class="node level-1 leaf fail" status="fail" test-id="' + desc + '_' + str(
                tid) + '_' + str(cid + 1) + '">'
            statusSpan = '<span class="test-status right fail">fail</span>'
        elif n==2:
            nodeLevel = '<li class="node level-1 leaf error" status="error" test-id="' + desc + '_' + str(
                tid) + '_' + str(cid + 1) + '">'
            statusSpan = '<span class="test-status right error">error</span>'
        else:
            nodeLevel = '<li class="node level-1 leaf pass" status="pass" test-id="' + desc + '_' + str(
                tid) + '_' + str(cid + 1) + '">'
            statusSpan = '<span class="test-status right pass">pass</span>'
        tcll = self.TEST_COLLECTION_UL_LIST % dict(
            node_level=nodeLevel,
            status_span=statusSpan,
            desc=name,
            doc=doc,
            t_body=tBody,
        )
        testCollectionUlList.append(tcll)
        caseid = self.REPORT_TEST_OUTPUT_CASEID % dict(
            case_id=saxutils.escape(uo + ue)
        )
        row = tmpl % dict(
            tid=tid,
            Class=(n == 0 and 'hiddenRow' or 'none'),
            style=n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none'),
            desc=desc,
            script=script,
            # image = image[image.find("image"):(int(image.find("png"))+3)],
            uescript=uescript,
            caseid=caseid[caseid.find("case"):(int(caseid.find("case")) + 9)],
            status=self.STATUS[n],
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL


##############################################################################
# Facilities for running tests from the command line
##############################################################################

# Note: Reuse unittest.TestProgram to launch test. In the future we may
# build our own launcher to support more specific command line
# parameters like test title, CSS, etc.
class TestProgram(unittest.TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters.
    """

    def runTests(self):
        # Pick HTMLTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate HTMLTestRunner before we know self.verbosity.
        if self.testRunner is None:
            self.testRunner = HTMLTestRunner(verbosity=self.verbosity)
        unittest.TestProgram.runTests(self)


main = TestProgram

##############################################################################
# Executing this module from the command line
##############################################################################

if __name__ == "__main__":
    main(module=None)