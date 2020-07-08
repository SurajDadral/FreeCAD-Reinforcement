# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "Reinforcement Drawing Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from xml.etree import ElementTree

import FreeCAD
import Part
import Draft
import DraftGeomUtils
import DraftVecUtils
import WorkingPlane

from SVGfunc import (
    getSVGRootElement,
    getPointSVG,
    isPointInSVG,
    getLineSVG,
    isLineInSVG,
    getSVGTextElement,
    getSVGPathElement,
    getArrowMarkerElement,
)
from .config import SVG_POINT_DIA_FACTOR


def getRebarsSpanAxis(rebar):
    """getRebarsSpanAxis(Rebar):
    Returns span axis of rebars.
    """
    if (
        Draft.getType(rebar.Base) == "Wire"
    ):  # Draft Wires can have "wrong" placement
        axis = DraftGeomUtils.getNormal(rebar.Base.Shape)
    else:
        axis = rebar.Base.Placement.Rotation.multVec(FreeCAD.Vector(0, 0, -1))
    if hasattr(rebar, "Direction"):
        if not DraftVecUtils.isNull(rebar.Direction):
            axis = FreeCAD.Vector(rebar.Direction)
            axis.normalize()
    return axis


def getViewPlane(view):
    """getViewPlane(View):
    Returns view_plane corresponding to view, where view can be "Front", "Rear",
    "Left", "Right", "Top" or "Bottom".
    """
    if view == "Front":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, -1, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(1, 0, 0)
    elif view == "Rear":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, 1, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(-1, 0, 0)
    elif view == "Left":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(-1, 0, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(0, -1, 0)
    elif view == "Right":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(1, 0, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(0, 1, 0)
    elif view == "Top":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, 0, 1)
        view_plane.v = FreeCAD.Vector(0, -1, 0)
        view_plane.u = FreeCAD.Vector(1, 0, 0)
    elif view == "Bottom":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, 0, -1)
        view_plane.v = FreeCAD.Vector(0, 1, 0)
        view_plane.u = FreeCAD.Vector(1, 0, 0)
    else:
        FreeCAD.Console.PrintError(
            'Invalid/Unsupported view. Valid views are: "Front", "Rear", '
            '"Left", "Right" "Top" and "Bottom".\n'
        )
        return None
    return view_plane


def getProjectionToSVGPlane(vec, plane):
    """getProjectionToSVGPlane(Vector, Plane):
    Returns projection of vector on plane.
    """
    nx = DraftVecUtils.project(vec, plane.u)
    lx = nx.Length
    if abs(nx.getAngle(plane.u)) > 0.1:
        lx = -lx
    ny = DraftVecUtils.project(vec, plane.v)
    ly = ny.Length
    if abs(ny.getAngle(plane.v)) > 0.1:
        ly = -ly
    return FreeCAD.Vector(lx, ly, 0)


