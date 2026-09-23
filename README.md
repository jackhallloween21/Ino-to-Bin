# ino2bin-site

Compiles Arduino `.ino` sketches into `.bin` firmware for ESP8266/ESP32 using
[arduino-cli](https://arduino.github.io/arduino-cli/latest/), and publishes the
results as a downloadable site via GitHub Pages — automatically, on every push.

## How it works

1. Drop a sketch into `sketches/<name>/<name>.ino` (folder and file name must match —
   this is an Arduino CLI requirement, and `ino2bin.py` will tell you clearly if they don't).
2. Push to `main`.
3. GitHub Actions (`.github/workflows/build.yml`) installs `arduino-cli`, the ESP8266
   and ESP32 board cores, and the libraries listed in the workflow, then compiles
   **every** sketch under `sketches/` for both boards using `ino2bin.py`.
4. Compiled `.bin` files land in `docs/downloads/`, and `scripts/generate_index.py`
   builds `docs/index.html` listing them with sizes and a download link.
5. GitHub Pages serves `docs/` as the site.

## Adding a new sketch

```
sketches/
  my_project/
    my_project.ino
```

If your sketch needs a library not already installed in the workflow, add an
`arduino-cli lib install "Library Name"` line under **Install common libraries**
in `.github/workflows/build.yml`.

## Running locally

```
pip install --upgrade pip   # no extra dependencies needed, ino2bin.py is stdlib-only
python ino2bin.py --sketch sketches/rgb_pwm_controller --board esp8266:esp8266:nodemcuv2
```

Requires `arduino-cli` installed and on your PATH, with the relevant board core
already installed (`arduino-cli core install esp8266:esp8266`).

### Common board FQBNs

| Board                  | FQBN                          |
|-------------------------|--------------------------------|
| ESP8266 NodeMCU 1.0     | `esp8266:esp8266:nodemcuv2`   |
| ESP8266 Generic         | `esp8266:esp8266:generic`     |
| ESP32 Dev Module        | `esp32:esp32:esp32`           |

## Enabling GitHub Pages (one-time setup)

In your repo: **Settings → Pages → Source → GitHub Actions**. The workflow's
`deploy` job will then publish `docs/` automatically after every successful build.
