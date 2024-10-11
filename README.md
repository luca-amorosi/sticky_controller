Sticky Controller
====

[![GitHub Release](https://img.shields.io/github/v/release/luca-amorosi/sticky_controller)](http://github.com/luca-amorosi/sticky_controller/releases)
[![GitHub License](https://img.shields.io/github/license/luca-amorosi/sticky_controller)](https://github.com/luca-amorosi/sticky_controller/blob/main/LICENSE)

[![arthur_bodart](https://img.shields.io/badge/Author-Arthur%20Bodart-darkgreen)](https://www.linkedin.com/in/arthur-bodart-35a442b8/)
[![luca_amorosi](https://img.shields.io/badge/Author-Luca%20Amorosi-darkgreen)](https://www.linkedin.com/in/luca-amorosi-234b70184/)


Autodesk Maya sticky controller for animators.

A controller which is stuck on a selected vertex allowing to deform and follow a
one or multiple geometries without double transformation. Useful for contacts,
polishing silhouettes, correct penetrations, ...

## :desktop_computer: Installation 

1) :floppy_disk: Get a copy of the [latest release](http://github.com/luca-amorosi/sticky_controller/releases)
2) Place it within the scripts directory of your maya documents folder.
   - Windows: ```C:/Users/username/Documents/maya/scripts```
   - Mac OS: ```~/Library/Preferences/Autodesk/maya/scripts```
   - Linux: ```~/maya/scripts```
3) Drag and drop the `scripts/install.py` file in the maya viewport to add the "Sticky"
button in current activated shelf.

## :gear: Usage 

You can either **left-click** on the shelf button to create a sticky on selected
vertex. Or you can **double left-click** on the shelf button to open a small Ui
to "edit" the stickies.

:fire:`All actions are undoable.`:fire:

- [Create stickies](#create-stickies)
- [Display stickies](#display-stickies-of-the-scene)
- [Rename](#rename-a-sticky)
- [Select controllers](#select-stickys-controllers)
- [Select geometries](#select-geometries-deformed-by-the-sticky)
- [Add deformed geometries](#add-deformed-geometries)
- [Remove deformed geometries](#remove-deformed-geometries)
- [Delete stickies](#delete-stickies)

---
### Create stickies

Select one vertex of one geometry and hit the shelf button or the create button
in the Ui.
A group called `STICKIES` will be created, you will find all your created
stickies within it.

---
### Display stickies of the scene.

Just hit the `Refresh` button and the Ui will get all stickies in the scene.

TIP: All next steps can be done by right-clicking on the sticky you want in the
table.

---
### Rename a sticky.

It will open a new window in which you can enter your new name. It preserves
does not break the animation.

---
### Select sticky's controllers.

It will select both `slide_ctrl` and `sticky_ctrl`. Pretty useful when you've
lost your controllers and want to focus your camera on them.

TIP: You can deform multiple geometries simultaneously with One sticky
controller.

Useful when you have clothes for example.

---
### Select geometries deformed by the sticky.

Select geometries deformed by the sticky, to quickly know which sticky is
deforming what, or remove any geometry from the deformed geometries.

---
### Add deformed geometries.

Select one or more geometries and hit the action in the menu. All geometries
will then be deformed the same way. There is a small "mesh" icon in the Ui with
a number. It displays how many geometries are deformed by the sticky.

---
### Remove deformed geometries.

Select the geometries you don't want to be deformed anymore then hit the action
in the menu. It is easier to select the geometries with the `Select geometries`
action first, to be sure to remove the correct geometries.

---
### Delete stickies.

Do I even need to explain ?