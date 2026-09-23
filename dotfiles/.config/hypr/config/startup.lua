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
    -- Kill any stale/crashed instance first so a leftover socket can't block a fresh
    -- daemon from binding (the usual cause of "Daemon not running" despite this exec).
    -- Log to a file instead of /dev/null so a future failure is actually diagnosable.
    hl.exec_cmd("pkill -x hyprswitch; nohup hyprswitch init --show-title --size-factor 6 >\"$XDG_RUNTIME_DIR/hyprswitch-init.log\" 2>&1 &")
end)
