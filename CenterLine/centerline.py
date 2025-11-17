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
class CenterLineExtension(inkex.EffectExtension):
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
        centerLineBoundingBox = centerLine.bounding_box();

        for selected in self.svg.selected.values():
            inkex.utils.debug(f"Selected object: {selected.get_id()}");
            selectedBoundingBox = selected.bounding_box();
            self.printObjectPosition(selected);
            
            if(self.options.center_line_type == "1"): #horizontal center line
                # Align to center of center line bounding box
                newY = centerLineBoundingBox.center_y + (centerLineBoundingBox.height - selectedBoundingBox.height) / 2;
                transformY = selectedBoundingBox.center_y - newY;
                selected.path.translate(0, transformY, True);
                selected.set('y', str(newY));
                inkex.utils.debug(f"Moved object '{selected.get_id()}' vertically by {transformY}.");
            elif(self.options.center_line_type == "2"): #vertical center line
                # Align to top of center line bounding box
                newX = centerLineBoundingBox.center_x + (centerLineBoundingBox.width - selectedBoundingBox.width) / 2;
                transformX = selectedBoundingBox.center_x - newX;
                selected.path.translate(transformX, 0, True);
                selected.set('x', str(newX));
                inkex.utils.debug(f"Moved object '{selected.get_id()}' horizontally by {transformX}.");
    
            self.printObjectPosition(selected);
    
    
    
    def printObjectPosition(self, object):
        try:
            boundingBox = object.bounding_box();
            inkex.utils.debug(f"Object '{object.get_id()}' position and size: {boundingBox.center_x}, {boundingBox.center_y}, {boundingBox.width}, {boundingBox.height}");
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
    CenterLineExtension().run()
