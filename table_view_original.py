"""
Table View Module for OpTrack Dashboard
Renders breakdown and ready tables with pagination
"""
import streamlit as st
import pandas as pd

def render_unit_table(df, get_unit_icon_html_func, section_type="breakdown", page_key="table_page"):
    """
    Render unit table with pagination for both breakdown and ready sections
    
    Args:
        df: DataFrame with unit data
        get_unit_icon_html_func: Function to get unit icon HTML
        section_type: 'breakdown' or 'ready' - affects styling
        page_key: Session state key for pagination
    """
    
    # CSS for the table
    css = """
    <style>
    .unit-table-wrapper {
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E5E7EB;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .table-controls {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        padding: 12px 16px;
        border-bottom: 1px solid #E5E7EB;
    }
    .ctrl-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        background: #FFF;
        border: 1px solid #E5E7EB;
        color: #374151;
        cursor: pointer;
    }
    .ctrl-btn:hover { background: #F9FAFB; }
    .table-body-wrapper {
        flex: 1;
        overflow-y: auto;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    .data-table th {
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        color: #6B7280;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: #F9FAFB;
        border-bottom: 1px solid #E5E7EB;
    }
    .data-table td {
        padding: 14px 16px;
        color: #374151;
        font-size: 14px;
        border-bottom: 1px solid #F3F4F6;
        vertical-align: middle;
    }
    .data-table tr:hover { background: #F9FAFB; }
    .unit-info-cell {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .unit-img-box {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .unit-img-box img { width: 36px; height: 36px; object-fit: contain; }
    .unit-code { font-weight: 600; color: #111827; font-size: 14px; }
    .loc-stack { display: flex; flex-direction: column; gap: 3px; }
    .loc-main { font-weight: 500; color: #111827; font-size: 14px; display: flex; align-items: center; gap: 6px; }
    .loc-sub { color: #6B7280; font-size: 12px; display: flex; align-items: center; gap: 5px; }
    .time-stack { display: flex; flex-direction: column; gap: 2px; }
    .duration-val { font-weight: 700; font-size: 14px; }
    .duration-val.open-dur { color: #EF4444; }
    .duration-val.ready-dur { color: #10B981; }
    .time-sub { color: #6B7280; font-size: 12px; }
    .note-badge {
        display: inline-block;
        padding: 5px 10px;
        background: #FEF9C3;
        color: #854D0E;
        border: 1px solid #FDE68A;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .status-pill {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .status-pill.open-status { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
    .status-pill.ready-status { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
    .table-pagination {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background: #FAFAFA;
        border-top: 1px solid #E5E7EB;
        font-size: 13px;
        color: #6B7280;
    }
    .empty-msg {
        text-align: center;
        padding: 40px;
        color: #9CA3AF;
        font-size: 14px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown(f'<div class="unit-table-wrapper"><div class="empty-msg">No {section_type} units</div></div>', unsafe_allow_html=True)
        return
    
    # Sort and paginate
    df = df.sort_values('start_date', ascending=False).reset_index(drop=True)
    rows_per_page = 7
    total = len(df)
    total_pages = max(1, (total + rows_per_page - 1) // rows_per_page)
    
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    page = max(1, min(st.session_state[page_key], total_pages))
    start_i = (page - 1) * rows_per_page
    end_i = min(start_i + rows_per_page, total)
    page_data = df.iloc[start_i:end_i]
    
    # Icons
    pin_icon = '<svg viewBox="0 0 24 24" fill="#EF4444" width="12" height="12"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'
    wrench_icon = '<svg viewBox="0 0 24 24" fill="#F59E0B" width="11" height="11"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>'
    filter_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>'
    sort_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="4" y1="6" x2="16" y2="6"/><line x1="4" y1="12" x2="12" y2="12"/><line x1="4" y1="18" x2="8" y2="18"/></svg>'
    
    # Build rows
    rows_html = ""
    for _, r in page_data.iterrows():
        icon = get_unit_icon_html_func(r['unit_code'], 36)
        pit = str(r.get('pit', '-'))
        evt = str(r.get('event_type', '-'))[:18] + ('...' if len(str(r.get('event_type', ''))) > 18 else '')
        status = r.get('current_status', 'Open')
        
        # Duration
        if status == 'Open' and pd.notna(r.get('start_date')):
            iso = r['start_date'].strftime('%Y-%m-%dT%H:%M:%S')
            dur = f'<span class="duration-val open-dur live-duration" data-start="{iso}">calculating...</span>'
        else:
            h = f"{r['total_duration_hours']:.1f}h" if pd.notna(r.get('total_duration_hours')) else '0h'
            dur = f'<span class="duration-val ready-dur">{h}</span>'
        
        start_dt = r['start_date'].strftime('%d %b %H:%M') if pd.notna(r.get('start_date')) else '-'
        
        # Note
        note = str(r.get('noted', '')) if pd.notna(r.get('noted')) else ''
        note_html = f'<span class="note-badge" title="{note}">{note[:15]}{"..." if len(note) > 15 else ""}</span>' if note.strip() else '<span style="color:#9CA3AF">-</span>'
        
        # Status
        st_class = 'ready-status' if status == 'Ready' else 'open-status'
        
        rows_html += f'''<tr>
            <td><div class="unit-info-cell"><div class="unit-img-box">{icon}</div><span class="unit-code">{r['unit_code']}</span></div></td>
            <td><div class="loc-stack"><div class="loc-main">{pin_icon} {pit}</div><div class="loc-sub">{wrench_icon} {evt}</div></div></td>
            <td><div class="time-stack">{dur}<span class="time-sub">{start_dt}</span></div></td>
            <td>{note_html}</td>
            <td><span class="status-pill {st_class}">{status.upper()}</span></td>
        </tr>'''
    
    # Pagination buttons - small and inline with showing text
    prev_disabled = 'disabled' if page <= 1 else ''
    next_disabled = 'disabled' if page >= total_pages else ''
    
    # Full HTML with inline pagination
    html = f'''<div class="unit-table-wrapper">
        <div class="table-controls">
            <span class="ctrl-btn">{filter_icon} Filter</span>
            <span class="ctrl-btn">{sort_icon} Sort</span>
        </div>
        <div class="table-body-wrapper">
            <table class="data-table">
                <thead><tr>
                    <th>Unit Info</th>
                    <th>Location &amp; Type</th>
                    <th>Time</th>
                    <th>Keterangan</th>
                    <th>Status</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        <div class="table-pagination">
            <span style="font-size:12px;color:#6B7280;">Showing {start_i+1} to {end_i} of {total} results</span>
            <div style="display:flex;gap:6px;">
                <span class="page-info" style="font-size:11px;color:#9CA3AF;padding:4px 8px;">Page {page}/{total_pages}</span>
            </div>
        </div>
    </div>'''
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Small Streamlit pagination buttons inline
    cols = st.columns([6, 1, 1])
    with cols[1]:
        if st.button("ΓåÉ Prev", key=f"{page_key}_p", disabled=(page <= 1)):
            st.session_state[page_key] = page - 1
            st.rerun()
    with cols[2]:
        if st.button("Next ΓåÆ", key=f"{page_key}_n", disabled=(page >= total_pages)):
            st.session_state[page_key] = page + 1
            st.rerun()


# Alias functions for backward compatibility
def render_breakdown_table(df, get_unit_icon_html_func, page_key="breakdown_page"):
    """Render breakdown table"""
    render_unit_table(df, get_unit_icon_html_func, "breakdown", page_key)

def render_ready_table(df, get_unit_icon_html_func, page_key="ready_page"):
    """Render ready table"""
    render_unit_table(df, get_unit_icon_html_func, "ready", page_key)
