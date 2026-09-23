if hl.plugin.hyprbars == nil then
    return
end

hl.config({
    plugin = {
        hyprbars = {
            enabled = true,
            bar_height = 30,
            bar_color = "rgba(1e1e2eee)",
            bar_blur = true,
            bar_title_enabled = true,
            bar_text_size = 11,
            bar_text_weight = "medium",
            bar_text_font = "Sans",
            bar_text_align = "center",
            bar_buttons_alignment = "right",
            bar_padding = 8,
            bar_button_padding = 6,
            col = {
                text = "rgba(cdd6f4ff)",
            },
            on_double_click =
                [[hyprctl dispatch 'hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" })']],
        },
    },
})

hl.plugin.hyprbars.add_button({
    bg_color = "rgb(f38ba8)",
    fg_color = "rgb(1e1e2e)",
    size = 12,
    icon = "×",
    action = "hyprctl dispatch 'hl.dsp.window.close()'",
})

hl.plugin.hyprbars.add_button({
    bg_color = "rgb(f9e2af)",
    fg_color = "rgb(1e1e2e)",
    size = 12,
    icon = "□",
    action =
        [[hyprctl dispatch 'hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" })']],
})

hl.plugin.hyprbars.add_button({
    bg_color = "rgb(a6e3a1)",
    fg_color = "rgb(1e1e2e)",
    size = 12,
    icon = "—",
    action =
        [[hyprctl dispatch 'hl.dsp.window.float({ action = "toggle" })']],
})
