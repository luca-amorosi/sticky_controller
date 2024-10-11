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

1) :minidisc: Get a copy of the [latest release](http://github.com/luca-amorosi/sticky_controller/releases)
2) :open_file_folder: Place it within the scripts directory of your maya documents folder.
   - Windows: ```C:/Users/username/Documents/maya/scripts```
   - Mac OS: ```~/Library/Preferences/Autodesk/maya/scripts```
   - Linux: ```~/maya/scripts```
3) :arrow_right: Drag and drop the `scripts/install.py` file in the maya viewport to add the "Sticky"
button in current activated shelf.


## :gear: Tools 

You can either **left-click** on the shelf button to create a sticky on selected
vertex. Or you can **double left-click** on the shelf button to open a small Ui
to "edit" the stickies.

:fire: `TIP: All actions are undoable !`:fire:

- [Create stickies](#create-stickies)
- [Rename](#rename-a-sticky)
- [Select controllers](#select-stickys-controllers)
- [Select geometries](#select-geometries-deformed-by-the-sticky)
- [Add deformed geometries](#add-deformed-geometries)
- [Remove deformed geometries](#remove-deformed-geometries)
- [Delete stickies](#delete-stickies)

## User Interface

It has a `Create` button to ... create stickies and `Reload` button to display all stickies currently in the scene. 

There is a small View in which you can see the stickies of the scene and some information about them:
1) Checkbox to enable/disable the sticky's deformation.
2) The name of the sticky.
3) The number of geometries it currently deforms.
4) If one of the controller of the sticky has keyframes or not. 

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/sticku_ui_columns.png)![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/right_click_actions.png)

This view also has a **right-click** context menu with different actions to edit the view's current selected sticky.

Version of the tool is also noted in the window title.

---
### Create stickies

Select one vertex of one geometry and hit the shelf button or the create button
in the Ui.
A group called `STICKIES` will be created, you will find all your stickies
within it.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/create_sticky.gif)

---
### Rename a sticky.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/action_rename.png)

It will open a new window in which you can enter your new name.

:fire:`TIP: Animation are preserved !`:fire:

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/rename.gif)

---
### Select sticky's controllers.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/action_select_controller.png)

It will select both `slide_ctrl` and `sticky_ctrl`. Pretty useful when you've
lost your controllers and want to focus your camera on them.

---
### Select geometries deformed by the sticky.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/action_select_geometries.png)

Select geometries deformed by the sticky, to quickly know which sticky is
deforming what, or remove any geometry from the deformed geometries.

:fire:`TIP: You can deform multiple geometries simultaneously with One sticky
controller. Useful when you have clothes for example.`:fire: 

---
### Add deformed geometries.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/action_deform_geometries.png)

Select one or more geometries and hit the action in the menu. All geometries
will then be deformed the same way. There is a small "mesh" icon in the Ui with
a number. It displays how many geometries are deformed by the sticky.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/add_deformed_geometry.gif)

---
### Remove deformed geometries.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/action_remove_geometries.png)

Select the geometries you don't want to be deformed anymore then hit the action
in the menu.

:fire:`It is easier to select the geometries with the "Select geometries" action first, to be sure to remove the correct geometries. !`:fire:

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/remove_deformed_geometry.gif)

---
### Delete stickies.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/action_delete.png)

Do I even need to explain :upside_down_face: ?

:fire:`All actions are undoable !`:fire:


## :gear: Usage

### Enable and disable stickies

Sticky can be "turn On or Off" by toggling the checkbox in the first colum of the Ui.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/enable_disable_sticky.gif)

### Radius

The `radius` of the sticky can be changed to determine the area of deformation.

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/radius.gif)

### Slide controller.

Kind of hard to explain, could you whatch the gif pwease :raised_hands:  

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/radius.gif)

:warning:`Moving too far away the slide_ctrl from the base point (where the sticky was initially created) will cause weird behaviors while moving the main controller !`:warning:

:fire:`TIP: Very usefull to simulate contacts, a finger tip on a cheek for example ! While the sticky_ctrl is deforming the cheek, you can constraint the slide_ctrl to the finger tip`:fire:

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/slide_example.gif)


### Falloff mode

- `Volume`: Deformation is based on a 3D volume of a sphere. Every geometry within this "sphere" will be deformed.
- `Surface`: Deformation is based on a region that conforms to the contours/edges of the geometry's surface.

:fire:`TIP: "Surface" mode is usefull to separate the upper lip from the bottom lip on a character's face !`:fire:

![](https://github.com/luca-amorosi/sticky_controller/blob/main/docs/images/falloff_mode.gif)


