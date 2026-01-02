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
    
    /* CLICK DETAIL CARD - Modal Style */
    .data-table tbody tr {
        position: relative;
        cursor: pointer;
    }
    
    .hover-detail-card {
        position: fixed;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 650px;
        max-height: 80vh;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        display: none;
        overflow: hidden;
    }
    
    /* Show card when active class is added */
    .hover-detail-card.active {
        display: block;
        animation: detailFadeIn 0.2s ease-out;
    }
    
    @keyframes detailFadeIn {
        from {
            opacity: 0;
            transform: translate(-50%, -48%);
        }
        to {
            opacity: 1;
            transform: translate(-50%, -50%);
        }
    }
    
    .detail-modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9998;
        display: none;
    }
    
    .detail-modal-backdrop.active {
        display: block;
    }
    
    .hover-detail-header {
        padding: 20px 24px;
        border-bottom: 1px solid #E5E7EB;
        background: #FFFFFF;
        position: relative;
    }
    
    .detail-close-btn {
        position: absolute;
        top: 16px;
        right: 16px;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        background: #F3F4F6;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: #6B7280;
        transition: all 0.2s ease;
    }
    
    .detail-close-btn:hover {
        background: #E5E7EB;
        color: #374151;
    }
    
    .hover-detail-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
        padding-right: 120px;
    }
    
    .hover-detail-subtitle {
        font-size: 14px;
        color: #6B7280;
    }
    
    .hover-detail-body {
        padding: 24px;
        max-height: calc(80vh - 100px);
        overflow-y: auto;
        display: flex;
        gap: 24px;
    }
    
    .hover-left-col {
        flex: 0 0 200px;
    }
    
    .hover-right-col {
        flex: 1;
    }
    
    .hover-unit-photo {
        width: 200px;
        height: 150px;
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 16px;
    }
    
    .hover-unit-photo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .hover-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        background: #F9FAFB;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    
    .hover-info-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .hover-info-label {
        font-size: 11px;
        color: #6B7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .hover-info-value {
        font-size: 14px;
        color: #111827;
        font-weight: 600;
    }
    
    .hover-section {
        margin-bottom: 16px;
    }
    
    .hover-section-label {
        font-size: 12px;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 10px;
    }
    
    .hover-history-chart {
        display: flex;
        gap: 12px;
        align-items: flex-end;
        height: 100px;
        padding: 12px;
        background: #F9FAFB;
        border-radius: 8px;
        margin-top: 8px;
    }
    
    .hover-bar-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }
    
    .hover-bar-track {
        width: 100%;
        height: 70px;
        background: #E5E7EB;
        border-radius: 6px 6px 0 0;
        display: flex;
        align-items: flex-end;
    }
    
    .hover-bar-fill {
        width: 100%;
        background: linear-gradient(180deg, #60A5FA, #3B82F6);
        border-radius: 6px 6px 0 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 12px;
        transition: height 0.3s ease;
    }
    
    .hover-bar-label {
        font-size: 10px;
        color: #6B7280;
        font-weight: 500;
        text-align: center;
    }
    
    .hover-action-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .hover-action-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 10px 12px;
        background: #FEF9C3;
        border-radius: 6px;
        border-left: 3px solid #F59E0B;
    }
    
    .hover-action-text {
        font-size: 13px;
        color: #374151;
        line-height: 1.5;
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
    for idx, r in page_data.iterrows():
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
        
        # === BUILD HOVER CARD HTML ===
        # Get larger icon for popup
        icon_large = get_unit_icon_html_func(r['unit_code'], 160)
        
        # Calculate duration hours for popup
        if status == 'Open' and pd.notna(r.get('start_date')):
            from datetime import datetime
            import pytz
            now = datetime.now(pytz.timezone('Asia/Makassar'))
            start = r['start_date']
            if start.tzinfo is None:
                start = pytz.timezone('Asia/Makassar').localize(start)
            diff_hours = (now - start).total_seconds() / 3600
        else:
            diff_hours = r.get('total_duration_hours', 0) if pd.notna(r.get('total_duration_hours')) else 0
        
        # History bars (mockup shows 4 weeks)
        history_bars = [
            {"label": "Minggu 1", "count": 1, "height": 25},
            {"label": "Minggu 2", "count": 0, "height": 0},
            {"label": "Minggu 3", "count": 1, "height": 25},
            {"label": "Minggu 4", "count": 1, "height": 25}
        ]
        
        chart_html = ""
        for bar in history_bars:
            chart_html += f'''<div class="hover-bar-col">
                <div class="hover-bar-track">
                    <div class="hover-bar-fill" style="height:{bar['height']}px">{bar['count'] if bar['count'] > 0 else ''}</div>
                </div>
                <div class="hover-bar-label">{bar['label']}</div>
            </div>'''
        
        # Actions from notes
        actions = []
        if note.strip():
            for line in note.split('\n')[:3]:
                if line.strip():
                    actions.append(line.strip())
        if not actions:
            actions = ["Ban Baru (x1)", "Alat Tambal", "Montir."]
        
        action_html = ""
        for action in actions:
            action_html += f'<div class="hover-action-item"><div class="hover-action-text">{action}</div></div>'
        
        # Build full hover card HTML with unique ID
        card_id = f"detail-card-{idx}"
        backdrop_id = f"backdrop-{idx}"
        hover_card = f'''<div class="detail-modal-backdrop" id="{backdrop_id}"></div>
        <div class="hover-detail-card" id="{card_id}">
            <div class="hover-detail-header">
                <div class="hover-detail-title">{r['unit_code']} - {evt}</div>
                <div class="hover-detail-subtitle">{pit}</div>
                <button class="detail-close-btn" onclick="closeDetail('{card_id}', '{backdrop_id}')" title="Close">✕</button>
            </div>
            <div class="hover-detail-body">
                <div class="hover-left-col">
                    <div class="hover-unit-photo">{icon_large}</div>
                    <div class="hover-section">
                        <div class="hover-section-label">Riwayat 30 Hari Terakhir (Total: 3)</div>
                        <div class="hover-history-chart">{chart_html}</div>
                    </div>
                </div>
                <div class="hover-right-col">
                    <div class="hover-section">
                        <div class="hover-section-label">Current Breakdown</div>
                        <div style="font-size:14px;color:#374151;margin-bottom:12px;"><strong>{evt}</strong> ({start_dt})<br>Unscheduled Maintenance<br>Durasi: {diff_hours:.0f}h {int((diff_hours % 1) * 60)}m.</div>
                    </div>
                    <div class="hover-section">
                        <div class="hover-section-label">History</div>
                        <div style="font-size:13px;color:#374151;">Riwayat 30 Hari Terakhir (Total: 3):<br>3x {evt}</div>
                    </div>
                    <div class="hover-section">
                        <div class="hover-section-label">Kebutuhan</div>
                        <div style="font-size:13px;color:#374151;margin-bottom:8px;"><strong>Kebutuhan & Ilustrasi:</strong></div>
                        <div class="hover-action-list">{action_html}</div>
                    </div>
                    <div class="hover-section">
                        <div style="font-size:13px;color:#374151;margin-bottom:8px;"><strong>Penjabaran:</strong> Kebocoran parah pada ban belakang kanan, membutuhkan penggantian ban dan pemeriksaan velg oleh teknisi.</div>
                    </div>
                </div>
            </div>
        </div>'''
        
        rows_html += f'''<tr onclick="showDetail('{card_id}', '{backdrop_id}')" style="cursor:pointer;">
            <td style="position:relative;">
                <div class="unit-info-cell"><div class="unit-img-box">{icon}</div><span class="unit-code">{r['unit_code']}</span></div>
                {hover_card}
            </td>
            <td><div class="loc-stack"><div class="loc-main">{pin_icon} {pit}</div><div class="loc-sub">{wrench_icon} {evt}</div></div></td>
            <td><div class="time-stack">{dur}<span class="time-sub">{start_dt}</span></div></td>
            <td>{note_html}</td>
            <td><span class="status-pill {st_class}">{status.upper()}</span></td>
        </tr>'''
    
    # Pagination buttons - small and inline with showing text
    prev_disabled = 'disabled' if page <= 1 else ''
    next_disabled = 'disabled' if page >= total_pages else ''
    
    # Full HTML with inline pagination and JavaScript
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
    </div>
    <script>
    function showDetail(cardId, backdropId) {{
        event.stopPropagation();
        document.getElementById(cardId).classList.add('active');
        document.getElementById(backdropId).classList.add('active');
    }}
    
    function closeDetail(cardId, backdropId) {{
        event.stopPropagation();
        document.getElementById(cardId).classList.remove('active');
        document.getElementById(backdropId).classList.remove('active');
    }}
    
    // Click outside to close
    document.addEventListener('click', function(e) {{
        if (e.target.classList.contains('detail-modal-backdrop') && e.target.classList.contains('active')) {{
            const backdropId = e.target.id;
            const cardId = backdropId.replace('backdrop-', 'detail-card-');
            closeDetail(cardId, backdropId);
        }}
    }});
    </script>'''
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Small Streamlit pagination buttons inline
    cols = st.columns([6, 1, 1])
    with cols[1]:
        if st.button("◀ Prev", key=f"{page_key}_p", disabled=(page <= 1)):
            st.session_state[page_key] = page - 1
            st.rerun()
    with cols[2]:
        if st.button("Next ▶", key=f"{page_key}_n", disabled=(page >= total_pages)):
            st.session_state[page_key] = page + 1
            st.rerun()


# Alias functions for backward compatibility
def render_breakdown_table(df, get_unit_icon_html_func, page_key="breakdown_page"):
    """Render breakdown table"""
    render_unit_table(df, get_unit_icon_html_func, "breakdown", page_key)

def render_ready_table(df, get_unit_icon_html_func, page_key="ready_page"):
    """Render ready table"""
    render_unit_table(df, get_unit_icon_html_func, "ready", page_key)
