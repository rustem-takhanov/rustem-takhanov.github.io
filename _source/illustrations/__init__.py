"""Deterministic, original SVG illustrations for publication detail pages."""
from . import geometry, kernels, constraints, language, learning


def build_illustrations():
    figures = {}
    for module in (geometry, kernels, constraints, language, learning):
        group = module.build_figures()
        overlap = figures.keys() & group.keys()
        if overlap:
            raise ValueError(f'Duplicate paper illustrations: {overlap}')
        figures.update(group)
    return figures
