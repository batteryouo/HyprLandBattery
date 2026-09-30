// Battery and network status, read straight from sysfs and procfs: the
// greeter runs before any session exists, so there is no upower or
// NetworkManager to ask. Needs QML_XHR_ALLOW_FILE_READ=1, which SDDM passes
// through GreeterEnvironment.
import QtQuick 2.15
import QtQuick.Controls 2.15

Column {
    id: statusInfo

    spacing: 2
    property real baseSize: root.font.pointSize

    // XMLHttpRequest cannot list a directory, so the battery cannot be
    // discovered by globbing /sys/class/power_supply. Probe the names Linux
    // actually gives a primary battery instead.
    readonly property var batteryNames: ["BAT0", "BAT1", "BAT2", "CMB0", "CMB1", "macsmc-battery"]

    function readFile(path) {
        var xhr = new XMLHttpRequest()
        xhr.open("GET", "file://" + path, false)
        try {
            xhr.send()
            return xhr.responseText ? xhr.responseText.trim() : ""
        } catch (e) {
            return ""
        }
    }

    function batteryCapacity() {
        for (var i = 0; i < batteryNames.length; i++) {
            var capacity = readFile("/sys/class/power_supply/" + batteryNames[i] + "/capacity")
            if (capacity !== "")
                return capacity
        }
        return ""
    }

    // Name of the interface holding the default route, or "" when offline.
    // Destination 00000000 marks the default route.
    function defaultRouteInterface() {
        var lines = readFile("/proc/net/route").split("\n")
        for (var i = 1; i < lines.length; i++) {
            var fields = lines[i].trim().split(/\s+/)
            if (fields.length > 1 && fields[1] === "00000000")
                return fields[0]
        }
        return ""
    }

    Label {
        id: batteryLabel

        anchors.right: parent.right
        font.pointSize: statusInfo.baseSize
        color: config.DateTextColor
        renderType: Text.QtRendering
        visible: text !== ""

        function update() {
            var capacity = statusInfo.batteryCapacity()
            text = capacity !== "" ? "󰁹 " + capacity + "%" : ""
        }
    }

    Label {
        id: networkLabel

        anchors.right: parent.right
        font.pointSize: statusInfo.baseSize
        color: config.DateTextColor
        renderType: Text.QtRendering

        function update() {
            var iface = statusInfo.defaultRouteInterface()
            if (iface === "")
                text = "󰖪 Offline"
            else if (iface.charAt(0) === "w")
                text = "󰖩 Online"
            else
                text = "󰈀 Online"
        }
    }

    Timer {
        interval: 10000
        repeat: true
        running: true
        onTriggered: {
            batteryLabel.update()
            networkLabel.update()
        }
    }

    Component.onCompleted: {
        batteryLabel.update()
        networkLabel.update()
    }
}