def getLineDimensionsData(
    p1, p2, dimension_text, h_dim_x, h_dim_y, v_dim_x, v_dim_y
):
    dimension = ElementTree.Element("g")
    if abs(p2.y - p1.y) < abs(p2.x - p1.x):
        dimension_line_horizontal = False
        x_cord = v_dim_x
        y_cord = (x_cord - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
        dimension_line = getSVGPathElement(
            "M{} {} V{}".format(x_cord, y_cord, v_dim_y),
            "url(#start_arrow)",
            "stroke:#000000",
        )
        dimension_label = getSVGTextElement(
            dimension_text, v_dim_x, v_dim_y, "DejaVu Sans", "10px", "middle"
        )
        dimension.append(dimension_line)
        dimension.append(dimension_label)
    else:
        dimension_line_horizontal = True
        y_cord = h_dim_y
        x_cord = (y_cord - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
        dimension_line = getSVGPathElement(
            "M{} {} H{}".format(x_cord, y_cord, h_dim_x),
            "url(#start_arrow)",
            "stroke:#000000",
        )
        dimension_label = getSVGTextElement(
            dimension_text,
            h_dim_x,
            h_dim_y,
            "DejaVu Sans",
            "10px",
            dominant_baseline="central",
        )
        dimension.append(dimension_line)
        dimension.append(dimension_label)
    return {
        "svg": dimension,
        "dimension_line_horizontal": dimension_line_horizontal,
    }


def getRoundCornerSVG(edge, radius, view_plane):
    """getRoundCornerSVG(Edge, Radius, ViewPlane):
    Returns round corner edge svg with given radius.
    """
    p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
    p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
    t1 = edge.tangentAt(edge.FirstParameter)
    t2 = edge.tangentAt(
        edge.FirstParameter + (edge.LastParameter - edge.FirstParameter) / 10
    )
    flag_sweep = int(DraftVecUtils.angle(t1, t2, view_plane.axis) < 0)
    svg = ElementTree.Element("path")
    svg.set("style", "stroke:#000000;fill:none")
    svg.set(
        "d",
        "M{x1} {y1} A{radius} {radius} 0 0 {flag_sweep} {x2} {y2}".format(
            x1=round(p1.x),
            y1=round(p1.y),
            x2=round(p2.x),
            y2=round(p2.y),
            radius=round(radius),
            flag_sweep=flag_sweep,
        ),
    )
    return svg


def isRoundCornerInSVG(edge, radius, view_plane, svg):
    """isRoundCornerInSVG(Edge, Radius, ViewPlane. SVG):
    Returns True if svg corresponding to round corner edge is present in SVG
    element, False otherwise.
    """
    p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
    p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
    t1 = edge.tangentAt(edge.FirstParameter)
    t2 = edge.tangentAt(
        edge.FirstParameter + (edge.LastParameter - edge.FirstParameter) / 10
    )
    flag_sweep = int(DraftVecUtils.angle(t1, t2, view_plane.axis) < 0)
    if (
        svg.find(
            './/path[@d="M{x1} {y1} A{radius} {radius} 0 0 {flag_sweep} {x2} '
            '{y2}"]'.format(
                x1=round(p1.x),
                y1=round(p1.y),
                x2=round(p2.x),
                y2=round(p2.y),
                radius=round(radius),
                flag_sweep=flag_sweep,
            )
        )
        is not None
    ):
        return True
    elif (
        svg.find(
            './/path[@d="M{x1} {y1} A{radius} {radius} 0 0 {flag_sweep} {x2} '
            '{y2}"]'.format(
                x1=round(p2.x),
                y1=round(p2.y),
                x2=round(p1.x),
                y2=round(p1.y),
                radius=round(radius),
                flag_sweep=not flag_sweep,
            )
        )
        is not None
    ):
        return True
    else:
        return False


def getStirrupSVGPoints(stirrup_wire, stirrup_alignment, view_plane):
    """getStirrupSVGPoints(StirrupWire, StirrupAlignment, ViewPlane):
    stirrup_alignment can be "V" for vertical, horizontal otherwise.
    Returns points corresponding to line representation of stirrup in
    view_plane.
    """
    first_point = getProjectionToSVGPlane(
        stirrup_wire.Vertexes[0].Point, view_plane
    )
    min_x = first_point.x
    min_y = first_point.y
    max_x = first_point.x
    max_y = first_point.y
    for vertex in stirrup_wire.Vertexes[1:]:
        point = getProjectionToSVGPlane(vertex.Point, view_plane)
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)
    if stirrup_alignment == "V":
        x_cord = (min_x + max_x) / 2
        return (
            FreeCAD.Vector(x_cord, min_y, 0),
            FreeCAD.Vector(x_cord, max_y, 0),
        )
    else:
        y_cord = (min_y + max_y) / 2
        return (
            FreeCAD.Vector(min_x, y_cord, 0),
            FreeCAD.Vector(max_x, y_cord, 0),
        )


def getStirrupSVGData(
    rebar, view_plane, rebars_svg,
):
    """getStirrupSVGData(StirrupRebar, ViewPlane, RebarsSVG):
    Returns dictionary containing stirrup svg data.
    Returned dictionary format:
    {
        "svg": stirrup_svg,
        "visibility": is_rebar_visible,
    }
    """
    stirrup_svg = ElementTree.Element("g", attrib={"id": str(rebar.Name)})
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    stirrup_span_axis = getRebarsSpanAxis(rebar)
    if round(drawing_plane_normal.cross(stirrup_span_axis).Length) == 0:
        edges = Part.__sortEdges__(
            DraftGeomUtils.filletWire(
                rebar.Base.Shape.Wires[0],
                rebar.Rounding * rebar.Diameter.Value,
            ).Edges
        )
        for edge in edges:
            if DraftGeomUtils.geomType(edge) == "Line":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                edge_svg = getLineSVG(p1, p2)
                if is_rebar_visible or not isLineInSVG(p1, p2, rebars_svg):
                    stirrup_svg.append(edge_svg)
                    is_rebar_visible = True
            elif DraftGeomUtils.geomType(edge) == "Circle":
                edge_svg = getRoundCornerSVG(
                    edge, rebar.Rounding * rebar.Diameter.Value, view_plane,
                )
                if is_rebar_visible or not isRoundCornerInSVG(
                    edge,
                    rebar.Rounding * rebar.Diameter.Value,
                    view_plane,
                    rebars_svg,
                ):
                    stirrup_svg.append(edge_svg)
                    is_rebar_visible = True

    else:
        if round(stirrup_span_axis.cross(view_plane.u).Length) == 0:
            stirrup_alignment = "V"
        else:
            stirrup_alignment = "H"
        basewire = DraftGeomUtils.filletWire(
            rebar.Base.Shape.Wires[0], rebar.Rounding * rebar.Diameter.Value
        )
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)
            p1, p2 = getStirrupSVGPoints(wire, stirrup_alignment, view_plane)
            rebar_svg = getLineSVG(p1, p2)
            if not isLineInSVG(p1, p2, rebars_svg):
                is_rebar_visible = True
            if is_rebar_visible:
                stirrup_svg.append(rebar_svg)
    return {
        "svg": stirrup_svg,
        "visibility": is_rebar_visible,
    }


