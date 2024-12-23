# How the model would work:

## Glossary
- **Environment**
- **Camera**
- **Routine/Loop**
- **Subsprite**

## Environment

Depending on the user's needs, the game could run in one of three modes:
- **Static camera**: The pet and environment are fully contained within the screen's bounds at all times. This reduces the need for complex camera motion/control and environment setup but greatly limits what you can put and do inside the environment.
- **Dynamic camera, centered view**: The environment expands beyond the boundary of the screen, but the pet stays fixed at the center at all times. Probably the best balance between complexity, performance, and interactivity.
- **Dynamic camera, dynamic view**: The camera and the pet move freely throughout the environment. Pushes the limits of Micropython but would still be worth trying regardless.

Aside from those, the game would support subenvironments for special cutscenes or minigames. How the game interacts within those subenvironments could be configured to be completely separate from the main game.

## Timings and Routines

The current plan is to run three non-blocking update routines with different schedules, as well as task delegation across the cores available. This project is originally based upon the **RP2040** microprocessor, so a plan for two cores would be the following:

### Main environment
1. **The main graphics update loop**:
    - Preferably 30+ times per second, can be faster or slower depending on performance.
    - Collects all environment components (including assembling sprites from components based on position and rotation, or text that aids in control) and prints it onto the screen.
    - Runs on **Core 0**.

2. **The immediate interactions loop**:
    - Preferably once a second.
    - Takes care of the interactions between the sprite, user, and the environment. Takes care of handling user input, interpreting it, and giving it to the graphics update loop.
    - Takes in data from the global update to respond to changes (schedules, weather, etc.), and lets the main graphics update loop update accordingly.
    - Maintains a stack to keep track of overlapping assets.
    - Maintains the clock
    - Runs on **Core 1**.

3. **The global update loop**:
    - Preferably once every 10 seconds or longer.
    - Takes care of reading the sensors, syncing the clock, interpreting it based on a given schedule, and adding some randomness/variation (sleeping, hunger, etc.).
    - Runs on **Core 1**.

### Subenvironments (minigames and special events)
Pretty much the same as the main environment, except need to:
- Allocate resources and handle garbage collection afterward.
- The global update loop would still handle responses to external sensors as needed.

## Data Type

Currently, three data structures are planned, and one is supported by the accompanying sprite editor:
- **Static sprites [DONE]**: Basic elemental sprites for building the environment in the form of a tuple containing:
    - Dimensions: *Tuple* with data on (width, height).
    - Data: *ByteArray*.
- **Dynamic sprites**: These sprites are a series of static sprites that change based on how the user wants. Uses more memory and redundant data but is easier to implement.
    - Dimensions: *Tuple* with data on (width, height).
    - Animation: *Dictionary* with values being an *Array* containing pointers to static sprites for a specific case.
    - A better approach would be containerizing everything in a class but might lead to reference issues.
- **Constructed sprites [TODO]**: This is the most computationally expensive and difficult to configure sprite, but if properly executed will create extremely realistic and pleasing sprites. Recommended for main sprites such as the pets.
    - Total dimensions: *Tuple* with data on (width, height), for the dimension of the fully constructed sprites.
    - Subsprite data: *Dictionary* with data on the dimensions of each subsprite as well as the *hinge point*, where things are attached.
    - Hinge rules: no idea how this would be executed for now.
    - Animation: *Dictionary* with:
        - Keys: Emotions and scenarios (e.g. excited, sad, hungry).
        - Values: Pointers to *Dictionaries*.
            - Key: Name of subsprites (e.g. tail, head, etc.).
            - Values: *List* with pointers to each subsprite.
    - _Maximum reusability_ and _space saving_ at the cost of complexity.
    - Requires a massive upgrade in the editing software:
        - Add flow control.
        - Subsprite management and saving, all in one workspace.