local options = require("config.options")

hl.on("hyprland.start", function()
    hl.exec_cmd(options.terminal)
    hl.exec_cmd("nm-applet")
    hl.exec_cmd("waybar")
    hl.exec_cmd("hyprpaper")
    hl.exec_cmd("mako")
    hl.exec_cmd("/usr/lib/polkit-kde-authentication-agent-1")
    hl.exec_cmd("hyprpm reload")
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    -- hyprswitch v5 requires its daemon to be initialized before `gui` is used.
    -- `hl.exec_cmd` already starts commands asynchronously, so no trailing `&` is needed.
    hl.exec_cmd("hyprswitch init --show-title --size-factor 6")
end)