def getUShapeRebarSVGData(
    rebar, view_plane, rebars_svg,
):
    """getUShapeRebarSVGData(UShapeRebar, ViewPlane, RebarsSVG):
    Returns dictionary containing UShape rebar svg data.
    Returned dictionary format:
    {
        "svg": u_rebar_svg,
        "visibility": is_rebar_visible,
    }
    """
    u_rebar_svg = ElementTree.Element("g", attrib={"id": str(rebar.Name)})
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    if round(drawing_plane_normal.cross(getRebarsSpanAxis(rebar)).Length) == 0:
        edges = Part.__sortEdges__(
            DraftGeomUtils.filletWire(
                rebar.Base.Shape.Wires[0],
                rebar.Rounding * rebar.Diameter.Value,
            ).Edges
        )
        for edge in edges:
            if DraftGeomUtils.geomType(edge) == "Line":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                    edge_svg = getPointSVG(
                        p1, radius=SVG_POINT_DIA_FACTOR * rebar.Diameter.Value
                    )
                else:
                    edge_svg = getLineSVG(p1, p2)
                    if not isLineInSVG(p1, p2, rebars_svg):
                        is_rebar_visible = True
                if is_rebar_visible:
                    u_rebar_svg.append(edge_svg)
                    is_rebar_visible = True
            elif DraftGeomUtils.geomType(edge) == "Circle":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                if round(p1.x) == round(p2.x) or round(p1.y) == round(p2.y):
                    edge_svg = getLineSVG(p1, p2)
                    if not isLineInSVG(p1, p2, rebars_svg):
                        is_rebar_visible = True
                else:
                    edge_svg = getRoundCornerSVG(
                        edge, rebar.Rounding * rebar.Diameter.Value, view_plane,
                    )
                    if not isRoundCornerInSVG(
                        edge,
                        rebar.Rounding * rebar.Diameter.Value,
                        view_plane,
                        rebars_svg,
                    ):
                        is_rebar_visible = True
                if is_rebar_visible:
                    u_rebar_svg.append(edge_svg)
    else:
        basewire = rebar.Base.Shape.Wires[0]
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)

            edges = Part.__sortEdges__(
                DraftGeomUtils.filletWire(
                    wire, rebar.Rounding * rebar.Diameter.Value,
                ).Edges
            )
            for edge in edges:
                if DraftGeomUtils.geomType(edge) == "Line":
                    p1 = getProjectionToSVGPlane(
                        edge.Vertexes[0].Point, view_plane
                    )
                    p2 = getProjectionToSVGPlane(
                        edge.Vertexes[1].Point, view_plane
                    )
                    if round(p1.x) == round(p2.x) and round(p1.y) == round(
                        p2.y
                    ):
                        edge_svg = getPointSVG(
                            p1,
                            radius=SVG_POINT_DIA_FACTOR * rebar.Diameter.Value,
                        )
                    else:
                        edge_svg = getLineSVG(p1, p2)
                        if not isLineInSVG(p1, p2, rebars_svg):
                            is_rebar_visible = True
                    if is_rebar_visible or not isLineInSVG(p1, p2, rebars_svg):
                        u_rebar_svg.append(edge_svg)
                        is_rebar_visible = True
                elif DraftGeomUtils.geomType(edge) == "Circle":
                    p1 = getProjectionToSVGPlane(
                        edge.Vertexes[0].Point, view_plane
                    )
                    p2 = getProjectionToSVGPlane(
                        edge.Vertexes[1].Point, view_plane
                    )
                    if round(p1.x) == round(p2.x) or round(p1.y) == round(p2.y):
                        edge_svg = getLineSVG(p1, p2)
                        if not isLineInSVG(p1, p2, rebars_svg):
                            is_rebar_visible = True
                    else:
                        edge_svg = getRoundCornerSVG(
                            edge,
                            rebar.Rounding * rebar.Diameter.Value,
                            view_plane,
                        )
                        if not isRoundCornerInSVG(
                            edge,
                            rebar.Rounding * rebar.Diameter.Value,
                            view_plane,
                            rebars_svg,
                        ):
                            is_rebar_visible = True
                    if is_rebar_visible:
                        u_rebar_svg.append(edge_svg)
    return {
        "svg": u_rebar_svg,
        "visibility": is_rebar_visible,
    }


