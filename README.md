# Sticky Controller

Autodesk Maya sticky controller for animators.

A controller which is stuck on a selected vertex allowing to deformed one or
multiple geometries while following the geometry.
Useful for contacts, polish so silhouettes, correct penetrations, ...

## Installation

Download the repository and place it within the scripts directory of your maya
documents folder.

- Windows: ```C:/Users/username/Documents/maya/scripts```
- Mac OS: ```~/Library/Preferences/Autodesk/maya/scripts```
- Linux: ```~/maya/scripts```

Drag and drop the `install.py` file in the maya viewport to add the "Sticky"
button in current activated shelf.

## Quick start

### Create a sticky controller.

- Select one vertex of a geometry.
- Left click on the shelf button.
- You're done :)

A group called `STICKIES` will be created, you will find all your created
stickies within it.

### Edit a sticky.

If you **double left-click** on the shelf button a small Ui will pop-up allowing
to "edit" the stickies.

TIP: All actions are undoable.

#### 1 - Create stickies

Exactly like with the shelf button. Select one vertex and click on create
button.

#### 2 - Display stickies of the scene.

Just hit the `Refresh` button and the Ui will get all stickies in the scene.

TIP: All next steps can be done by right-clicking on the sticky you want in the
table.

#### 3 - Rename a sticky.

It will open a new window in which you can enter your new name. It preserves
does not break the animation.

#### 4 - Select sticky's controllers.

It will select both `slide_ctrl` and `sticky_ctrl`. Pretty useful when you've
lost it and want to focus your camera on them.

TIP: You can deform multiple geometries simultaneously with One sticky
controller.

Useful when you have clothes for example.

#### 5 - Select geometries deformed by the sticky.

Select geometries deformed by the sticky, to quickly know which sticky is
deforming what, or remove any geometry from the deformed geometries.

#### 6 - Add deformed geometries.

Select one or more geometries and hit the action in the menu. All geometries
will then be deformed the same way. There is a small "mesh" icon in the Ui with
a number. It displays how many geometries are deformed by the sticky.

#### 7 - Remove deformed geometries.

Select the geometries you don't want to be deformed anymore then hit the action
in the menu. It is easier to select the geometries with the `Select geometries`
action first, to be sure to remove the correct geometries.

#### 8 - Delete stickies.

Do I even need to explain ?

## Contributors

Arthur Bodart - https://www.linkedin.com/in/arthur-bodart-35a442b8/

Luca Amorosi - https://www.linkedin.com/in/luca-amorosi-234b70184/

