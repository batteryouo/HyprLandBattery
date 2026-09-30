// Avatar that follows whatever username is currently typed (or picked from
// the dropdown), falling back to the last-logged-in user's picture.
// Reads SDDM's own userModel, so it needs no config of its own: a picture
// shows up as soon as /usr/share/sddm/faces/<user>.face.icon exists.
//
// The round shape is baked into that file's alpha channel rather than masked
// here, because Qt6 MultiEffect mask rendering produced nothing at all in
// this greeter build.
import QtQuick 2.15

Item {
    id: avatarRoot

    property string typedUsername: ""
    property url defaultIcon: ""
    property var userList: []

    function iconFor(name) {
        if (name !== "") {
            for (var i = 0; i < userList.length; i++) {
                if (userList[i].name === name || userList[i].realName === name)
                    return userList[i].icon
            }
        }
        return defaultIcon
    }

    Repeater {
        model: userModel
        Item {
            Component.onCompleted: {
                // Reassigning the same (in-place mutated) array reference does
                // not reliably notify QML bindings, so build a fresh array.
                avatarRoot.userList = avatarRoot.userList.concat([{
                    name: model.name,
                    realName: model.realName || "",
                    icon: model.icon
                }])
                if (index === userModel.lastIndex)
                    avatarRoot.defaultIcon = model.icon
            }
        }
    }

    Image {
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        smooth: true
        asynchronous: true
        source: avatarRoot.iconFor(avatarRoot.typedUsername)
    }
}