def getStraightRebarSVGData(
    rebar,
    view_plane,
    h_dim_x_offset,
    h_dim_y_offset,
    v_dim_x_offset,
    v_dim_y_offset,
    rebars_svg,
):
    """getStraightRebarSVGData(StraightRebar, ViewPlane, RebarsSVG):
    Returns dictionary containing straight rebar svg data.
    Returned dictionary format:
    {
        "svg": straight_rebar_svg,
        "visibility": is_rebar_visible,
    }
    """
    straight_rebar_svg = ElementTree.Element(
        "g", attrib={"id": str(rebar.Name)}
    )
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    if round(drawing_plane_normal.cross(getRebarsSpanAxis(rebar)).Length) == 0:
        p1 = getProjectionToSVGPlane(
            rebar.Base.Shape.Wires[0].Vertexes[0].Point, view_plane
        )
        p2 = getProjectionToSVGPlane(
            rebar.Base.Shape.Wires[0].Vertexes[1].Point, view_plane
        )
        if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
            rebar_svg = getPointSVG(
                p1, radius=SVG_POINT_DIA_FACTOR * rebar.Diameter.Value
            )
            if not isPointInSVG(p1, rebars_svg):
                is_rebar_visible = True
        else:
            rebar_svg = getLineSVG(p1, p2)
            if not isLineInSVG(p1, p2, rebars_svg):
                is_rebar_visible = True
        if is_rebar_visible:
            straight_rebar_svg.append(rebar_svg)
            dimension_data = getLineDimensionsData(
                p1,
                p2,
                "{}⌀{}".format(rebar.Amount, rebar.Diameter),
                h_dim_x_offset,
                h_dim_y_offset,
                v_dim_x_offset,
                v_dim_y_offset,
            )
            straight_rebar_svg.append(dimension_data["svg"])
            if dimension_data["dimension_line_horizontal"]:
                # Add logic calculate increment
                h_dim_y_offset += 100
            else:
                v_dim_x_offset += 100
    else:
        basewire = rebar.Base.Shape.Wires[0]
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)
            p1 = getProjectionToSVGPlane(wire.Vertexes[0].Point, view_plane)
            p2 = getProjectionToSVGPlane(wire.Vertexes[1].Point, view_plane)
            if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                rebar_svg = getPointSVG(
                    p1, radius=SVG_POINT_DIA_FACTOR * rebar.Diameter.Value
                )
                if not (
                    isPointInSVG(p1, rebars_svg)
                    or isPointInSVG(p1, straight_rebar_svg)
                ):
                    is_rebar_visible = True
            else:
                rebar_svg = getLineSVG(p1, p2)
                if not (
                    isLineInSVG(p1, p2, rebars_svg)
                    or isLineInSVG(p1, p2, straight_rebar_svg)
                ):
                    is_rebar_visible = True
            if is_rebar_visible:
                straight_rebar_svg.append(rebar_svg)
    return {
        "svg": straight_rebar_svg,
        "visibility": is_rebar_visible,
        "h_dim_y_offset": h_dim_y_offset,
        "v_dim_x_offset": v_dim_x_offset,
    }


