"""
Demo/Test Script for Hover Card Functionality
Run this to verify the hover card implementation
"""

# Hover Card View Features Demo

## What Was Implemented

### 1. **Hover-to-Reveal Detail Cards**
- Pure CSS hover interaction (no server roundtrip)
- Smooth slide-in animation (0.2s ease-out)
- Positioned absolutely to the right of each unit row
- 380px wide detail card with shadow and border

### 2. **Unit Row Design**
- Clean white cards with icons, unit ID, location, time
- Hover effect: blue border, shadow, slight translation
- Live duration counter for Open breakdowns
- Status badge and duration display

### 3. **Detail Card Content**

#### Header (Blue Gradient)
- Unit ID in bold
- Event/Issue type

#### Body Sections

**Info Grid** (2x2)
- Location
- Duration  
- Start time
- Status

**Breakdown History Bar Chart** (CSS-based)
- "This Week" breakdown count
- "This Month" breakdown count  
- "Last 3 Months" breakdown count
- Animated horizontal bars with gradient fill
- Count displayed on bars

**Action Items List**
- Up to 3 action items
- Yellow-bordered cards with alert icons
- Displays notes or default actions

## How to Test

1. **Navigate to Overview Page**
   - Open the dashboard
   - Go to the "Overview" tab

2. **Hover Over Units**
   - Move your mouse over any unit in the "Current Breakdown" section
   - Detail card should appear instantly on the right
   - Card should show unit details, history chart, and actions

3. **Test Multiple Units**
   - Hover over different units
   - Each should show its own data
   - Cards should appear/disappear smoothly

4. **Check Interactions**
   - Live duration should update every second for Open units
   - Bar chart should show different values per unit
   - Actions should reflect notes or defaults

## CSS Classes Reference

- `.unit-row` - Main container (position: relative)
- `.hover-detail` - The popup card (position: absolute, hidden by default)
- `.unit-row:hover .hover-detail` - Reveals card on hover
- `.history-chart` - CSS bar chart container
- `.bar-fill` - Animated gradient bars
- `.action-item` - Action list items with icons

## Files Modified

1. **Created**: `hover_card_view.py` (491 lines)
   - Main rendering function with CSS and HTML generation
   
2. **Modified**: `dashboard.py`
   - Added import: `from hover_card_view import render_hover_breakdown_list`
   - Replaced: `render_breakdown_table()` with `render_hover_breakdown_list()`
   - Line 1252: Now calls the hover card renderer

## Key Features

✅ **No Server Roundtrip** - Pure CSS hover (instant)
✅ **CSS Bar Chart** - No Plotly dependencies
✅ **Smooth Animation** - SlideIn effect
✅ **Responsive Data** - Shows real breakdowns
✅ **Live Updates** - Duration counters work
✅ **Action Items** - Displays notes or defaults
✅ **Clean Design** - Modern gradient header, organized layout

## Expected Behavior

When hovering over a unit row in the "Current Breakdown" section:
1. Row highlights (blue border, shadow)
2. Detail card slides in from the right
3. Card stays visible while hovering
4. Card hides when mouse moves away
5. No page reload or lag

## Troubleshooting

If cards don't appear:
- Check browser console for errors
- Verify `hover_card_view.py` is in the same directory
- Ensure Streamlit restarted after code changes
- Try hard refresh (Ctrl+Shift+R)

If positioning is off:
- Check if parent containers have conflicting CSS
- Verify `.unit-row` has `position: relative`
- Adjust `margin-left` on `.hover-detail` if needed
