#!/usr/bin/python

import sys
import dbus
from optparse import OptionParser
import time

AMBTools_VERSION_MAJOR = 0
AMBTools_VERSION_MINOR = 1

def getBus():
    return dbus.SystemBus()
    # return dbus.SessionBus()

def getObject( bus, name ):
    session = None
    timeout = 0
    timeMax = 120
    while session == None:
        try:
            session = bus.get_object( name , "/" );

        except Exception as ex:
            sys.stdout.write( "[%s] waiting: %s is not available...\r" % (timeout, name ) )
            sys.stdout.flush()
            if timeout >= timeMax:
                sys.stdout.write("\nWaited too long for %s (not available, max wait is %s)...\n" % ( name, timeMax ))
                exit(-1)
            else:
                timeout = timeout + 1
                time.sleep(1)
                pass
    if timeout > 0:
        # We printed the waiting message so get a new line for following data:
        print
    return session

def getPropertyIF( bus, objectName ):
    timeout = 60
    session = getObject( bus, "org.automotive.message.broker" )
    managerIFSession = dbus.Interface( session, "org.automotive.Manager" );
    try:
        objectPaths = managerIFSession.FindObject( objectName );

    except Exception:
        print "Object %s is not defined, exiting." % objectName
        exit(-1)

    for objectPath in objectPaths:
        objectSession = bus.get_object("org.automotive.message.broker", objectPath )
        objectAsPropertyIF = dbus.Interface(objectSession, "org.freedesktop.DBus.Properties")
        return objectAsPropertyIF
    return None

def introspectProperty( objectName ):
    bus = getBus()
    session = getObject( bus, "org.automotive.message.broker" )
    managerIFSession = dbus.Interface( session, "org.automotive.Manager" );
    objectPaths = managerIFSession.FindObject( objectName );
    for objectPath in objectPaths:
        objectSession = bus.get_object("org.automotive.message.broker", objectPath )
        objectAsIntrospectableIF = dbus.Interface(objectSession, "org.freedesktop.DBus.Introspectable")
        return objectAsIntrospectableIF.Introspect()
    return None

def getList():
    bus         = getBus()
    ambSession = getObject( bus, "org.automotive.message.broker" )
    ambManagerIFSession = dbus.Interface( ambSession, "org.automotive.Manager" );
    return sorted(ambManagerIFSession.List());


def get( ambValueName, subValueName=None ):
    bus = getBus()
    ect = getPropertyIF( bus, ambValueName )
    return ect.Get( "org.automotive."+ambValueName, (ambValueName if subValueName == None else subValueName) )

def getAll( ambValueName ):
    bus = getBus()
    ect = getPropertyIF( bus, ambValueName )
    return ect.GetAll( "org.automotive."+ambValueName )

def set( ambValueName, ambSubValueName, value=None ):
    #
    #   Note: In some cases the name of the value set is NOT the same as the name of the property!
    #
    if value == None:
        value = ambSubValueName
        ambSubValueName = ambValueName
    elif ambSubValueName == None:
        value = value
        ambSubValueName = ambValueName
    bus = getBus()
    ect = getPropertyIF( bus, ambValueName )
    return ect.Set( "org.automotive."+ambValueName, ambSubValueName, value )

def onPropertiesChanged( ambValueName, signalHandler ):
    # Some property in this group changed
    bus = getBus()
    ect = getPropertyIF( bus, ambValueName )
    return ect.connect_to_signal( "PropertiesChanged", signalHandler )

def onPropertyChanged( ambValueName, signalHandler ):
    # *this* property changed...
    bus = getBus()
    ect = getPropertyIF( bus, ambValueName )
    return ect.connect_to_signal( ambValueName, signalHandler )

#-----------------------------------------------------------------------------------


def handler1(sender = None, *args, **kws ):
    print "Handler1 == Sender: %r" %( sender )
    for arg in args: print "arg %s" % arg
    for key in kws.keys(): print "keyword %s in %s" %(key, kws[key])
    # print "got signal from %s %s" %(args,kws["sender_keyword"])
    print "---"

def handler2(sender = None, *args, **kws ):
    print "Handler2 == Sender: %r" %( sender )
    for arg in args: print "arg %s" % arg
    for key in kws.keys(): print "keyword %s in %s" %(key, kws[key])
    # print "got signal from %s %s" %(args,kws["sender_keyword"])
    print "---"


def sayHelp():
    print "%s Help:\n" % sys.argv[0]
    print "help                                    -- display this help"
    print "get <AMBName> [<AMBSubName>]            -- Read a value from AMB database"
    print "set <AMBName> [<AMBSubName>] <value>    -- Send a value to AMB"
    print "                                           value can be on/off/true/false, 99.9 or 99 "
    print "list <regex>                            -- List all AMBNames containing or matching regex"
    print "                                           (Case insensitive)                            "
    print "show <AMBName>                          -- Show introspection information"
    print "listen <AMBName>                        -- Listen for and display value changes on name"
    print ""
    sys.exit(-1)


def main( argv ):
    print "%s Version %s.%s" % (argv[0], AMBTools_VERSION_MAJOR, AMBTools_VERSION_MINOR)
    if len(argv) < 3:
        sayHelp()

    command = argv[1].lower()
    ambName = argv[2]

    # amb <set|get|show> <ambIdentifier> ...
    if command=="get" and (len(argv) == 3 or len(argv)==4):
        ambName = argv[2]
        ambSubName = argv[3] if len(argv)==4 else None
        item = get(ambName, ambSubName)
        value = int(item) if type(item) is dbus.Byte else item
        print "(%s) %s" % (type(item), value)

    elif command=="set" and (len(argv) == 4 or len(argv)==5):
        ambName = argv[2]
        ambSubName = argv[3] if len(argv)==5 else None
        value = (argv[4] if len(argv)==5 else argv[3]).lower()
        if value=="on" or value=="true":
            value=True
        elif value=="off" or value=="false":
            value=False
        elif value.find(".")>=0:
            value=float(value)
        else:
            value = int(value)
        # print "set( %s, %s, %s )" % ( ambName, ambSubName, value )
        try:
            set( ambName, ambSubName, value )
        except dbus.exceptions.DBusException as e:
            set(ambName, ambSubName, dbus.Byte(value) )
            pass

    elif command=="list" and (len(argv)==2 or len(argv)==3):
        # amb list <regexList>
        import re
        p = re.compile( argv[2], re.IGNORECASE ) if len(argv) > 2 else None
        for name in getList():
            if p==None or p.search(name):
                print "%s" % name

    elif command=="show" and len(argv)==3:
        # amb show <ambIdentifier>
        print "Introspect %s: \n%s" % (argv[2], introspectProperty( argv[2] ))

    elif command=="listen" and len(argv)==3:
        # amb listen <ambIdentifier>
        print "This option does not work correctly at this time (glib problems on Tizen)"
        #
        # -- Set up event loop so signals can work
        #
        # from dbus import gobject_service
        from dbus import glib
        from dbus.mainloop.glib import DBusGMainLoop
        DBusGMainLoop(set_as_default=True)

        onPropertyChanged("DirectionIndicationMS", handler1 )
        onPropertyChanged("DirectionIndicationINST", handler2 )
        mainloop = glib.DBusGMainLoop()
        mainloop.run()

    else:
        sayHelp()

if __name__ == "__main__":
    import signal

    def signal_handler(signal, frame):
        print
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    main( sys.argv )

