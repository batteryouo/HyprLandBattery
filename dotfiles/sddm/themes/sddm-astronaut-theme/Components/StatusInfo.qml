// Battery and network status, read directly from sysfs since the SDDM
// greeter has no shell/session access to upower or NetworkManager.
import QtQuick 2.15
import QtQuick.Controls 2.15

Column {
    id: statusInfo

    spacing: 2
    property real baseSize: root.font.pointSize

    // Hardware-specific sysfs paths; update these if the battery or
    // network interface name changes (check with `upower -e` / `ip link`).
    property string batteryPath: "/sys/class/power_supply/BAT0/capacity"
    property string netInterface: "wlp0s20f3"

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

    Label {
        id: batteryLabel

        anchors.right: parent.right
        font.pointSize: statusInfo.baseSize
        color: config.DateTextColor
        renderType: Text.QtRendering

        function update() {
            var capacity = statusInfo.readFile(statusInfo.batteryPath)
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
            var state = statusInfo.readFile("/sys/class/net/" + statusInfo.netInterface + "/operstate")
            text = state === "up" ? "󰖩 Online" : "󰖪 Offline"
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
