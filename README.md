# linux-shimeji-flickerfix

A personal fork of `estenv/linux-shimeji` with small practical fixes for running on a modern Ubuntu desktop.

## What changed in this fork

### Flicker reduction experiment
This fork removes an old visibility toggle in `src/com/group_finity/mascot/Mascot.java`:

- upstream hid the mascot window on specific ticks with `setVisible(false)`
- on modern compositors, that behavior can show up as visible flicker while the mascot moves
- this fork keeps the mascot visible and relies on the normal image update path instead

This is intended to reduce the obvious blinking/flicker seen on Ubuntu GNOME/X11. It is **not** a guarantee that all rendering issues are solved, because the codebase is still old Java/X11 code.

### Modern build compatibility
This fork also updates `build.xml` so the project can be rebuilt with a current JDK + Ant toolchain:

- `source="8"`
- `target="8"`
- `debuglevel="lines,vars,source"`

That means you can rebuild on a modern Ubuntu system without needing an old Java 6 era setup.

## Current status

- Best suited for **X11 sessions**
- Still a legacy codebase
- Wayland support is not expected
- Rendering behavior may still vary by compositor / GPU / desktop environment

![Shimeji for Linux](http://i.imgur.com/efHyX.png "Shimeji for Linux")

## Requirements

A compositing manager is still recommended for old X11 desktops.

For this fork on modern Ubuntu, a practical setup is:

- X11 session
- `openjdk-21-jdk` or another current JDK
- `ant`

Example install:

```bash
sudo apt-get update
sudo apt-get install -y openjdk-21-jdk ant
```

## Usage

Clone the repository:

```bash
git clone https://github.com/ngoc-thu/linux-shimeji-flickerfix.git
cd linux-shimeji-flickerfix
```

Run it:

```bash
./launch.sh
```

Build it:

```bash
ant clean jar
```

A prebuilt `Shimeji.jar` is included, but rebuilding is recommended if you modify the source.

## Configuration

- `window.conf` — set window dimensions to match your window decorations. If you're using a plain WM with no decorations, zero on all values or an empty file should be accurate.
- `titles.conf` — enter window titles, one per line, case insensitive. The mascots will interact with these windows only. If no window titles are specified, all windows will be interacted with. Leaving this file empty should be ideal for most people.

For more information refer to the configuration files.

## Obtaining more Shimejis

You can find thousands on DeviantArt and Pixiv (tag: `しめじ`). This version uses Japanese `Actions.xml` and `Behavior.xml` files.

To navigate the XML files more comfortably, using an English version from the Shimeji-EE project as a roadmap can still help.

A conversion file for English XML files used in the EE version is included and any ShimejiEE mascot can be made fully functional with this version. Make sure you use a Japanese `Mascot.xsd` XML schema after the conversion, do not replace it with the English one. The filenames read by this version are the same as in the current official Shimeji: `Actions.xml` and `Behavior.xml`.

Keep in mind:

- all images should go into the `img` directory
- no subdirectories inside `img` are read
- the same rule applies to configurations and the `conf` directory

You will find `conv.sed` in the `conf` directory.

## Known issues

- This fork only attempts a small, targeted flicker reduction. It does **not** modernize the rendering stack.
- Wayland sessions are still not a realistic target for this codebase.
- If you encounter trayicon-sized artifacts in the top-left corner of your screen, it's caused by an issue with Compton/XCompmgr and Java system tray spawning. The original author wrote a Compton patch for that issue instead of solving it inside this project.

## Original project note

The upstream project is archived and described by its author as ancient/legacy code. This fork only makes it easier to rebuild and test a targeted flicker-related behavior change on modern Ubuntu.

## License

This project inherits the ZLIB/LIBPNG license of the original Shimeji.

The included Java Native Access library is licensed under the LGPL. The Mozilla Rhino Javascript Engine is licensed under the Mozilla Public License.
