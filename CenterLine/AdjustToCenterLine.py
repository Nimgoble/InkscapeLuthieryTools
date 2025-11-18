#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [YEAR] [YOUR NAME], [YOUR EMAIL]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
This extension changes the stroke of all selected paths depending on its node number parity.
"""

import inkex
import json
import math


"""Align an object along the center line."""
class AdjustToCenterLineExtension(inkex.EffectExtension):
    def __init__(self):
        inkex.Effect.__init__(self);
    
    def add_arguments(self, pars):
        pars.add_argument("--center_line_name", type=str, default="centerline");
        pars.add_argument("--center_line_type", type=str, default="1");
    
    def effect(self):
        if(self.options.ids is None or len(self.options.ids) == 0):
            inkex.utils.debug("No objects selected.");
            return;

        centerLine = self.svg.getElementById(self.options.center_line_name);
        if(centerLine is None):
            inkex.utils.debug(f"Center line with id '{self.options.center_line_name}' not found.");
            return;
    
        self.printObject(centerLine);
        
        for selected in self.svg.selected.values():
            inkex.utils.debug(f"Selected object: {selected.get_id()}");
            self.centerObjectOnCenterLine(selected, centerLine);
    
    
    def centerObjectOnCenterLine(self, object, centerLine, overrideBoundingBox = None):
        self.printObjectPositionAndSize(object);
        if isinstance(object, inkex.Group):
            for child in object.iterchildren():
                self.centerObjectOnCenterLine(child, centerLine, overrideBoundingBox if overrideBoundingBox is not None else object.bounding_box());
            self.printObjectPositionAndSize(object);
            return;

        selectedBoundingBox = overrideBoundingBox if overrideBoundingBox is not None else object.bounding_box();
        centerLineBoundingBox = centerLine.bounding_box();
        selectedPath = object.path;
        inkex.utils.debug(f"Selected object center position: ({selectedBoundingBox.center_x}, {selectedBoundingBox.center_y})");
        inkex.utils.debug(f"Center line center position: ({centerLineBoundingBox.center_x}, {centerLineBoundingBox.center_y})");
        if(self.options.center_line_type == "1"): #horizontal center line
            # Align to center Y of center line 
            transformY = centerLineBoundingBox.center_y - selectedBoundingBox.center_y;
            selectedPath.translate(0, transformY, True);
            inkex.utils.debug(f"Moved object '{object.get_id()}' vertically by {transformY}.");
        elif(self.options.center_line_type == "2"): #vertical center line
            # Align to center X of center line
            transformX = centerLineBoundingBox.center_x - selectedBoundingBox.center_x;
            selectedPath.translate(transformX, 0, True);
            inkex.utils.debug(f"Moved object '{object.get_id()}' horizontally by {transformX}.");
        
        object.path = selectedPath;
        self.printObjectPositionAndSize(object);
    
    
    def printObjectPositionAndSize(self, object):
        try:
            boundingBox = object.bounding_box();
            inkex.utils.debug(f"Object '{object.get_id()}' position and size: ({boundingBox.center_x}, {boundingBox.center_y}), w: {boundingBox.width}, h: {boundingBox.height}");
        except Exception as e:
            inkex.utils.debug(f"Unable to get bounding box for object '{object.get_id()}': {e}");

    def printObject(self, object):
        inkex.utils.debug(object);
        try:
            objJson = json.dumps(object);
            inkex.utils.debug(objJson);
        except Exception as e:
           inkex.utils.debug(f"Unable to parse object to json: {e}");
        if hasattr(object, '__dict__'):
           for thing in vars(object):
            inkex.utils.debug(thing);
            self.printObject(thing);

if __name__ == '__main__':
    AdjustToCenterLineExtension().run()
