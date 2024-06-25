import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from shapely import Point, LineString, LinearRing, Polygon
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry


def make_patch(polygon: Polygon, **kwargs) -> PathPatch:
    def get_path_codes(ring: LinearRing):
        path_codes_ = [Path.LINETO for _ in ring.coords]
        path_codes_[0] = Path.MOVETO
        return path_codes_

    vertices = list(polygon.exterior.coords)
    codes = get_path_codes(polygon.exterior)

    for int_ring in polygon.interiors:
        vertices += list(int_ring.coords)
        codes += get_path_codes(int_ring)

    path = Path(vertices, codes)
    return PathPatch(path, **kwargs)


class GeomPlotter:
    def __init__(self, **kwargs):
        if not kwargs:
            kwargs = {"figsize": (10, 10), "facecolor": "w"}
        self.fig = plt.figure(**kwargs)
        self.ax = self.fig.gca()
        self.ax.axis('off')
        self.ax.set_aspect("equal")

    def add_geom(self, geom, **kwargs) -> None:
        add_plot(geom, self.ax, **kwargs)
        self.ax.axis("scaled")

    def show(self) -> None:
        self.fig.show()


def add_plot(geom: BaseGeometry, ax, fill: bool = None, **kwargs) -> None:
    if not isinstance(geom, BaseGeometry):
        raise TypeError(f"{type(geom)=}")

    # Recursive call for Multipart geometries
    if isinstance(geom, BaseMultipartGeometry):
        for subgeom in geom.geoms:
            add_plot(subgeom, ax, **kwargs, fill=fill)
        return None

    # 0. Empty Geometry
    if geom.is_empty:
        return None

    # 1. Point
    elif isinstance(geom, Point):
        ax.scatter(geom.x, geom.y, **kwargs)
        return None

    # 2. Polygon
    elif isinstance(geom, Polygon):
        if "c" in kwargs:
            kwargs["color"] = kwargs.pop("c")
        if fill is None:
            fill = True
        patch = make_patch(geom, fill=fill, **kwargs)
        ax.add_patch(patch)
        return None

    # 3. LineString
    elif isinstance(geom, LineString):
        xy = geom.xy

        if fill is None:
            fill = False

        if fill:
            method = ax.fill
        else:
            method = ax.plot

        method(*xy, **kwargs)
        return None

    else:
        raise TypeError(f"{type(geom)=}")
