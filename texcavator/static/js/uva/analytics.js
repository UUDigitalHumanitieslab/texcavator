// FL-13-May-2013 Created
// FL-13-May-2013 Changed

// Logging with dojox.analytics for analysis of user behavior. 

<script type="text/javascript" src="dojotoolkit/dojo/dojo.js"
   data-dojo-config="parseOnLoad: true, sendInterval: 5000, analyticsUrl: 'http://server/path/to/dataLogger'"></script>

<script language="JavaScript" type="text/javascript">
   // include the analytics system
   dojo.require("dojox.analytics");

   // this plugin returns the information dojo collects when it launches
   dojo.require("dojox.analytics.plugins.dojo");

   // this plugin return the information the window has when it launches
   // and it also ties to a few events such as window.option
   dojo.require("dojox.analytics.plugins.window");

   // this plugin tracks console. message, It logs console.error, warn, and
   // info messages to the tracker.  It also defines console.rlog() which
   // can be used to log only to the server.  Note that if isDebug() is disabled
   // you will still see the console messages on the sever, but not in the actual
   // browser console.
   dojo.require("dojox.analytics.plugins.consoleMessages");

   // tracks where a mouse is on a page an what it is over, periodically sampling
   // and storing this data
   dojo.require("dojox.analytics.plugins.mouseOver");

   // tracks mouse clicks on the page
   dojo.require("dojox.analytics.plugins.mouseClick");

   // tracks when the user has gone idle
   dojo.require("dojox.analytics.plugins.idle");

 </script>

// [eof]
