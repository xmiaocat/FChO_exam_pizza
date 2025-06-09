# FChO Exam Pizza

This is a digital realisation of the FChO Exam Pizza, a timer for exams 
overseen by members of the 
[FChO](https://www.fcho.de/) (Förderverein der Chemie-Olympiade e.V.).

The pizza timer was first introduced during the national finals of the
student competition
["Chemie - die stimmt!"](https://www.chemie-die-stimmt.de/)
in 2019, originally as a hand-drawn circle on a blackboard,
which is filled slice by slice with pizza toppings as the exam progresses.

This digital version is meant to be used in a similar way, but with
more flexibility and convenience.

---

## Features

- **Configurable exam length** (`total_hours`) and slice size (`div_hour`)  
- **Custom pizza images** (PNG), with **random** or **cycle** change policies  
- **Resizable window**—your canvas stays centered  
- **TOML configuration** with sensible defaults & validation  

---

## Requirements

- **Python 3.11+** (for `tomllib`)
- [pygame](https://www.pygame.org/), tested with version 2.6.1
- (optional) **toml** package if you back-port to Python 3.10 or earlier (not tested)

## Installation
- Clone or download this repository.
- (optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
- Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
- (optional) Install the `toml` package if you are using Python 3.10 or earlier:
   ```bash
   pip install toml
   ```
- Make sure there’s an `images/` folder alongside `pizza_timer.py` 
containing at least `000_default.png` (and any other `.png` you list in your config).
Add your own pizza images there if you like.
- Create or edit `config.toml` (see below).

## Configuration (`config.toml`)

Place a toml file (default: `config.toml`) in the same directory as `pizza_timer.py`.
The obligatory and most important optional fields are:

```toml
# total exam length in hours (obligatory)
total_hours = 3.5

[config]
# slice length in hours (default: 0.5)
div_hour = 0.5

# start the timer with a specific duration in seconds
# (default: "none" → start with the total exam time)
start_second = "none"

# list your PNGs (or use "all" to load every .png in ./images)
# (default: ["000_default.png"])
pizza_images = ["000_default.png", "candy.png", "labware.png"]

# start index in that list (default: 0)
pizza_init_idx = 0

# when to change image (default: "none" → same as div_hour)
pizza_change_interval = "none"

# "random" or "cycle" (default: "random")
pizza_change_policy = "random"
```

Other parameters can be found in the `config.example.toml` file.

Omit any key to accept its default. To get `None` in Python for 
optional fields (e.g. `start_second` or `pizza_change_interval`), 
set the TOML value to "none" (string).

## Usage

Run from the command line, optionally passing your config file:
```bash
python pizza_timer.py [path/to/config.toml]
```
If you omit the path, it will look for ./config.toml.
Close the window or press Esc to quit.

## License & Contribution

Feel free to open issues or PRs on GitHub.
All contributions are welcome—whether it’s new slice-styles, 
additional policies, or bug-fixes!

