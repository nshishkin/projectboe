# Hexagonal Grid System Documentation

## Overview
The tactical combat system in Brothers of Eador uses a hexagonal grid system with axial coordinates to represent the battlefield. This provides more natural movement and positioning compared to square grids. The hexagons use a flat-topped orientation for a more horizontal layout.

## Coordinate System
The system uses axial coordinates (q, r) where:
- q represents the column axis (horizontal-like)
- r represents the row axis (diagonal)
- The coordinate system is oriented flat-topped for horizontal layout

## Key Components

### HexTile Class
Represents a single hexagonal tile with:
- Axial coordinates (q, r)
- Terrain type (plain, hills, woods, swamp, water)
- Elevation value
- Pixel coordinates for rendering
- Vertices for drawing the hexagon

### HexGrid Class
Manages the entire hexagonal grid with:
- Grid dimensions (default 20x10 - 20 hexes wide, 10 hexes high)
- Hex size parameter
- Methods for coordinate conversion (flat-topped orientation with flat sides on top/bottom)
- Neighbor calculation
- Rendering functionality

### TacticalMap Class
High-level interface for the tactical map:
- Wraps the HexGrid functionality
- Handles map rendering
- Provides access to individual hexes
- Manages terrain randomization

## Coordinate Conversions
- Axial to Pixel: Converts axial coordinates to screen coordinates for rendering using flat-topped orientation
- Cube to Pixel: Used internally for precise coordinate calculations

## Neighbors
Each hex has 6 potential neighbors in flat-topped orientation:
- (+1, 0): Right
- (0, +1): Bottom-right
- (-1, +1): Bottom-left
- (-1, 0): Left
- (0, -1): Top-left
- (+1, -1): Top-right

## Terrain Types
- Plain: Basic terrain with no special modifiers
- Hills: Provides defensive bonuses
- Woods: Provides cover bonuses
- Swamp: Reduces movement speed
- Water: May be impassable or have special movement rules

## Rendering
Each hex is rendered as a polygon with:
- Color based on terrain type
- Black border for visibility
- Optional coordinate labels for debugging