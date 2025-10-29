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

class LineInfo:
    parentElement = None;
    subPathId = None;
    path: None;
    startNodeId: None;
    endNodeId: None;
    startNode = None;
    endNode = None;
    def to_dict(self):
        return {
            "parentElement": self.parentElement.get_id(),
            "subPathId": self.subPathId,
            "path": self.path.__class__.__name__,
            "startNodeId": self.startNodeId,
            "endNodeId": self.endNodeId,
            "startNode": f"({self.startNode.x}, {self.startNode.y})",
            "endNode": f"({self.endNode.x}, {self.endNode.y})"
        };


"""Changes the length of a line"""
class LineLengthExtension(inkex.EffectExtension):
    def __init__(self):
        inkex.Effect.__init__(self);
    
    def add_arguments(self, pars):
        pars.add_argument("--line_length", type=float, default=0.0);
        pars.add_argument("--tab", type=str, default="stroke");
    
    def effect(self):
        inkex.utils.debug(f"Selected nodes: {str(self.options.selected_nodes)}");
        selected_nodes = self.getSelectedElementsWithNodes();
        for selectedLineInfo in selected_nodes.values():
            #inkex.utils.debug(f"Selected node before processing: {json.dumps(selectedLineInfo.to_dict())}");
            self.adjustLine(selectedLineInfo);
            #inkex.utils.debug(f"Selected node after processing: {json.dumps(selectedLineInfo.to_dict())}");
        
    
    def adjustLine(self, lineInfo):
        a = lineInfo.startNode;
        b = lineInfo.endNode;
        #startNodeObj = lineInfo.path[lineInfo.startNodeId];
        endNodeObject = lineInfo.path[lineInfo.endNodeId];
        slope = inkex.transforms.Vector2d(b.x - a.x, b.y - a.y);
        currentLineLengthString = str(self.options.line_length);
        newLineLength = inkex.units.convert_unit(currentLineLengthString + "mm", "px");
        newB = self.findEndPoint(a, slope, newLineLength);
        inkex.utils.debug("line length in pixels: " + str(newLineLength));
        inkex.utils.debug("line length in mm: " + currentLineLengthString);
        inkex.utils.debug("slope: " + str(slope));
        inkex.utils.debug("new end point: " + str(newB));

        newEndPoint = None;
        match endNodeObject.letter:
            case "M":
                newEndPoint = inkex.paths.lines.Move(newB.x, newB.y);
            case "L":
                newEndPoint = inkex.paths.lines.Line(newB.x, newB.y);
        
        lineInfo.path[lineInfo.endNodeId] = newEndPoint;
        #firstPath.close();

        #This is wrong.  We need to set the correct sub path, if there is one. 
        lineInfo.parentElement.path = lineInfo.path;
        lineInfo.endNode = newB;
    
    def getSelectedElementsWithNodes(self):
        selected_nodes = {};
        for path in self.options.selected_nodes:
            sel_data = path.rsplit(':', 2)
            path_id = sel_data[0]
            sub_path = int(sel_data[1])
            sel_node = int(sel_data[2])
            nodeParentElement = self.svg.selection[path_id];
            parentProperty = nodeParentElement if sub_path == 0 else nodeParentElement.break_apart()[sub_path];
            controlPoints = list(parentProperty.path.control_points);
            actualNode = controlPoints[sel_node];
            if path_id not in selected_nodes or selected_nodes[path_id].subPathId != sub_path:
                newLineInfo = LineInfo();
                newLineInfo.parentElement = nodeParentElement;
                newLineInfo.startNode = actualNode;
                newLineInfo.subPathId = sub_path;
                newLineInfo.path = parentProperty.path;
                newLineInfo.startNodeId = sel_node;
                selected_nodes[path_id] = newLineInfo;
            else:
                if selected_nodes[path_id].endNode is not None:
                    raise Exception("Cannot modify a line with more than two points selected.");
                else:
                    selected_nodes[path_id].endNode = actualNode;
                    selected_nodes[path_id].endNodeId = sel_node;
        return selected_nodes;

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
    
    def findEndPoint(self, start, slope, distance):
        self.normalizeVector(slope);
        newEndpoint = (distance * slope) + start;
        return newEndpoint;

    def normalizeVector(self, vector):
        magnitude = math.sqrt(vector.x ** 2 + vector.y ** 2);
        vector.x = vector.x / magnitude;
        vector.y = vector.y / magnitude;

if __name__ == '__main__':
    LineLengthExtension().run()