def getReinforcementDrawingSVG(structure, rebars_list, view_direction):
    """getReinforcementDrawingSVG(Structure, RebarsList, ViewDirection):
    Generates Reinforcement Drawing View.

    view_direction is FreeCAD.Vector() or WorkingPlane.plane() corresponding to
    direction of view point.

    Returns svg content for reinforcement drawing.
    """
    if isinstance(view_direction, FreeCAD.Vector):
        if view_direction != FreeCAD.Vector(0, 0, 0):
            view_plane = WorkingPlane.plane()
            view_plane.alignToPointAndAxis(
                FreeCAD.Vector(0, 0, 0),
                view_direction.negative().negative(),
                0,
            )
    elif isinstance(view_direction, WorkingPlane.plane):
        view_plane = view_direction

    if view_plane.axis == FreeCAD.Vector(0, -1, 0):
        pts = [0, 1, 4, 5]
    elif view_plane.axis == FreeCAD.Vector(0, 1, 0):
        pts = [2, 3, 6, 7]
    elif view_plane.axis == FreeCAD.Vector(0, 0, 1):
        pts = [0, 1, 2, 3]
    elif view_plane.axis == FreeCAD.Vector(0, 0, -1):
        pts = [4, 5, 6, 7]
    elif view_plane.axis == FreeCAD.Vector(1, 0, 0):
        pts = [1, 2, 5, 6]
    else:
        pts = [0, 3, 4, 7]

    bounding_box = Part.Compound(
        [rebar.Shape for rebar in rebars_list] + [structure.Shape]
    ).BoundBox
    point = getProjectionToSVGPlane(bounding_box.getPoint(pts[0]), view_plane)
    min_x = point.x
    min_y = point.y
    max_x = point.x
    max_y = point.y
    for pt in pts[1:]:
        point = getProjectionToSVGPlane(bounding_box.getPoint(pt), view_plane)
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)

    svg = getSVGRootElement()
    defs_element = ElementTree.Element("defs")
    defs_element.append(getArrowMarkerElement("start_arrow", "start"))
    defs_element.append(getArrowMarkerElement("end_arrow", "end"))
    svg.append(defs_element)

    reinforcement_drawing = ElementTree.Element(
        "g", attrib={"id": "reinforcement_drawing"}
    )
    svg.append(reinforcement_drawing)

    # Filter rebars created using Reinforcement Workbench
    stirrups = []
    bent_rebars = []
    u_rebars = []
    l_rebars = []
    straight_rebars = []
    helical_rebars = []
    custom_rebars = []
    for rebar in rebars_list:
        if rebar.RebarShape == "Stirrup":
            stirrups.append(rebar)
        elif rebar.RebarShape == "BentShapeRebar":
            bent_rebars.append(rebar)
        elif rebar.RebarShape == "UShapeRebar":
            u_rebars.append(rebar)
        elif rebar.RebarShape == "LShapeRebar":
            l_rebars.append(rebar)
        elif rebar.RebarShape == "StraightRebar":
            straight_rebars.append(rebar)
        elif rebar.RebarShape == "HelicalRebar":
            helical_rebars.append(rebar)
        else:
            custom_rebars.append(rebar)

    rebars_svg = ElementTree.Element("g", attrib={"id": "Rebars"})
    reinforcement_drawing.append(rebars_svg)

    visible_rebars = []
    stirrups_svg = ElementTree.Element("g", attrib={"id": "Stirrup"})
    rebars_svg.append(stirrups_svg)
    for rebar in stirrups:
        rebar_data = getStirrupSVGData(rebar, view_plane, rebars_svg)
        if rebar_data["visibility"]:
            stirrups_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    bent_rebars_svg = ElementTree.Element("g", attrib={"id": "BentShapeRebar"})
    rebars_svg.append(bent_rebars_svg)
    for rebar in bent_rebars:
        rebar_data = getUShapeRebarSVGData(rebar, view_plane, rebars_svg)
        if rebar_data["visibility"]:
            bent_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    u_rebars_svg = ElementTree.Element("g", attrib={"id": "UShapeRebar"})
    rebars_svg.append(u_rebars_svg)
    for rebar in u_rebars:
        rebar_data = getUShapeRebarSVGData(rebar, view_plane, rebars_svg)
        if rebar_data["visibility"]:
            u_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    l_rebars_svg = ElementTree.Element("g", attrib={"id": "LShapeRebar"})
    rebars_svg.append(l_rebars_svg)
    for rebar in l_rebars:
        rebar_data = getUShapeRebarSVGData(rebar, view_plane, rebars_svg)
        if rebar_data["visibility"]:
            l_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    straight_rebars_svg = ElementTree.Element(
        "g", attrib={"id": "StraightRebar"}
    )
    rebars_svg.append(straight_rebars_svg)

    h_dim_x_offset = max_x + 50
    h_dim_y_offset = min_y + 50
    v_dim_x_offset = min_x + 50
    v_dim_y_offset = min_y - 50
    for rebar in straight_rebars:
        rebar_data = getStraightRebarSVGData(
            rebar,
            view_plane,
            h_dim_x_offset,
            h_dim_y_offset,
            v_dim_x_offset,
            v_dim_y_offset,
            rebars_svg,
        )
        if rebar_data["visibility"]:
            straight_rebars_svg.append(rebar_data["svg"])
            h_dim_y_offset = rebar_data["h_dim_y_offset"]
            v_dim_x_offset = rebar_data["v_dim_x_offset"]
            visible_rebars.append(rebar)

    helical_rebars_svg = ElementTree.Element("g", attrib={"id": "HelicalRebar"})
    rebars_svg.append(helical_rebars_svg)

    # SVG is generated for all helical rebars, because all helical rebars in
    # circular column are assumed to be visible, not overlapped by any other
    # rebar type (it makes sense for me). Please create an issue on github
    # repository if you think its wrong assumption
    for rebar in helical_rebars:
        helical_rebars_svg.append(
            ElementTree.fromstring(
                Draft.getSVG(rebar, direction=view_plane, fillstyle="none")
            )
        )
        visible_rebars.append(rebar)

    custom_rebars_svg = ElementTree.Element("g", attrib={"id": "CustomRebar"})
    rebars_svg.append(custom_rebars_svg)
    for rebar in custom_rebars:
        custom_rebars_svg.append(
            ElementTree.fromstring(
                Draft.getSVG(rebar, direction=view_plane, fillstyle="none")
            )
        )

    # Create Structure SVG
    structure_svg = ElementTree.fromstring(
        '<g id="structure">'
        + Draft.getSVG(structure, direction=view_plane, fillstyle="none")
        + "</g>"
    )
    reinforcement_drawing.append(structure_svg)
    reinforcement_drawing.set(
        "transform",
        "translate({}, {})".format(round(-min_x + 60), round(-min_y + 100)),
    )

    svg_width = round(max_x - min_x + 200)
    svg_height = round(max_y - min_y + 200)

    svg.set("width", str(svg_width) + "mm")
    svg.set("height", str(svg_height) + "mm")
    svg.set("viewBox", "0 0 {} {}".format(svg_width, svg_height))

    return svg