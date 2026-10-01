hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

-- Catppuccin Mocha cursor theme (AUR: catppuccin-cursors-mocha). Swap the
-- "blue" accent for another flavor variant (e.g. "mauve", "lavender") if
-- you want a different look later — this is just the starting template.
hl.env("XCURSOR_THEME", "catppuccin-mocha-blue-cursors")
hl.env("HYPRCURSOR_THEME", "catppuccin-mocha-blue-cursors")

-- GTK/Qt theme unification (Catppuccin Mocha everywhere). GTK_THEME covers
-- apps that ignore ~/.config/gtk-3.0/settings.ini; QT_QPA_PLATFORMTHEME=gtk3
-- makes Qt apps (e.g. the polkit agent) follow the same GTK3 theme instead
-- of falling back to a plain default Qt style.
hl.env("GTK_THEME", "catppuccin-mocha-blue-standard+default")
hl.env("QT_QPA_PLATFORMTHEME", "gtk3")
